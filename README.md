# Social Platform API

A social platform backend built with **FastAPI, PostgreSQL, and SQLAlchemy**.

## Features

- User registration
- Login with username or email
- Password hashing
- JWT authentication
- Database migrations with Alembic

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-folder>
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
APP_NAME=Social Platform API
APP_ENV=development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/social_platform
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace `YOUR_PASSWORD` and `your_secret_key` with your own values.

### 5. Apply Database Migrations

```powershell
python -m alembic upgrade head
```

### 6. Start the Server

```powershell
python -m uvicorn app.main:app --reload
```

## API Documentation

After starting the server, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login using username or email |

## Database Migrations

### Create a Migration

```powershell
python -m alembic revision --autogenerate -m "describe your change"
```

### Apply Migrations

```powershell
python -m alembic upgrade head
```