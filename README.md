# ADRITE AGENCY - Backend API

Full-stack Digital Agency Platform built with FastAPI, PostgreSQL, Redis, and AWS S3.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python FastAPI |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Auth | JWT + OAuth2 (Google) |
| Payments | Stripe |
| Email | SendGrid |
| Storage | AWS S3 |
| Queue | Celery |
| Docs | Swagger UI |

---

## Project Structure

adrite-backend/
├── app/
│   ├── main.py
│   ├── core/          (config, security, database, redis, dependencies)
│   ├── models/        (user, project, ticket, invoice, chat, blog, analytics)
│   ├── schemas/       (user, project, ticket, invoice, chat, admin)
│   ├── api/v1/endpoints/ (auth, users, projects, tickets, invoices, chat, blogs, payments, webhooks, admin)
│   ├── services/      (auth, user, project, email, payment, storage)
│   ├── ai/            (llm_client, rag_pipeline, embeddings, vector_store)
│   ├── workers/       (celery_app, email_tasks, report_tasks, analytics_tasks)
│   ├── middleware/    (rate_limit, logging, cors)
│   └── utils/         (logger, exceptions, pagination, validators)
├── alembic/           (database migrations)
├── tests/             (test files)
├── docker/            (Dockerfile, docker-compose.yml)
├── scripts/           (init_db.py, seed_data.py, backup_db.sh)
├── .env.example
├── requirements.txt
└── README.md

---

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 15
- Redis 7
- Docker (optional)

---

### Local Setup

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/adrite-backend.git
cd adrite-backend
```

**2. Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

**5. Run database migrations**
```bash
alembic upgrade head
```

**6. Seed test data**
```bash
python scripts/seed_data.py
```

**7. Start the server**
```bash
uvicorn app.main:app --reload
```

API will be running at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

---

### Docker Setup

**Run everything with one command:**
```bash
docker-compose -f docker/docker-compose.yml up --build
```

**Run migrations inside Docker:**
```bash
docker exec -it adrite_api alembic upgrade head
docker exec -it adrite_api python scripts/seed_data.py
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/auth/register | Register new user | Public |
| POST | /api/v1/auth/login | User login | Public |
| POST | /api/v1/auth/logout | User logout | Authenticated |
| POST | /api/v1/auth/refresh | Refresh token | Authenticated |
| GET | /api/v1/auth/me | Get current user | Authenticated |
| POST | /api/v1/auth/google | Google OAuth login | Public |
| POST | /api/v1/auth/forgot-password | Request OTP | Public |
| POST | /api/v1/auth/verify-otp | Verify OTP | Public |
| POST | /api/v1/auth/reset-password | Reset password | Public |
| POST | /api/v1/auth/resend-otp | Resend OTP | Public |

### Users
| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | /api/v1/users/me | Get my profile | Authenticated |
| PUT | /api/v1/users/me | Update my profile | Authenticated |
| POST | /api/v1/users/me/avatar | Upload avatar | Authenticated |
| GET | /api/v1/users/ | Get all users | Admin |
| GET | /api/v1/users/{id} | Get single user | Admin |
| PUT | /api/v1/users/{id} | Update user | Admin |
| DELETE | /api/v1/users/{id} | Delete user | Admin |

### Projects
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/projects/ | Create project | Admin |
| GET | /api/v1/projects/ | Get all projects | Admin |
| GET | /api/v1/projects/my-projects | Get my projects | Client |
| GET | /api/v1/projects/{id} | Get single project | Authenticated |
| PUT | /api/v1/projects/{id} | Update project | Admin |
| DELETE | /api/v1/projects/{id} | Delete project | Admin |
| POST | /api/v1/projects/meetings | Schedule meeting | Authenticated |
| GET | /api/v1/projects/meetings | Get all meetings | Admin |
| GET | /api/v1/projects/meetings/my-meetings | Get my meetings | Client |

### Invoices
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/invoices/ | Create invoice | Admin |
| GET | /api/v1/invoices/ | Get all invoices | Admin |
| GET | /api/v1/invoices/my-invoices | Get my invoices | Client |
| GET | /api/v1/invoices/{id} | Get single invoice | Authenticated |
| PUT | /api/v1/invoices/{id} | Update invoice | Admin |
| DELETE | /api/v1/invoices/{id} | Delete invoice | Admin |

### Tickets
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/tickets/ | Create ticket | Client |
| GET | /api/v1/tickets/ | Get all tickets | Admin |
| GET | /api/v1/tickets/my-tickets | Get my tickets | Client |
| GET | /api/v1/tickets/{id} | Get single ticket | Authenticated |
| PUT | /api/v1/tickets/{id} | Update ticket | Authenticated |
| DELETE | /api/v1/tickets/{id} | Delete ticket | Admin |

### Blogs
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/blogs/ | Create blog | Admin |
| GET | /api/v1/blogs/ | Get published blogs | Public |
| GET | /api/v1/blogs/all | Get all blogs | Admin |
| GET | /api/v1/blogs/{id} | Get single blog | Public |
| PUT | /api/v1/blogs/{id} | Update blog | Admin |
| DELETE | /api/v1/blogs/{id} | Delete blog | Admin |

### Chat
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/chat/send | Send message | Authenticated |
| GET | /api/v1/chat/my-chats | Get my chats | Authenticated |
| GET | /api/v1/chat/ | Get all chats | Admin |
| WS | /api/v1/chat/ws/{client_id} | WebSocket chat | Authenticated |

### Payments
| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | /api/v1/payments/create-payment-intent | Create payment | Authenticated |
| POST | /api/v1/payments/webhook | Stripe webhook | Public |
| GET | /api/v1/payments/status/{id} | Payment status | Authenticated |

### Admin
| Method | Endpoint | Description | Access |
|---|---|---|---|
| GET | /api/v1/admin/dashboard | Dashboard stats | Admin |
| GET | /api/v1/admin/users | Get all users | Admin |
| GET | /api/v1/admin/revenue-overview | Revenue stats | Admin |
| GET | /api/v1/admin/projects-overview | Projects stats | Admin |
| GET | /api/v1/admin/tickets-overview | Tickets stats | Admin |
| PUT | /api/v1/admin/projects/{id}/assign | Assign task | Admin |

---

## Test Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@adrite.com | Admin@1234 |
| Client | john@example.com | Client@1234 |
| Client | sarah@example.com | Client@1234 |

---


## Intern

**Name:** Ifrah Sadiq
**Role:** Backend Developer
**Institution:** TechNexus Virtual University