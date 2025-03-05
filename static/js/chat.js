$(document).ready(function() {
    // Initialize the to-do list with placeholders
    updateTodoList([]);

    // Fetch the initial response from the server
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: '' }) // Empty message to trigger initial prompt
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
        //Message empty check 
        if (message.trim() === "") {
            alert("Message cannot be empty");
            return;
        }
        $.ajax({
            url: '/chat',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: message }),
            success: function(response) {
                if (response.error) {
                    alert(response.error);
                } else if (response.todo_list) {
                    $('#messages').append('<div>To-Do List:</div>');
                    response.todo_list.forEach(function(task) {
                        $('#messages').append('<div>' + task.task + '</div>');
                    });
                } else {
                    $('#messages').append('<div>' + response.response + '</div>');
                }
                $('#message-input').val('');
            },
            error: function(xhr, status, error) {
                alert("An error occurred: " + error);
            }
        });
    });

    $('#message-input').keypress(function(e) {
        if (e.which == 13) { // Enter key pressed
            $('#send-button').click();
        }
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
        console.log('API response:', data); // Debugging log
        if (data.todo_list) {
            updateTodoList(data.todo_list);
        } else if (data.response) {
            addMessage('ai', data.response);
        } else if (data.error) {
            addMessage('error', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error); // Debugging log
        addMessage('error', 'An error occurred while communicating with the server.');
    });
    if (!isInitial) document.getElementById('message-input').value = '';
}

function addMessage(sender, message) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.innerHTML = message;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
}

function updateTodoList(todoList) {
    const todoListElement = document.getElementById('todo-list');
    todoListElement.innerHTML = '';
    todoList.forEach(item => {
        const li = document.createElement('li');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = item.completed;
        li.appendChild(checkbox);
        li.innerHTML += item.task;
        todoListElement.appendChild(li);
    });

    // Add placeholder checklists
    for (let i = 1; i <= 3; i++) {
        const li = document.createElement('li');
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        li.appendChild(checkbox);
        li.innerHTML += `SmartTaskAI ${i}`;
        todoListElement.appendChild(li);
    }
}
