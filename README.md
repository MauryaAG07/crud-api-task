# My First CRUD API

This is a simple RESTful API for managing a to-do list, built using Python and FastAPI. It supports full CRUD operations (Create, Read, Update, Delete) with data stored in-memory.

## How to Install and Run

To start the server, open your terminal in this directory and run:

`python3 -m uvicorn main:app --reload`

The API will be available at `http://localhost:8000`. 
You can view the interactive Swagger UI documentation at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Returns basic API information |
| GET | `/health` | Diagnostic health check |
| GET | `/tasks` | Lists all tasks |
| GET | `/tasks/{task_id}` | Retrieves a specific task by ID |
| POST | `/tasks` | Creates a new task (requires title) |
| PUT | `/tasks/{task_id}` | Updates a task's title/status |
| DELETE | `/tasks/{task_id}` | Deletes a task by ID |

## Example Request

**Creating a new task:**
```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Wed, 19 Aug 2026 00:00:00 GMT
server: uvicorn
content-length: 44
content-type: application/json

{"id":4,"title":"Buy milk","done":false}


