from fastapi import FastAPI, Response
from pydantic import BaseModel
import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
DATABASE_URL = os.getenv("DATABASE_URL")
app = FastAPI()
# stage 0: database init
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    with open ("init.sql", "r") as file:
        sql_script = file.read()
    cursor.execute(sql_script)
    conn.commit()
    #checking whether table is empty or not
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        task_starter = [
            ("Learn FastAPI", False),
            ("Build CrudAPI", True),
            ("Publish to Github", False),
        ]
        cursor.executemany("INSERT INTO tasks (title, done) VALUES (%s, %s)", task_starter) #psycopg2 uses %s instead of ?
        conn.commit()
    cursor.close()
    conn.close()
# run init once file loads
init_db()
#deleted old task box
class TaskInput(BaseModel):
    title: str

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
    conn = psycopg2.connect(DATABASE_URL)
    grab = conn.cursor()
    grab.execute("SELECT * FROM tasks ORDER BY id ASC")
    raw_tasks = grab.fetchall()
    formatted_tasks = [
        {"id": row[0],"title": row[1],"done": row[2] } for row in raw_tasks
    ]
    grab.close()
    conn.close()
    return formatted_tasks


@app.get("/tasks/{task_id}")
def read_task(task_id: int, response: Response):
    """Retrieves a single specific task by its ID number."""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)) # task_id is inside a
    # one item list within a tuple, we are expecting only one variable to be injected
    tasks = cursor.fetchone()
    # selects data, no need to commit
    cursor.close()
    conn.close()
    if not tasks:
        response.status_code = 404
        return {"error": f"Task {task_id} not found"}
    formatted_task = {
        "id": tasks[0],
        "title": tasks[1],
        "done": tasks[2]
    }
    return formatted_task #if the program gets here, that means the requested task is in the dataset

@app.post("/tasks")
def create_task(task_input: TaskInput, response: Response):
    """Creates a new task, requiring a valid title in the request"""
    if not task_input.title or not task_input.title.strip():
        response.status_code = 400
        return {"error": "Title is missing or empty"}
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s,%s)RETURNING *", (task_input.title, False))
    uniform_task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    formatted_task = {
        "id": uniform_task[0],
        "title": uniform_task[1],
        "done": uniform_task[2]}

    response.status_code = 201
    return formatted_task
# make changes to main file ^
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate, response: Response):
    """Updates an existing task's title and/or completion status."""
    if task_update.title is None and task_update.done is None:
        response.status_code = 400
        return {"error": "Request is missing or empty"}
    if task_update.title is not None and not task_update.title.strip():
        response.status_code = 400
        return {"error": "Title is missing or empty"}

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)) #reformatted to fit psycopg2
    current_task = cursor.fetchone()
    if current_task is None:
        cursor.close()
        conn.close()
        response.status_code = 404
        return {"error": f"Task {task_id} not found"}
    final_title = task_update.title if task_update.title is not None else current_task[1]
    final_done = task_update.done if task_update.done is not None else current_task[2]
    cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s", (final_title,final_done, task_id))
    conn.commit()
    cursor.close()
    conn.close()
    final_task = {
        "id": task_id,
        "title": final_title,
        "done": final_done
    }
    return final_task


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, response: Response):
    """Permanently deletes an existing task, found by its ID number"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))

    if cursor.rowcount == 0:
        response.status_code = 404
        cursor.close()
        conn.close()
        return {"error": f"Task {task_id} not found"}
    conn.commit() #if it made it here that means the task existed.
    cursor.close()
    conn.close()
    #return success status
    response.status_code = 204
    return