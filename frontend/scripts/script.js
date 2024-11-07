const apiUrl = "http://localhost:8000/tasks";

document.getElementById("task-title").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.querySelector(".task-input button").click();
    }
});

document.getElementById("task-desc").addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.querySelector(".task-input button").click();
    }
});

async function fetchTasks() {
    try {
        const response = await fetch(apiUrl);
        const tasks = await response.json();
        if (!tasks.length) {
            const taskList = document.getElementById("task-list");
            taskList.innerHTML = "No tasks found";
            return;
        }
        const taskList = document.getElementById("task-list");
        taskList.innerHTML = "";
        tasks.forEach(task => {
            const li = document.createElement("li");
            li.innerHTML = `
                <span>${task.title} - ${task.description} (${task.completed ? "Completed" : "Pending"})</span>
                <button onclick="updateTask(${task.id})">Toggle Status</button>
                <button onclick="deleteTask(${task.id})">Delete</button>
            `;
            taskList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching tasks:", error);
    }
}

async function addTask() {
    const title = document.getElementById("task-title").value;
    const description = document.getElementById("task-desc").value;
    if (!title) {
        alert("Task title is required");
        return;
    }

    try {
        await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
                "Access-Control-Allow-Methods":"POST,PATCH,OPTIONS"
            },
            body: JSON.stringify({ title, description })
        });
        document.getElementById("task-title").value = "";
        document.getElementById("task-desc").value = "";
        fetchTasks();
    } catch (error) {
        console.error("Error adding task:", error);
    }
}

async function updateTask(taskId) {
    try {
        const response = await fetch(`${apiUrl}/${taskId}`);
        const task = await response.json();
        await fetch(`${apiUrl}/${taskId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin":"*",
                "Access-Control-Allow-Methods":"POST,PATCH,OPTIONS"
            },
            body: JSON.stringify({ completed: !task.completed })
        });
        fetchTasks();
    } catch (error) {
        console.error("Error updating task:", error);
    }
}

async function deleteTask(taskId) {
    try {
        await fetch(`${apiUrl}/${taskId}`, {
            method: "DELETE"
        });
        fetchTasks();
    } catch (error) {
        console.error("Error deleting task:", error);
    }
}

document.addEventListener("DOMContentLoaded", fetchTasks);
