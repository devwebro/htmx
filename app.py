from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Load todos on startup for production
load_todos_on_startup = True

# JSON file for persistent storage
DATA_FILE = 'todos.json'
CHAT_FILE = 'chat.json'

# In-memory storage for todos
todos = []
next_id = 1

# In-memory storage for chat messages
messages = []
next_message_id = 1


def load_todos():
    """Load todos from JSON file"""
    global todos, next_id
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                todos = data.get('todos', [])
                next_id = data.get('next_id', 1)
        except (json.JSONDecodeError, IOError):
            todos = []
            next_id = 1
    else:
        todos = []
        next_id = 1


def save_todos():
    """Save todos to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({'todos': todos, 'next_id': next_id}, f, indent=2)
    except IOError:
        pass


def load_messages():
    """Load chat messages from JSON file"""
    global messages, next_message_id
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, 'r') as f:
                data = json.load(f)
                messages = data.get('messages', [])
                next_message_id = data.get('next_message_id', 1)
        except (json.JSONDecodeError, IOError):
            messages = []
            next_message_id = 1
    else:
        messages = []
        next_message_id = 1


def save_messages():
    """Save chat messages to JSON file"""
    try:
        with open(CHAT_FILE, 'w') as f:
            json.dump({'messages': messages, 'next_message_id': next_message_id}, f, indent=2)
    except IOError:
        pass


# Load todos when app starts (for production)
if load_todos_on_startup:
    load_todos()
    load_messages()


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', todos=todos)


@app.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos"""
    return render_template('todos.html', todos=todos)


@app.route('/todos', methods=['POST'])
def add_todo():
    """Add a new todo"""
    global next_id
    title = request.form.get('title')
    
    if title:
        todo = {
            'id': next_id,
            'title': title,
            'completed': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        todos.append(todo)
        next_id += 1
        save_todos()
        
    return render_template('todos.html', todos=todos)


@app.route('/todos/<int:todo_id>/toggle', methods=['POST'])
def toggle_todo(todo_id):
    """Toggle todo completion status"""
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = not todo['completed']
            break
    
    save_todos()
    return render_template('todos.html', todos=todos)


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    
    save_todos()
    return render_template('todos.html', todos=todos)


@app.route('/chat')
def chat():
    """Render the chat page"""
    return render_template('chat.html', messages=messages)


@app.route('/chat/messages', methods=['GET'])
def get_messages():
    """Get all chat messages"""
    return render_template('chat_messages.html', messages=messages)


@app.route('/chat/messages', methods=['POST'])
def send_message():
    """Send a new chat message"""
    global next_message_id
    username = request.form.get('username', 'Anonymous')
    message = request.form.get('message')
    
    if message:
        msg = {
            'id': next_message_id,
            'username': username,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        messages.append(msg)
        next_message_id += 1
        save_messages()
        
    return render_template('chat_messages.html', messages=messages)


if __name__ == '__main__':
    load_todos()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
