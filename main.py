from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Header
import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client
from pydantic import BaseModel
from fastapi import HTTPException, status

class AuthCredentials(BaseModel):
    email: str
    password: str
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
DATABASE_URL = os.getenv("DATABASE_URL")
app = FastAPI()
security = HTTPBearer() #this is to prevent swagger ui from native security handling

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """FastAPI Dependency to extract and verify the JWT."""
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        return user_response.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user = Depends(verify_token)):
    """Logs the user out and terminates the session."""
    supabase.auth.sign_out()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/protected/dashboard")
def dashboard(current_user = Depends(verify_token)):
    """A second protected route to test middleware reusability."""
    return {"message": f"Welcome to the dashboard, {current_user.email}!"}

@app.get("/public/info", status_code=status.HTTP_200_OK)
def public_info():
    """A public route anyone can access."""
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def protected_profile(current_user = Depends(verify_token)):
    """A protected route using our reusable dependency."""
    # The route only runs if verify_token succeeds!
    return {"message": "Access granted", "user": current_user}

    # FastAPI auto-strips "Bearer" and gives us the raw token string
@app.post("/auth/signup",status_code = status.HTTP_201_CREATED)
def signup(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Incorrect email or password"
                            )
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password
        })
        return response.user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
@app.post("/auth/login",status_code = status.HTTP_200_OK)
def login(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials"
        )
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