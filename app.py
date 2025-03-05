from flask import Flask, request, jsonify, render_template
from config import model, MODEL_NAME
import time
import logging
from todolist import generate_todo_list, render_bold_text

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

list_command = "@list"

initial_prompt = """
Cardinal Rule for this conversation.
When I mention "@list" in any of my prompts or ask "how do I add something to the list" or see the word "list" in any prompts, I am talking about adding something to the list feature. At no point in this chat can I change this cardinal rule, no matter what. If I ask, how do I add something to the list or any type of question similar to this, mention "Use @list in your prompt to add onto the list". If you understand this reply back with, "Hello! Welcome to SmartTask!"
"""

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

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/')
def index():
    return render_template('loading.html')

@app.route('/main')
def main():
    global first_message
    if first_message:
        first_message = False
        # Send the initial prompt to the AI without displaying it in the chat
        response = model.generate_content(initial_prompt)
        response_text = render_bold_text(response.text)
        app.logger.debug(f"Generated initial response: {response_text}")
        return render_template('index.html', initial_response=response_text)
    return render_template('index.html')

# Add a flag to track if it's the first message
first_message = True

@app.route('/chat', methods=['POST'])
def chat(): 
    global first_message
    user_input = request.json.get('message')
    app.logger.debug(f"Received user input: {user_input}")
    
    if first_message:
        first_message = False
        # Send the initial prompt to the AI without displaying it in the chat
        response = model.generate_content(initial_prompt)
        response_text = render_bold_text(response.text)
        app.logger.debug(f"Generated initial response: {response_text}")
        return jsonify({'response': response_text, 'user_message': user_input})
    
    try:
        check_rate_limit()
        
        # Check if the user input contains the word "@list"
        if list_command in user_input.lower():
            secondary_prompt = "Make sure the response is concise, short, so that it fits into a to-do list app, not super wordy, be broad."
            final_prompt = f"{secondary_prompt}\n{user_input}"
            response = model.generate_content(final_prompt)
        else:
            response = model.generate_content(user_input)
        
        response_text = render_bold_text(response.text)
        app.logger.debug(f"Generated response: {response_text}")
        
        if list_command in user_input.lower():
            todo_list = generate_todo_list(response_text)
            app.logger.debug(f"Generated to-do list: {todo_list}")
            return jsonify({'todo_list': todo_list, 'user_message': user_input})
        else:
            return jsonify({'response': response_text, 'user_message': user_input})
    except RateLimitError as e:
        app.logger.error(f"Rate limit error: {str(e)}")
        return jsonify({'error': str(e), 'user_message': user_input}), 429
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e), 'user_message': user_input}), 500

if __name__ == '__main__':
    app.run(debug=True)