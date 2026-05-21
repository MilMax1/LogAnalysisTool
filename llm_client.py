import os
import time
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_llm(prompt: str) -> str:
    model = os.getenv("OPENAI_MODEL")

    max_attempts = 5
    wait_seconds = 5

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.responses.create(
                model=model,
                input=prompt,
            )

            return response.output_text

        except RateLimitError as error:
            if attempt == max_attempts:
                raise

            print(
                f"Rate limit nådd. Väntar {wait_seconds} sekunder "
                f"och försöker igen ({attempt}/{max_attempts})..."
            )
            time.sleep(wait_seconds)
            wait_seconds *= 2