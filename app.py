from flask import Flask, request, jsonify, render_template
from config import client, MODEL_NAME
import time

app = Flask(__name__)

# --- Rate Limiting ---
MAX_REQUESTS_PER_MINUTE = 10
TIME_WINDOW = 60
REQUEST_HISTORY = []

class RateLimitError(Exception):
    pass

def check_rate_limit():
    global REQUEST_HISTORY
    current_time = time.time()
    REQUEST_HISTORY = [t for t in REQUEST_HISTORY if current_time - t < TIME_WINDOW]
    if len(REQUEST_HISTORY) >= MAX_REQUESTS_PER_MINUTE:
        time_to_wait = TIME_WINDOW - (current_time - REQUEST_HISTORY[0])
        raise RateLimitError(f"Rate limit exceeded. Please wait {time_to_wait:.2f} seconds.")
    REQUEST_HISTORY.append(current_time)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    try:
        check_rate_limit()
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_input
        )
        response_text = response.text
        if "list" in user_input.lower() or "plan" in user_input.lower():
            tasks = response_text.split('\n')  # Assuming each task is on a new line
            todo_list = [{'task': task, 'completed': False} for task in tasks]
            return jsonify({'todo_list': todo_list})
        else:
            return jsonify({'response': response_text})
    except RateLimitError as e:
        return jsonify({'error': str(e)}), 429
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
