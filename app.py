from flask import Flask, request, jsonify, render_template
from config import model, MODEL_NAME
import time
import logging
import uuid
from datetime import datetime
from collections import defaultdict, deque
from todolist import generate_todo_list, render_bold_text
from flask_socketio import SocketIO, emit
import asyncio
from google import genai
import re  # Add this import statement
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
model_id = "gemini-2.0-flash-exp"
config = {
    "response_modalities": ["TEXT"],
    "max_tokens": 150  # Ensure the model is configured to generate longer responses
}

app = Flask(__name__)
socketio = SocketIO(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('watchdog.observers.inotify_buffer').setLevel(logging.WARNING)

def load_prompts(filepath):
    prompts = {}
    with open(filepath, 'r') as file:
        content = file.read()
        for section in content.split('\n\n'):
            if ' = ' in section:
                key, value = section.split(' = ', 1)
                prompts[key.strip()] = value.strip().strip('"""')
            else:
                app.logger.warning(f"Skipping invalid section: {section}")
    return prompts

# Define a placeholder validate_request_signature decorator
def validate_request_signature(f):
    def decorated_function(*args, **kwargs):
        # TODO: Implement request signature validation logic
        return f(*args, **kwargs)
    return decorated_function

prompts = load_prompts('/workspaces/SmartTaskAI/config/prompts.txt')
initial_prompt = prompts['initial_prompt']
dynamic_context_prompt = prompts['dynamic_context_prompt']

# --- Rate Limiting ---
MAX_REQUESTS_PER_MINUTE = 10
TIME_WINDOW = 60
RATE_LIMITS = defaultdict(deque)

class RateLimitError(Exception):
    pass

def check_rate_limit(ip):
    current_time = time.time()
    RATE_LIMITS[ip] = deque([t for t in RATE_LIMITS[ip] if current_time - t < TIME_WINDOW])
    if len(RATE_LIMITS[ip]) >= MAX_REQUESTS_PER_MINUTE:
        time_to_wait = TIME_WINDOW - (current_time - RATE_LIMITS[ip][0])
        raise RateLimitError(f"Rate limit exceeded. Please wait {time_to_wait:.2f} seconds.")
    RATE_LIMITS[ip].append(current_time)

# Server-side to-do list state
todo_list = {
    "version": 0,
    "items": []
}

def validate_change(change):
    # TODO: Implement validation logic
    return True

def broadcast_update():
    socketio.emit('list_update', todo_list)

def resolve_conflict(client_version, server_version):
    # TODO: Implement version-based merge
    pass

class ListOperationDetector:
    LIST_TRIGGERS = {
        'add': r'(add|remember|create).+ (to )?the? list',
        'remove': r'(remove|delete|drop).+ (from )?the? list',
        'modify': r'(edit|update|change|toggle).+ item',
        'query': r'(show|what).+ (list|tasks)'
    }

    @staticmethod
    def detect_operation(user_input):
        for operation, pattern in ListOperationDetector.LIST_TRIGGERS.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                return operation
        return None

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
        app.logger.debug("Sending initial prompt to Gemini API")
        response = asyncio.run(generate_gemini_response(initial_prompt + dynamic_context_prompt))
        response_text = render_bold_text(response)
        app.logger.debug(f"Generated initial response: {response_text}")
        return jsonify({'initial_response': response_text})
    return render_template('index.html')

@app.route('/index')
def show_index():
    return render_template('index.html')

@app.route('/todolist')
def show_todolist():
    return render_template('todolist.html')

# Add a flag to track if it's the first message
first_message = True

async def generate_gemini_response(prompt):
    try:
        async with client.aio.live.connect(model=model_id, config=config) as session:
            await session.send(input=prompt, end_of_turn=True)
            async for response in session.receive():
                if response.text is not None:
                    app.logger.debug(f"Received response from Gemini: {response.text}")
                    return response.text
    except Exception as e:
        app.logger.error(f"Error generating Gemini response: {str(e)}")
    return ""

# Update the chat endpoint to use the Gemini model
@app.route('/chat', methods=['POST'])
def chat(): 
    global first_message, todo_list
    user_input = request.json.get('message')
    ip = request.remote_addr
    app.logger.debug(f"Received user input: {user_input}")
    
    if first_message:
        first_message = False
        response_text = asyncio.run(generate_gemini_response(initial_prompt + dynamic_context_prompt))
        response_text = render_bold_text(response_text)
        app.logger.debug(f"Generated initial response: {response_text}")
        return jsonify({'response': response_text, 'user_message': user_input})
  
    try:
        check_rate_limit(ip)
        
        operation = ListOperationDetector.detect_operation(user_input)
        if operation:
            response_text = asyncio.run(generate_gemini_response(user_input))
            response_text = render_bold_text(response_text)
            app.logger.debug(f"Generated response: {response_text}")
            
            # Update the server-side to-do list based on the operation
            if operation == 'add':
                new_task = {
                    "id": str(uuid.uuid4()),
                    "content": response_text,
                    "status": "incomplete",
                    "priority": 0,
                    "created": datetime.now().isoformat(),
                    "modified": datetime.now().isoformat(),
                    "metadata": {}
                }
                todo_list["items"].append(new_task)
                todo_list["version"] += 1
                broadcast_update()
            elif operation == 'remove':
                # TODO: Implement remove logic
                pass
            elif operation == 'modify':
                # TODO: Implement modify logic
                pass
            elif operation == 'query':
                return jsonify({'response': todo_list, 'user_message': user_input})
            
            return jsonify({'todo_list': todo_list, 'user_message': user_input})
        else:
            response_text = asyncio.run(generate_gemini_response(user_input))
            response_text = render_bold_text(response_text)
            app.logger.debug(f"Generated response: {response_text}")
            return jsonify({'response': response_text, 'user_message': user_input})
    except RateLimitError as e:
        app.logger.error(f"Rate limit error: {str(e)}")
        return jsonify({'error': str(e), 'user_message': user_input}), 429
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e), 'user_message': user_input}), 500

@app.route('/update_list', methods=['POST'])
@validate_request_signature
def update_list():
    global todo_list
    action = request.json.get('action')
    item = request.json.get('item')
    if action == 'add':
        new_task = {
            "id": str(uuid.uuid4()),
            "content": item,
            "status": "incomplete",
            "priority": 0,
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "metadata": {}
        }
        todo_list["items"].append(new_task)
        todo_list["version"] += 1
        prompt = f"Add '{item}' to the imaginary list."
    elif action == 'remove':
        todo_list["items"] = [task for task in todo_list["items"] if task['content'] != item]
        todo_list["version"] += 1
        prompt = f"Remove '{item}' from the imaginary list."
    model.generate_content(prompt)
    broadcast_update()
    return jsonify({'todo_list': todo_list})

@socketio.on('list_update')
def handle_update(change):
    if validate_change(change):
        resolve_conflict(change['version'], todo_list['version'])
        broadcast_update()

if __name__ == '__main__':
    socketio.run(app, debug=True)