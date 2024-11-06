# Backend Documentation

## Overview
This backend project is part of a *full-stack* **to-do list** application. It is built using FastAPI, a modern, fast (high-performance), ASGI (Asynchronous Server Gateway Interface) web framework for building APIs with Python 3.6+ based on standard Python type hints.

## Useful Links
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis-Py Connections Documentation](https://redis-py.readthedocs.io/en/stable/connections.html#id1)
- [Redis-Py Client Documentation](https://redis.io/docs/latest/develop/connect/clients/python/redis-py/)
- [Redis Quick Start Guide](https://redis.io/learn/howtos/quick-start)

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the backend directory.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Run the FastAPI server using `uvicorn src.main:app`.

## Features
<!-- - User authentication and authorization. -->
- CRUD operations for to-do items.
- Integration with Redis for items caching.

## License
This project is licensed under the MIT License.