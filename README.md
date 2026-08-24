# Task List CRUD API

This project is a fully functional CRUD API that manages a task list, built for the FlyRank Backend AI Engineering track. 

## Features
- Create, Read, Update, and Delete tasks.
- Data persistence using a relational database.
- Interactive API documentation via Swagger UI.

## Architecture & Storage
- **Database Choice:** **SQLite** was chosen for this project because it is extremely lightweight, requires no background server to run, and makes local development incredibly easy. 
- **Storage Location:** All data is persistently stored in a single file located in the root directory named `tasks.db`.

## How to Run the Project
To start the API on your local machine, follow these steps:

1. Ensure you have the required dependencies installed (FastAPI and Uvicorn).
2. Open your terminal in the project's root directory.
3. Run the development server using the following command:
   ```bash
   uvicorn main:app --reload
   ```
4. The API will automatically generate the `tasks.db` file if it does not exist. 
5. Open your browser and navigate to `http://localhost:8000/docs` to view and interact with the Swagger UI.

## Database Exploration
The database can be explored using any SQLite viewer (such as DataGrip). Below is a screenshot of the `tasks` table being viewed in DataGrip, showing that the data successfully synced with the API.

<img width="948" height="930" alt="DataGrip" src="https://github.com/user-attachments/assets/c7e89c9e-9c67-4635-be2b-70ebe8f5c5a2" />

### Example SQL Queries
During development, the following queries were executed directly on the database to verify persistence and API synchronization:

```sql
-- Mark every task as completed
UPDATE tasks SET done = 1;

-- Verify the changes
SELECT * FROM tasks WHERE done = 1;
```
