from fastapi import FastAPI, Response
from pydantic import BaseModel

app = FastAPI()
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CrudAPI", "done": False},
    {"id": 3, "title": "Publish to Github", "done": False},
]


class TaskInput(BaseModel):
    title: str = None

class TaskUpdate(BaseModel):
    title: str = None
    done: bool = None

@app.get("/")
def root():
    """Returns basic information qnd metadata about the API"""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    """Diagnostic endpoint to check if the server is running successfully"""
    return {"status": "ok"}


@app.get("/tasks")
def read_tasks():
    """Retrieves a list of all current tasks"""
    return tasks


@app.get("/tasks/{task_id}")
def read_task(task_id: int, response: Response):
    """Retrieves a single specific task by its ID number."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    response.status_code = 404
    return {"error": f"Task {task_id} not found"}


@app.post("/tasks")
def create_task(task_input: TaskInput, response: Response):
    """Creates a new task, requiring a valid title in the request"""
    if not task_input.title or not task_input.title.strip():
        response.status_code = 400
        return {"error": "Title is missing or empty"}

    new_id = max(t["id"] for t in tasks) + 1 if tasks else 1
    new_task = {"id": new_id, "title": task_input.title, "done": False}
    tasks.append(new_task)

    response.status_code = 201
    return new_task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, response: Response):
    """Updates an existing task's title and/or completion status."""
    if task_update.title is None and task_update.done is None:
        response.status_code = 400
        return {"error": "Request is missing or empty"}
    if task_update.title is not None and not task_update.title.strip():
        response.status_code = 400
        return {"error": "Title is missing or empty"}

    for task in tasks:
        if task["id"] == task_id:
            if task_update.title is not None:
                task["title"] = task_update.title
            if task_update.done is not None:
                task["done"] = task_update.done
            return task
    response.status_code = 404
    return {"error": f"Task {task_id} not found"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, response: Response):
    """Permanently deletes an existing task, found by its ID number"""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            response.status_code = 204
            return
    response.status_code = 404
    return {"error": f"Task {task_id} not found"}