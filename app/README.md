# Finance Data Processing and Access Control Backend

A backend API for a finance dashboard system built with FastAPI, PostgreSQL, and JWT authentication.

## Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Auth**: JWT (python-jose) + bcrypt
- **Docs**: Auto-generated Swagger UI at `/docs`

## Setup Instructions

### 1. Clone the repository
git clone <your-repo-url>
cd finance-backend

### 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment
Copy `.env.example` to `.env` and fill in your values:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=finance_db
DB_USER=your_postgres_username
DB_PASSWORD=your_password
JWT_SECRET=your_secret_key

### 5. Create database
psql postgres -c "CREATE DATABASE finance_db;"

### 6. Run the server
uvicorn app.main:app --reload

### 7. Open API docs
http://127.0.0.1:8000/docs

## Roles

| Role    | Permissions |
|---------|-------------|
| viewer  | View records, view dashboard summary, view recent activity |
| analyst | All viewer permissions + category totals + monthly trends |
| admin   | Full access — create/edit/delete records, manage users |

## API Endpoints

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | /api/auth/register | Public | Register a new user |
| POST | /api/auth/login | Public | Login and get JWT token |

### Records
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /api/records/ | All roles | List records (filter by type, category, date, search) |
| POST | /api/records/ | Admin | Create a new record |
| GET | /api/records/{id} | All roles | Get a single record |
| PATCH | /api/records/{id} | Admin | Update a record |
| DELETE | /api/records/{id} | Admin | Soft delete a record |

### Dashboard
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /api/dashboard/summary | All roles | Total income, expenses, net balance |
| GET | /api/dashboard/categories | Analyst + Admin | Totals grouped by category |
| GET | /api/dashboard/recent | All roles | Recent transactions |
| GET | /api/dashboard/trends/monthly | Analyst + Admin | Month-by-month trends |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | /api/users/ | Admin | List all users |
| GET | /api/users/{id} | Admin | Get a user |
| PATCH | /api/users/{id} | Admin | Update role or status |
| DELETE | /api/users/{id} | Admin | Delete a user |

## Assumptions I Made
- Went with soft delete for records because finance data shouldnt be permanently lost
- Made viewer the default role since most users wont need write access
- Kept JWT expiry at 7 days so users dont have to login too often
- Admin cant delete themselves to avoid accidentally locking out the system
- Used SQLAlchemy ORM instead of raw SQL to keep the code readable