import os
import re
import shutil
from pathlib import Path
from typing import Generator

from smolagents.agent_types import AgentAudio, AgentImage, AgentText
from smolagents.agents import MultiStepAgent, PlanningStep
from smolagents.memory import ActionStep, FinalAnswerStep
from smolagents.models import ChatMessageStreamDelta, MessageRole, agglomerate_stream_deltas
from smolagents.utils import _is_package_available



def get_step_footnote_content(step_log: ActionStep | PlanningStep, step_name: str) -> str:
    """Get a footnote string for a step log with duration and token information"""
    step_footnote = f"**{step_name}**"
    if step_log.token_usage is not None:
        step_footnote += f" | Input tokens: {step_log.token_usage.input_tokens:,} | Output tokens: {step_log.token_usage.output_tokens:,}"
    step_footnote += f" | Duration: {round(float(step_log.timing.duration), 2)}s" if step_log.timing.duration else ""
    step_footnote_content = f"""<span style="color: #bbbbc2; font-size: 12px;">{step_footnote}</span> """
    return step_footnote_content


def _clean_model_output(model_output: str) -> str:
    """
    Clean up model output by removing trailing tags and extra backticks.

    Args:
        model_output (`str`): Raw model output.

    Returns:
        `str`: Cleaned model output.
    """
    if not model_output:
        return ""
    model_output = model_output.strip()
    # Remove any trailing <end_code> and extra backticks, handling multiple possible formats
    model_output = re.sub(r"```\s*<end_code>", "```", model_output)  # handles ```<end_code>
    model_output = re.sub(r"<end_code>\s*```", "```", model_output)  # handles <end_code>```
    model_output = re.sub(r"```\s*\n\s*<end_code>", "```", model_output)  # handles ```\n<end_code>
    return model_output.strip()


def _format_code_content(content: str) -> str:
    """
    Format code content as Python code block if it's not already formatted.

    Args:
        content (`str`): Code content to format.

    Returns:
        `str`: Code content formatted as a Python code block.
    """
    content = content.strip()
    # Remove existing code blocks and end_code tags
    content = re.sub(r"```.*?\n", "", content)
    content = re.sub(r"\s*<end_code>\s*", "", content)
    content = content.strip()
    # Add Python code block formatting if not already present
    if not content.startswith("```python"):
        content = f"```python\n{content}\n```"
    return content


def _process_action_step(step_log: ActionStep, skip_model_outputs: bool = False) -> Generator:
    """
    Process an [`ActionStep`] and yield appropriate Gradio ChatMessage objects.

    Args:
        step_log ([`ActionStep`]): ActionStep to process.
        skip_model_outputs (`bool`): Whether to skip model outputs.

    Yields:
        `gradio.ChatMessage`: Gradio ChatMessages representing the action step.
    """
    import gradio as gr

    # Output the step number
    step_number = f"Step {step_log.step_number}"
    if not skip_model_outputs:
        yield gr.ChatMessage(role=MessageRole.ASSISTANT, content=f"**{step_number}**", metadata={"status": "done"})

    # First yield the thought/reasoning from the LLM
    if not skip_model_outputs and getattr(step_log, "model_output", ""):
        model_output = _clean_model_output(step_log.model_output)
        yield gr.ChatMessage(role=MessageRole.ASSISTANT, content=model_output, metadata={"status": "done"})

    # For tool calls, create a parent message
    if getattr(step_log, "tool_calls", []):
        first_tool_call = step_log.tool_calls[0]
        used_code = first_tool_call.name == "python_interpreter"

        # Process arguments based on type
        args = first_tool_call.arguments
        if isinstance(args, dict):
            content = str(args.get("answer", str(args)))
        else:
            content = str(args).strip()

        # Format code content if needed
        if used_code:
            content = _format_code_content(content)

        # Create the tool call message
        parent_message_tool = gr.ChatMessage(
            role=MessageRole.ASSISTANT,
            content=content,
            metadata={
                "title": f"🛠️ Used tool {first_tool_call.name}",
                "status": "done",
            },
        )
        yield parent_message_tool

    # Display execution logs if they exist
    if getattr(step_log, "observations", "") and step_log.observations.strip():
        log_content = step_log.observations.strip()
        if log_content:
            log_content = re.sub(r"^Execution logs:\s*", "", log_content)
            # yield gr.ChatMessage(
            #     role=MessageRole.ASSISTANT,
            #     content=f"```bash\n{log_content}\n",
            #     metadata={"title": "📝 Execution Logs", "status": "done"},
            # )

    # Display any images in observations
    if getattr(step_log, "observations_images", []):
        for image in step_log.observations_images:
            path_image = AgentImage(image).to_string()
            yield gr.ChatMessage(
                role=MessageRole.ASSISTANT,
                content={"path": path_image, "mime_type": f"image/{path_image.split('.')[-1]}"},
                metadata={"title": "🖼️ Output Image", "status": "done"},
            )

    # Handle errors
    if getattr(step_log, "error", None):
        yield gr.ChatMessage(
            role=MessageRole.ASSISTANT, content=str(step_log.error), metadata={"title": "💥 Error", "status": "done"}
        )

    # Add step footnote and separator
    yield gr.ChatMessage(
        role=MessageRole.ASSISTANT,
        content=get_step_footnote_content(step_log, step_number),
        metadata={"status": "done"},
    )
    yield gr.ChatMessage(role=MessageRole.ASSISTANT, content="-----", metadata={"status": "done"})


def _process_planning_step(step_log: PlanningStep, skip_model_outputs: bool = False) -> Generator:
    """
    Process a [`PlanningStep`] and yield appropriate gradio.ChatMessage objects.

    Args:
        step_log ([`PlanningStep`]): PlanningStep to process.

    Yields:
        `gradio.ChatMessage`: Gradio ChatMessages representing the planning step.
    """
    import gradio as gr

    if not skip_model_outputs:
        yield gr.ChatMessage(role=MessageRole.ASSISTANT, content="**Planning step**", metadata={"status": "done"})
        yield gr.ChatMessage(role=MessageRole.ASSISTANT, content=step_log.plan, metadata={"status": "done"})
    yield gr.ChatMessage(
        role=MessageRole.ASSISTANT,
        content=get_step_footnote_content(step_log, "Planning step"),
        metadata={"status": "done"},
    )
    yield gr.ChatMessage(role=MessageRole.ASSISTANT, content="-----", metadata={"status": "done"})


def _process_final_answer_step(step_log: FinalAnswerStep) -> Generator:
    """
    Process a [`FinalAnswerStep`] and yield appropriate gradio.ChatMessage objects.

    Args:
        step_log ([`FinalAnswerStep`]): FinalAnswerStep to process.

    Yields:
        `gradio.ChatMessage`: Gradio ChatMessages representing the final answer.
    """
    import gradio as gr

    final_answer = step_log.output
    if isinstance(final_answer, AgentText):
        yield gr.ChatMessage(
            role=MessageRole.ASSISTANT,
            content=f"**Final answer:**\n{final_answer.to_string()}\n",
            metadata={"status": "done"},
        )
    elif isinstance(final_answer, AgentImage):
        yield gr.ChatMessage(
            role=MessageRole.ASSISTANT,
            content={"path": final_answer.to_string(), "mime_type": "image/png"},
            metadata={"status": "done"},
        )
    elif isinstance(final_answer, AgentAudio):
        yield gr.ChatMessage(
            role=MessageRole.ASSISTANT,
            content={"path": final_answer.to_string(), "mime_type": "audio/wav"},
            metadata={"status": "done"},
        )
    else:
        yield gr.ChatMessage(
            role=MessageRole.ASSISTANT, content=f"**Final answer:** {str(final_answer)}", metadata={"status": "done"}
        )


def pull_messages_from_step(step_log: ActionStep | PlanningStep | FinalAnswerStep, skip_model_outputs: bool = False):
    """Extract Gradio ChatMessage objects from agent steps with proper nesting.

    Args:
        step_log: The step log to display as gr.ChatMessage objects.
        skip_model_outputs: If True, skip the model outputs when creating the gr.ChatMessage objects:
            This is used for instance when streaming model outputs have already been displayed.
    """
    if not _is_package_available("gradio"):
        raise ModuleNotFoundError(
            "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
        )
    if isinstance(step_log, ActionStep):
        yield from _process_action_step(step_log, skip_model_outputs)
    elif isinstance(step_log, PlanningStep):
        yield from _process_planning_step(step_log, skip_model_outputs)
    elif isinstance(step_log, FinalAnswerStep):
        yield from _process_final_answer_step(step_log)
    else:
        raise ValueError(f"Unsupported step type: {type(step_log)}")


def stream_to_gradio(
    agent,
    task: str,
    task_images: list | None = None,
    reset_agent_memory: bool = False,
    additional_args: dict | None = None,
) -> Generator:
    """Runs an agent with the given task and streams the messages from the agent as gradio ChatMessages."""

    if not _is_package_available("gradio"):
        raise ModuleNotFoundError(
            "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
        )
    accumulated_events: list[ChatMessageStreamDelta] = []
    for event in agent.run(
        task, images=task_images, stream=True, reset=reset_agent_memory, additional_args=additional_args
    ):
        if isinstance(event, ActionStep | PlanningStep | FinalAnswerStep):
            for message in pull_messages_from_step(
                event,
                # If we're streaming model outputs, no need to display them twice
                skip_model_outputs=getattr(agent, "stream_outputs", False),
            ):
                yield message
            accumulated_events = []
        elif isinstance(event, ChatMessageStreamDelta):
            accumulated_events.append(event)
            text = agglomerate_stream_deltas(accumulated_events).render_as_markdown()
            yield text


class GradioUI:
    """
    Gradio interface for interacting with a [`MultiStepAgent`].

    This class provides a web interface to interact with the agent in real-time, allowing users to submit prompts, upload files, and receive responses in a chat-like format.
    It  can reset the agent's memory at the start of each interaction if desired.
    It supports file uploads, which are saved to a specified folder.
    It uses the [`gradio.Chatbot`] component to display the conversation history.
    This class requires the `gradio` extra to be installed: `smolagents[gradio]`.

    Args:
        agent ([`MultiStepAgent`]): The agent to interact with.
        file_upload_folder (`str`, *optional*): The folder where uploaded files will be saved.
            If not provided, file uploads are disabled.
        reset_agent_memory (`bool`, *optional*, defaults to `False`): Whether to reset the agent's memory at the start of each interaction.
            If `True`, the agent will not remember previous interactions.

    Raises:
        ModuleNotFoundError: If the `gradio` extra is not installed.

    Example:
        ```python
        from smolagents import CodeAgent, GradioUI, InferenceClientModel

        model = InferenceClientModel(model_id="meta-llama/Meta-Llama-3.1-8B-Instruct")
        agent = CodeAgent(tools=[], model=model)
        gradio_ui = GradioUI(agent, file_upload_folder="uploads", reset_agent_memory=True)
        gradio_ui.launch()
        ```
    """

    def __init__(self, agent: MultiStepAgent, 
                 file_upload_folder: str | None = None, 
                 reset_agent_memory: bool = False,
                 name: str | None = None,
                 description: str | None = None,
                 tools: list | None = None):
        if not _is_package_available("gradio"):
            raise ModuleNotFoundError(
                "Please install 'gradio' extra to use the GradioUI: `pip install 'smolagents[gradio]'`"
            )
        self.agent = agent
        self.file_upload_folder = Path(file_upload_folder) if file_upload_folder is not None else None
        self.reset_agent_memory = reset_agent_memory
        self.name = name or getattr(agent, "name") or "Agent interface"
        self.description = description or getattr(agent, "description", None)
        self.tools = tools or getattr(agent, "tools", [])
        if self.file_upload_folder is not None:
            if not self.file_upload_folder.exists():
                self.file_upload_folder.mkdir(parents=True, exist_ok=True)

    def interact_with_agent(self, prompt, messages, session_state):
        import gradio as gr

        # Get the agent from session state or use the template agent
        if "agent" not in session_state:
            session_state["agent"] = self.agent

        try:
            # Add user message to chat history
            user_message = gr.ChatMessage(role="user", content=prompt, metadata={"status": "done"})
            messages.append(user_message)
            yield messages

            # Stream agent response
            for msg in stream_to_gradio(
                session_state["agent"], task=prompt, reset_agent_memory=self.reset_agent_memory
            ):
                if isinstance(msg, gr.ChatMessage):
                    # Mark previous message as done and add new message
                    if messages and messages[-1].metadata.get("status") == "pending":
                        messages[-1].metadata["status"] = "done"
                    messages.append(msg)
                elif isinstance(msg, str):  # Streaming text delta
                    msg = msg.replace("<", r"\<").replace(">", r"\>")  # HTML tags seem to break Gradio Chatbot
                    if messages and messages[-1].metadata.get("status") == "pending":
                        messages[-1].content = msg
                    else:
                        messages.append(
                            gr.ChatMessage(role=MessageRole.ASSISTANT, content=msg, metadata={"status": "pending"})
                        )
                yield messages

            # Ensure final message is marked as done
            if messages and messages[-1].metadata.get("status") == "pending":
                messages[-1].metadata["status"] = "done"
            yield messages

        except Exception as e:
            error_message = gr.ChatMessage(
                role=MessageRole.ASSISTANT, 
                content=f"Error: {str(e)}", 
                metadata={"status": "done", "title": "💥 Error"}
            )
            messages.append(error_message)
            yield messages

    def upload_file(self, file, file_uploads_log, allowed_file_types=None):
        """
        Upload a file and add it to the list of uploaded files in the session state.

        The file is saved to the `self.file_upload_folder` folder.
        If the file type is not allowed, it returns a message indicating the disallowed file type.

        Args:
            file (`gradio.File`): The uploaded file.
            file_uploads_log (`list`): A list to log uploaded files.
            allowed_file_types (`list`, *optional*): List of allowed file extensions. Defaults to [".pdf", ".docx", ".txt"].
        """
        import gradio as gr

        if file is None:
            return gr.Textbox(value="No file uploaded", visible=True), file_uploads_log

        if allowed_file_types is None:
            allowed_file_types = [".pdf", ".docx", ".txt"]

        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in allowed_file_types:
            return gr.Textbox("File type disallowed", visible=True), file_uploads_log

        # Sanitize file name
        original_name = os.path.basename(file.name)
        sanitized_name = re.sub(
            r"[^\w\-.]", "_", original_name
        )  # Replace any non-alphanumeric, non-dash, or non-dot characters with underscores

        # Save the uploaded file to the specified folder
        file_path = os.path.join(self.file_upload_folder, os.path.basename(sanitized_name))
        shutil.copy(file.name, file_path)

        return gr.Textbox(f"File uploaded: {file_path}", visible=True), file_uploads_log + [file_path]



    def reset_conversation(self, session_state):
        """Reset the conversation and agent memory."""
        import gradio as gr
        
        if "agent" in session_state:
            session_state["agent"].memory.reset()
        
        return [], gr.Textbox(value="", interactive=True), gr.Button(interactive=True)

    def launch(self, share: bool = True, **kwargs):
        """
        Launch the Gradio app with the agent interface.

        Args:
            share (`bool`, defaults to `True`): Whether to share the app publicly.
            **kwargs: Additional keyword arguments to pass to the Gradio launch method.
        """
        self.create_app().launch(debug=True, share=share, **kwargs)

    def create_app(self):
        import gradio as gr

        with gr.Blocks(theme="soft", fill_height=True, css="""
            .main-header { 
                text-align: center; 
                padding: 15px 0; 
                margin-bottom: 15px; 
            }
            .chat-container { 
                height: 65vh; 
                min-height: 400px; 
            }
            .tools-panel {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-right: 15px;
                height: 65vh;
                overflow-y: auto;
            }
            .tool-item {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 10px;
                margin-bottom: 8px;
            }
            .tool-name {
                font-weight: 600;
                color: #2563eb;
                margin-bottom: 4px;
            }
            .tool-description {
                font-size: 12px;
                color: #666;
                line-height: 1.4;
            }
            .input-container { 
                padding: 15px 0; 
                gap: 10px;
            }
            .input-container .gr-column {
                gap: 8px;
            }
            /* 简化输入框样式 */
            .input-container textarea {
                border-radius: 20px !important;
                border: 1px solid #ddd !important;
                padding: 12px 16px !important;
                font-size: 14px !important;
            }
            /* 按钮样式 */
            .input-container button {
                border-radius: 8px !important;
                font-weight: 500 !important;
                margin-bottom: 4px !important;
            }
        """) as demo:
            # Add session state to store session-specific data
            session_state = gr.State({})
            file_uploads_log = gr.State([])

            # Top header
            with gr.Row(elem_classes="main-header"):
                with gr.Column():
                    gr.Markdown(
                        f"# {self.name.replace('_', ' ').capitalize()}",
                        elem_id="main-title"
                    )
                    if self.description:
                        gr.Markdown(
                            f"*{self.description}*",
                            elem_id="description"
                        )
                    else:
                        gr.Markdown(
                            "*AI Assistant with tools and multi-step reasoning*",
                            elem_id="description"
                        )

            # Main content area with tools panel and chat
            with gr.Row():
                # Left sidebar for tools
                with gr.Column(scale=1, min_width=250):
                    with gr.Group(elem_classes="tools-panel"):
                        if self.tools:
                            tools_html = f"<div class='tools-container'>🛠️ Available Tools({len(self.tools)})</div>"
                            for tool in self.tools:
                                tool_name = getattr(tool, 'name', str(tool))
                                tool_description = getattr(tool, 'description', 'No description available')
                                tools_html += f"""
                                <div class="tool-item">
                                    <div class="tool-name">{tool_name}</div>
                                    <div class="tool-description">{tool_description}</div>
                                </div>
                                """
                            gr.HTML(tools_html)
                        else:
                            gr.Markdown("*No tools available*")
                
                # Right side for chat interface
                with gr.Column(scale=3):
                    # Main chat interface - takes up most of the space
                    chatbot = gr.Chatbot(
                        type="messages",
                        avatar_images=(
                            None
                        ),
                        height=500,
                        elem_classes="chat-container",
                        latex_delimiters=[
                            {"left": "$$", "right": "$$", "display": True},
                            {"left": "$", "right": "$", "display": False},
                            {"left": r"\[", "right": r"\]", "display": True},
                            {"left": r"\(", "right": r"\)", "display": False},
                        ],
                        show_copy_button=True,
                    )

                    # Bottom input area
                    with gr.Row():
                        with gr.Column(scale=6):
                            text_input = gr.Textbox(
                                placeholder="Type your message here...",
                                container=True,
                                show_label=False,
                                lines=4,
                                max_lines=4,
                            )
                        with gr.Column(scale=1, min_width=120):
                            with gr.Row():
                                with gr.Column():
                                    submit_btn = gr.Button("Send", variant="primary")
                                    clear_btn = gr.Button("Clear", variant="secondary")

            # File upload and footer row
            with gr.Row():
                with gr.Column(scale=1):
                    # File upload if enabled
                    if self.file_upload_folder is not None:
                        upload_file = gr.File(
                            label="📎 Upload File", 
                            file_count="single",
                            file_types=[".pdf", ".docx", ".txt"],
                            scale=1
                        )
                        upload_status = gr.Textbox(
                            label="Upload Status", 
                            interactive=False, 
                            visible=False
                        )
                with gr.Column(scale=2):
                    gr.HTML(
                        "<div style='text-align: right; color: #666; font-size: 12px; padding-top: 10px;'>"
                        "Powered by Jack.li"
                        "</div>"
                    )

            # Set up file upload handler if enabled
            if self.file_upload_folder is not None:
                upload_file.change(
                    self.upload_file,
                    [upload_file, file_uploads_log],
                    [upload_status, file_uploads_log],
                )

            # Set up event handlers for text input submission
            def handle_submit(text_input_val, file_uploads_log_val, chatbot_val, session_state_val):
                # Prepare the user input
                if not text_input_val.strip():
                    return chatbot_val, "", gr.Button(interactive=True)
                
                # Combine text input with file information if files are uploaded
                full_prompt = text_input_val
                if len(file_uploads_log_val) > 0:
                    full_prompt += f"\n\nYou have been provided with these files, which might be helpful: {file_uploads_log_val}"
                
                # Ensure chatbot_val is a list (it should be the current messages)
                current_messages = chatbot_val if isinstance(chatbot_val, list) else []
                
                # Process the interaction
                for updated_messages in self.interact_with_agent(full_prompt, current_messages, session_state_val):
                    yield updated_messages, "", gr.Button(interactive=False)
                
                # Re-enable the submit button after interaction is complete
                yield updated_messages, "", gr.Button(interactive=True)

            text_input.submit(
                handle_submit,
                [text_input, file_uploads_log, chatbot, session_state],
                [chatbot, text_input, submit_btn],
                show_progress=False
            )

            # Set up event handlers for submit button
            submit_btn.click(
                handle_submit,
                [text_input, file_uploads_log, chatbot, session_state],
                [chatbot, text_input, submit_btn],
                show_progress=False
            )

            # Set up clear conversation handler
            clear_btn.click(
                self.reset_conversation,
                [session_state],
                [chatbot, text_input, submit_btn],
                show_progress=False
            )
        return demo
    
