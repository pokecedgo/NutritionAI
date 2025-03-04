import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.0-flash"


def initialize_model(client, model_name):
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Test initialization"
        )
        return response
    except ValueError as e:
        raise ValueError(f"Invalid model name '{model_name}': {e}")

MODEL = initialize_model(client, MODEL_NAME)
