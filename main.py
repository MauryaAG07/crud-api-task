from fastapi import FastAPI, Response
from pydantic import BaseModel
import sqlite3

app = FastAPI()
# stage 0: database init
def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL
    )
    """)
    #checking whether table is empty or not
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        task_starter = [
            ("Learn FastAPI", False),
            ("Build CrudAPI", True),
            ("Publish to Github", False),
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", task_starter)
        conn.commit()
    conn.close()
# run init once file loads
init_db()
#deleted old task box
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
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    grab = conn.cursor()
    grab.execute("SELECT * FROM tasks")
    tasks = grab.fetchall()
    conn.close()
    return tasks


@app.get("/tasks/{task_id}")
def read_task(task_id: int, response: Response):
    """Retrieves a single specific task by its ID number."""
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) # task_id is inside a
    # one item list within a tuple, we are expecting only one variable to be injected
    tasks = cursor.fetchone()
    conn.close()
    if not tasks:
        response.status_code = 404
        return {"error": f"Task {task_id} not found"}
    return tasks #if the program gets here, that means the requested task is in the dataset

@app.post("/tasks")
def create_task(task_input: TaskInput, response: Response):
    """Creates a new task, requiring a valid title in the request"""
    if not task_input.title or not task_input.title.strip():
        response.status_code = 400
        return {"error": "Title is missing or empty"}
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?,?)", (task_input.title, False))
    new_task = {
        "id": cursor.lastrowid,
        "title": task_input.title,
        "done": False
    }

    conn.commit()
    conn.close()
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