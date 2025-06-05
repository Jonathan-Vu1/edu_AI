from openai import OpenAI
import os


def generate_model():

    # Initialize OpenAI client with API key from environment variable
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    if not OPENAI_API_KEY:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

    client = OpenAI(
        api_key = OPENAI_API_KEY
    )

    return client