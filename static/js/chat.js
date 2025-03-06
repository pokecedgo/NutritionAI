$(document).ready(function() {
    updateTodoList([]);

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: '' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            addMessage('ai', data.response);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });

    $('#send-button').click(function() {
        var message = $('#message-input').val();
        $.ajax({
            url: '/chat',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(response) {
                if (response.error) {
                    alert(response.error);
                } else if (response.todo_list) {
                    updateTodoList(response.todo_list);
                } else {
                    addMessage('ai', response.response, true);
                }
                $('#message-input').val('');
            },
            error: function(xhr, status, error) {
                alert("An error occurred: " + error);
            }
        });
    });

    $('#message-input').keypress(function(e) {
        if (e.which == 13) {
            $('#send-button').click();
        }
    });

    $('#add-task-button').click(function() {
        var newTask = $('#new-task-input').val();
        if (newTask.trim() !== "") {
            addTaskToList(newTask);
            $('#new-task-input').val('');
            updateServerList('add', newTask);
        }
    });

    $('#new-task-input').keypress(function(e) {
        if (e.which == 13) {
            $('#add-task-button').click();
        }
    });

    $(document).on('click', '.remove-task-button', function() {
        var task = $(this).siblings('span').text();
        $(this).parent().remove();
        updateServerList('remove', task);
    });
});

function sendMessage(userInput, isInitial = false) {
    if (!userInput) return;
    if (!isInitial) addMessage('user', userInput);
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        console.log('API response:', data);
        if (data.todo_list) {
            updateTodoList(data.todo_list);
        } else if (data.response) {
            addMessage('ai', data.response, true);
        } else if (data.error) {
            addMessage('error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('error', 'An error occurred while communicating with the server.');
    });
    if (!isInitial) document.getElementById('message-input').value = '';
}

function addMessage(sender, message, typewriter = false) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    if (typewriter) {
        typewriterEffect(messageDiv, message);
    } else {
        messageDiv.innerHTML = message;
    }
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function typewriterEffect(element, text) {
    let index = 0;
    const speed = 100;
    function type() {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            index++;
            setTimeout(type, speed);
        }
    }
    type();
}

function updateTodoList(todoList) {
    const todoListElement = document.getElementById('todo-list');
    todoListElement.innerHTML = '';
    todoList.items.forEach(item => {
        const li = document.createElement('li');
        li.className = `priority-${item.priority} ${item.status}`;
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = item.status === 'complete';
        li.appendChild(checkbox);
        li.innerHTML += `<span class="task-text">${item.content}</span>`;
        if (item.metadata.dueDate) {
            li.innerHTML += `<span class="due-date">📅 ${item.metadata.dueDate}</span>`;
        }
        li.innerHTML += `<button onclick="editTask('${item.id}')">✏️</button>`;
        todoListElement.appendChild(li);
    });
}

function addTaskToList(task) {
    const todoListElement = document.getElementById('todo-list');
    const li = document.createElement('li');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    li.appendChild(checkbox);
    li.innerHTML += `<span>${task}</span> <button class="remove-task-button">Remove</button>`;
    todoListElement.appendChild(li);
}

function updateServerList(action, item) {
    fetch('/update_list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, item: item })
    })
    .then(response => response.json())
    .then(data => {
        updateTodoList(data.todo_list);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function showLoading() {
    document.getElementById('loading').style.display = 'inline';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

async function sendMessage(message) {
    showLoading();
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        // Handle the response data
        console.log(data);
    } catch (error) {
        console.error('Error:', error);
    } finally {
        hideLoading();
    }
}

// Example usage
document.getElementById('send-button').addEventListener('click', () => {
    const message = document.getElementById('message-input').value;
    sendMessage(message);
});
