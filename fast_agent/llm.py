from smolagents.models import OpenAIServerModel
import os

llm = OpenAIServerModel(
                    model_id=os.environ.get("OPENAI_MODEL"),
                    api_key=os.environ.get("OPENAI_API_KEY"),
                    api_base=os.environ.get("OPENAI_BASE_URL")
                )


