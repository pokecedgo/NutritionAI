import re

def render_bold_text(text):
    return re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

def generate_todo_list(response_text):
    tasks = [task.strip() for task in response_text.split('\n') if task.strip()]
    todo_list = [{'task': render_bold_text(task), 'completed': False} for task in tasks]
    return todo_list
