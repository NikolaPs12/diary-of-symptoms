Diary of Symptoms

A full-stack system for tracking health symptoms, medications, and generating AI-powered health insights across web and Telegram interfaces.

---

Overview

Diary of Symptoms is a distributed health-tracking platform designed to help users record symptoms, medications, sleep quality, and related health metadata, then analyze trends using AI-assisted insights.

It provides:

- Web interface (React + Vite)
- REST API (FastAPI)
- PostgreSQL database
- Telegram bot interface
- AI-based symptom analysis layer

---

Features

- Symptom tracking with severity, duration, and context
- Medication and diagnosis history management
- Sleep and stress correlation tracking
- AI-generated health insights
- Multi-channel access (Web + Telegram)
- RESTful API with OpenAPI documentation
- Docker-based deployment

---

Architecture

Frontend (React + Vite)
        ↓
Backend API (FastAPI)
        ↓
Service Layer (Business Logic)
        ↓
PostgreSQL Database

        ↓
AI Analysis Service (external API integration)

        ↓
Telegram Bot Interface (async API client)

---

Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic
- Frontend: React, Vite
- Database: PostgreSQL
- Bot: Python Telegram Bot / Async client
- Deployment: Docker, Docker Compose
- Testing: Pytest, Pytest-asyncio
- AI: External LLM API integration

---

Installation

1. Clone repository

git clone <repository-url>
cd diary-of-symptoms

2. Environment setup

Create ".env" file:

DB_NAME=diary
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

API_AI_KEY=your_ai_key
TOKEN=your_telegram_bot_token

---

3. Run with Docker (recommended)

docker compose up --build

---

4. Local development

Backend

cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend

cd frontend
npm install
npm run dev

---

Access Points

Service| URL| Description
Frontend| http://localhost:5173| Web application
Backend API| http://localhost:8000| REST API
Swagger UI| http://localhost:8000/docs| API documentation
ReDoc| http://localhost:8000/redoc| Alternative docs
PostgreSQL| localhost:5433| External DB access

---

Authentication Flow

1. User registers via "/auth/register"
2. User logs in via "/auth/login"
3. Backend returns JWT token
4. Token is used in requests:

-H "Authorization: Bearer <TOKEN>"

---

API Examples

Register

curl -X POST http://localhost:8000/api/auth/register \
-H "Content-Type: application/json" \
-d '{
  "name": "User",
  "email": "user@example.com",
  "password": "StrongPassword123"
}'

---

Login

curl -X POST http://localhost:8000/api/auth/login \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "StrongPassword123"
}'

---

Create symptom entry

curl -X POST http://localhost:8000/api/symptoms \
-H "Authorization: Bearer <TOKEN>" \
-H "Content-Type: application/json" \
-d '{
  "symptom": "Headache",
  "severity": 7,
  "duration": "3 hours",
  "sleep_hours": 5,
  "stress_level": 8
}'

---

Telegram Bot

The Telegram bot provides quick access to core features without using the web UI.

Features

- Add symptom via chat
- Retrieve last entries
- Get AI health summary

Setup

TOKEN=your_telegram_bot_token

Run

docker compose up --build

If "TOKEN" is not set, the bot service will remain disabled.

---

Testing

Run tests:

pytest

Run inside Docker:

docker compose exec backend pytest

Coverage areas

- Authentication logic
- Symptom CRUD
- Database integration
- API validation
- AI fallback behavior

---

Performance Considerations

- Asynchronous FastAPI backend
- Separate database service
- Stateless API design
- Externalized AI processing
- Dockerized services for scaling

Potential optimizations:

- caching repeated AI queries
- background task queue (Celery/RQ)
- DB indexing on user_id and timestamps
- rate limiting for AI endpoints

---

Roadmap

Completed

- Full-stack MVP
- Symptom tracking system
- PostgreSQL integration
- Telegram bot
- AI integration
- Docker deployment

Planned
- [ ] Advanced JWT roles (RBAC)
- [ ] CI/CD pipeline
- [ ] Health analytics dashboard
- [ ] PDF report export
- [ ] Notification system
- [ ] Advanced trend analysis

---

Security

- JWT-based authentication
- Environment-based secrets management
- Input validation via Pydantic
- Separation of API and AI layers

Recommended improvements:

- rate limiting (anti-abuse)
- audit logging
- secure secret storage (vault / CI secrets)
- HTTPS enforcement in production

---

Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Open Pull Request

Guidelines:

- small atomic commits
- clear PR descriptions
- no secrets in code
- update documentation when needed

---

License

MIT License (or project-specific license)

---

Author

Maintained by project contributor(s).

---

Contact

- GitHub: https://github.com/<your-profile>
- Email: <your-email>
- Telegram: <your-telegram>

---

Notes

This project is designed as a portfolio-grade full-stack system demonstrating backend architecture, API design, and multi-interface integration (web + bot + AI).