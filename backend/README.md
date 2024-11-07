# Backend Documentation

## Overview

This backend project is part of a _full-stack_ **to-do list** application. It is built using FastAPI, a modern, fast (high-performance), ASGI (Asynchronous Server Gateway Interface) web framework for building APIs with Python 3.6+ based on standard Python type hints.

## Core Features

### User Authentication

- **User Registration**: Users can register by providing a username and password.
- **User Login**: Users can log in to receive an access token.
- **JWT Authentication**: The API uses JWT tokens to authenticate users for subsequent requests.

### Task Management

- **Create Task**: Authenticated users can create new tasks with a title, description, and completion status.
- **Retrieve Task**: Authenticated users can retrieve tasks by their ID.
- **Update Task**: Authenticated users can update the title, description, and completion status of a task.
- **Delete Task**: Authenticated users can delete tasks by their ID.
- **List Tasks**: Authenticated users can list all tasks with a limit on the number of tasks returned.

### Caching

- **Redis Cache**: The API uses Redis to cache task data for faster retrieval.

### Data Validation and Sanitization

- **Pydantic**: Used for data validation.
- **Bleach**: Used to sanitize input data to prevent XSS attacks.

### Database Interaction

- **SQLAlchemy**: Used to interact with a PostgreSQL database.

## Endpoints

- `POST /register`: Register a new user.
- `POST /token`: Login to get an access token.
- `GET /users/me/`: Get the current authenticated user.
- `POST /tasks/`: Create a new task.
- `GET /tasks/{task_id}`: Retrieve a task by its ID.
- `PUT /tasks/{task_id}`: Update a task by its ID.
- `DELETE /tasks/{task_id}`: Delete a task by its ID.
- `GET /tasks/`: List all tasks.

## How to Run

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Set environment variables in a `.env` file, accordingly to `.env_example`.

3. Run the FastAPI application:
    ```sh
    uvicorn src.main:app
    ```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Redis-Py Connections Documentation](https://redis-py.readthedocs.io/en/stable/connections.html#id1)
- [Redis-Py Client Documentation](https://redis.io/docs/latest/develop/connect/clients/python/redis-py/)
- [Redis Quick Start Guide](https://redis.io/learn/howtos/quick-start)

## License

This project is licensed under the MIT License.
