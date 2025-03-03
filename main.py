import sys
import time
import PIL.Image
from config import MODEL
from PIL import UnidentifiedImageError

# --- Rate Limiting ---
MAX_REQUESTS_PER_MINUTE = 10  # Adjust based on observed rate limits.  Start conservatively.
TIME_WINDOW = 60  # Seconds in a minute
REQUEST_HISTORY = [] # Store timestamps of requests
last_request_time = 0

# --- Error Handling ---
class RateLimitError(Exception):
    pass

def check_rate_limit():
    """
    Checks if the rate limit has been exceeded.  Raises RateLimitError if it has.
    """
    global REQUEST_HISTORY
    current_time = time.time()

# --- Error Handling ---
class RateLimitError(Exception):
    pass

# --- Rate Limiting ---
def check_rate_limit():
    """
    Checks if the rate limit has been exceeded.  Raises RateLimitError if it has.
    """
    global REQUEST_HISTORY
    current_time = time.time()

    # Remove requests older than the time window
    REQUEST_HISTORY = [t for t in REQUEST_HISTORY if current_time - t < TIME_WINDOW]

    if len(REQUEST_HISTORY) >= MAX_REQUESTS_PER_MINUTE:
        time_to_wait = TIME_WINDOW - (current_time - REQUEST_HISTORY[0])
        raise RateLimitError(f"Rate limit exceeded.  Please wait {time_to_wait:.2f} seconds.")

    REQUEST_HISTORY.append(current_time)

def get_nutrition(image_path, prompt_text="If that image is a food, what is the general (Calories, Protei, Carbs) nutrition information?"):
    """
    Generates a description of an image using the Gemini Pro Vision API, with rate limiting.

    Args:
        image_path: The path to the image file.
        prompt_text:  The prompt to guide the image description.

    Returns:
        A string containing the generated description, or None if an error occurred.
    """
    global last_request_time

    try:
        # 1. Load the Image
        with open(image_path, "rb") as image_file:
            img = PIL.Image.open(image_file)
            img.load()

        # 2. Construct the Prompt (including the image)
        contents = [prompt_text, img]

        # 3. Rate Limit Check
        check_rate_limit()

        # 4. Call the Gemini API
        response = MODEL.generate_content(contents)
        response.resolve()

        # 5. Handle the Response
        return response.text

    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except RateLimitError as e:
        print(f"RateLimitError: {e}")
        return None
    except PIL.UnidentifiedImageError:
        print(f"Error: Cannot identify image file at {image_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # More informative error message
        return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    description = get_nutrition(image_path)

    if description:
        print("Image Description:")
        print(description)
    else:
        print("Failed to generate image description.")