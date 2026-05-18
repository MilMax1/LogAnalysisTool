import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
    input="Svara med exakt text: API-test fungerar."
)

print(response.output_text)