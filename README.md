# Task List CRUD API

This project is a fully functional CRUD API that manages a task list, built for the FlyRank Backend AI Engineering Internship. It has been upgraded to include secure JWT authentication using Supabase.

## Features

- Create, Read, Update, and Delete tasks.
- Secure Authentication (Sign Up, Log In, Log Out) using Supabase and JSON Web Tokens (JWT).
- Protected API routes using FastAPI HTTPBearer middleware.
- Containerized deployment using Docker and Docker Compose.
- Data persistence using a PostgreSQL database.
- Interactive API documentation via Swagger UI.

## Local Environment Setup

To run this project securely, you must configure your environment variables. 
1. Create a `.env` file in the root directory.
2. Add your database and Supabase credentials to the file:

    DATABASE_URL=your_postgresql_database_url
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_anon_key

*(Note: The `.env` file is included in `.gitignore` to keep credentials secure and should never be pushed to version control.)*

## How to Run the Project

To start the API on your local machine, follow these steps:
1. Ensure you have Docker Desktop installed and running on your machine.
2. Open your terminal in the project's root directory.
3. Run the application and database together using the following command: `docker compose up --build`
4. Wait for the terminal to show that the application startup is complete.
5. Open your browser and navigate to `http://localhost:8000/docs` to view and interact with the Swagger UI.

## API Endpoints & Authentication

| Method | Endpoint | Authentication Required | Description |
| :--- | :--- | :--- | :--- |
| **POST** | `/auth/signup` | No | Register a new user with email/password. |
| **POST** | `/auth/login` | No | Authenticate user and receive a JWT access token. |
| **POST** | `/auth/logout` | **Yes (Bearer Token)** | Terminate the current user session. |
| **GET** | `/public/info` | No | Read public, unprotected data. |
| **GET** | `/protected/profile` | **Yes (Bearer Token)** | Read secure user metadata using token verification. |
| **GET** | `/protected/dashboard` | **Yes (Bearer Token)** | Secondary protected route testing middleware. |
| **GET** | `/tasks` | No | Retrieve a list of all current tasks. |
| **POST** | `/tasks` | No | Create a new task. |
| **GET** | `/tasks/{id}` | No | Retrieve a specific task by ID. |
| **PUT** | `/tasks/{id}` | No | Update a task's title or completion status. |
| **DELETE**| `/tasks/{id}` | No | Permanently delete a task. |

## Interactive Documentation (Swagger UI)

The API uses FastAPI's built-in Swagger UI for interactive testing. Protected routes are secured using a Bearer token scheme. Users can log in, copy their `access_token`, and inject it into the **Authorize** menu to unlock protected endpoints.

<img width="1289" height="869" alt="protected" src="https://github.com/user-attachments/assets/cf02bf85-7c1e-4bde-b97f-60bb9a253e40" />


## Architecture & Storage

- **Tooling & Database Reasoning:** **SQLite** was initially chosen for this project because it is extremely lightweight, requires no background server to run, and makes local development incredibly easy. However, to support a production-like environment, the database has been upgraded to **PostgreSQL**.
- **Containerized Storage:** The PostgreSQL database now runs inside a Docker container. All data is persistently stored using a Docker volume, ensuring tasks survive container restarts and shutdowns.
- **Architecture Proof (FlyRank Requirement):** The repository pattern was utilized to seamlessly swap out the previous SQLite repository for the new PostgreSQL repository. Because of this cleanly layered architecture, **the service logic and API routes remained completely unchanged**.

## Database Exploration

The database can be explored using any database GUI that supports PostgreSQL (such as DataGrip) by connecting to the local instance running in your Docker container. 

### Example SQL Queries

    -- Mark every task as completed
    UPDATE tasks SET done = 1;
    
    -- Verify the changes
    SELECT * FROM tasks WHERE done = 1;
