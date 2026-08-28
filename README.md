# Task List CRUD API

This project is a fully functional CRUD API that manages a task list, built for the FlyRank Backend AI Engineering Internship.

## Features
- Create, Read, Update, and Delete tasks.
- Containerized deployment using Docker and Docker Compose.
- Data persistence using a PostgreSQL database.
- Interactive API documentation via Swagger UI.

## Architecture & Storage

- **Tooling & Database Reasoning:** **SQLite** was initially chosen for this project because it is extremely lightweight, requires no background server to run, and makes local development incredibly easy. However, to support a production-like environment, the database has been upgraded to **PostgreSQL**.
- **Containerized Storage:** The PostgreSQL database now runs inside a Docker container. All data is persistently stored using a Docker volume, ensuring tasks survive container restarts and shutdowns.
- **Architecture Proof (FlyRank Requirement):** The repository pattern was utilized to seamlessly swap out the previous SQLite repository for the new PostgreSQL repository. Because of this cleanly layered architecture, **the service logic and API routes remained completely unchanged**.

## Persistence Test Validation (FlyRank Requirement)

To verify that the database data survives a server restart, the following persistence test was successfully conducted:
1. A new task was created using the `POST /tasks` endpoint in Swagger UI.
2. The Docker containers were completely shut down using `Control + C` in the terminal.
3. The stack was rebooted using the `docker compose up` command.
4. A `GET /tasks` request confirmed that the previously created task was still successfully retrieved from the Docker volume.

## How to Run the Project

To start the API on your local machine, follow these steps:

1. Ensure you have Docker Desktop installed and running on your machine.
2. Open your terminal in the project's root directory.
3. Run the application and database together using the following command: 
   ```bash
   docker compose up --build
   ```
4. Wait for the terminal to show that the application startup is complete. 
5. Open your browser and navigate to `http://localhost:8000/docs` to view and interact with the Swagger UI.

## Database Exploration
The database can be explored using any database GUI that supports PostgreSQL (such as DataGrip) by connecting to the local instance running in your Docker container. Below is a screenshot of the `tasks` table being viewed in DataGrip, showing that the data successfully synced with the API.

<img width="948" height="930" alt="DataGrip" src="https://github.com/user-attachments/assets/c7e89c9e-9c67-4635-be2b-70ebe8f5c5a2" />

### Example SQL Queries
During development, the following queries were executed directly on the database to verify persistence and API synchronization:

```sql
-- Mark every task as completed
UPDATE tasks SET done = 1;

-- Verify the changes
SELECT * FROM tasks WHERE done = 1;
```
For a visual walkthrough on getting this setup working smoothly, check out this [DataGrip and Docker guide](https://www.youtube.com/watch?v=_1xJYjtrn8I). It demonstrates exactly how to configure DataGrip to connect to a PostgreSQL instance running locally inside a Docker container.
