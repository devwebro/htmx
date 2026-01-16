from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# JSON file for persistent storage
DATA_FILE = 'todos.json'

# In-memory storage for todos
todos = []
next_id = 1


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


@app.route('/')
def index():
    """Render the main page"""
    load_todos()
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


if __name__ == '__main__':
    load_todos()
    app.run(debug=True, port=5000)
