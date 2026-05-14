import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_llm(prompt: str) -> str:
    model = os.getenv("OPENAI_MODEL")

    response = client.responses.create(
        model=model,
        input=prompt
    )

    return response.output_text