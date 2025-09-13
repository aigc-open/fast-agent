from smolagents import CodeAgent,ToolCallingAgent
from smolagents import OpenAIServerModel
from smolagents import (
    CodeAgent,
    LiteLLMModel,
    DuckDuckGoSearchTool
)
from smolagents import tool
import os

def run(workspace: str = "./workspace"):
    os.makedirs(workspace, exist_ok=True)
    try:
        # load environment variables from .env file (requires `python-dotenv`)
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    from fast_agent.tools import tools_list
    from fast_agent.ui import GradioUI
    from fast_agent.llm import llm
    agent = ToolCallingAgent(tools=tools_list, model=llm, stream_outputs=False)
    agent.max_steps = 10
    GradioUI(agent, reset_agent_memory=False, 
             name="Fast Agent", 
             description="快速实现AI智能体",
             tools=tools_list).launch(share=False)

if __name__ == "__main__":
    from fire import Fire
    Fire(run)