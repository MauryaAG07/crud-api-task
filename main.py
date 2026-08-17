from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# In-memory list of tasks
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk dog", "done": True},
    {"id": 3, "title": "Read book", "done": False}
]

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Get all tasks
@app.get("/tasks")
def get_tasks():
    return tasks

# Get a single task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})