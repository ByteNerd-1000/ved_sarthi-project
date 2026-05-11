# Running Veda Sarthi Locally

This guide provides step-by-step instructions for running the Veda Sarthi Health Assistant project locally on your machine. The project consists of a FastAPI backend and a static HTML/JS frontend.

## Prerequisites
- Python 3.8+ installed on your system.
- An internet connection to install Python dependencies.

## Step 1: Run the Backend

The backend is built with FastAPI and runs on port `8002`.

1. Open a terminal and navigate to the `backend` directory of the project:
   ```bash
   cd "backend"
   ```

2. Create a Python virtual environment (recommended):
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```cmd
     venv\Scripts\activate
     ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   *This will install the following main dependencies for the FastAPI backend:*
   - `fastapi`: The web framework for building APIs.
   - `uvicorn`: The ASGI web server used to run FastAPI.
   - `pydantic` & `pydantic-settings`: For data validation and settings management.
   - `sqlalchemy`: SQL toolkit and Object-Relational Mapping (ORM) library.
   - `aiosqlite`: Asynchronous database driver for SQLite.
   - `python-dotenv`: For loading environment variables from a `.env` file.
   - `groq`: Official Python client for the Groq API (used for the AI model).
   - `aiofiles`, `python-multipart`, `pytest`


5. Start the backend server:
   ```bash
   python -m app.main
   ```
   *The backend will now be running on `http://localhost:8002`.*

## Step 2: Run the Frontend

The frontend is built with pure HTML, CSS, and JavaScript. It connects directly to the backend API via port 8002.

1. Open a **new terminal window** and navigate to the `frontend` directory:
   ```bash
   cd "frontend"
   ```

2. Start a simple HTTP server using Python:
   ```bash
   python3 -m http.server 8000
   ```
   *The frontend server will now be running on `http://localhost:8000`.*

## Step 3: Access the Application

3. temp
1. Open your web browser.
2. Navigate to **[http://localhost:8000](http://localhost:8000)**.
3. The Veda Sarthi chatbot interface should load. You can start typing messages, and the frontend will automatically connect to your local backend to generate AI responses.

> Note: Ensure both the backend terminal and frontend terminal remain open and running while you are using the application.
