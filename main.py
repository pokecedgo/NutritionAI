from openai import OpenAI
from dotenv import load_dotenv
import base64
import sys
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_nutrition_from_image(image_path):
    with open(image_path, "rb") as image:
        base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is the total calories, protein, and carbs in this image?",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    response_message = response.choices[0].message
    content = response_message['content']

    return content

if __name__ == "__main__":
    image_path = sys.argv[1]
    nutrition = get_nutrition_from_image(image_path)
    print(nutrition)