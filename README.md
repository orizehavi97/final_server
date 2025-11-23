# ML Training and Prediction Server

A production-ready FastAPI server for machine learning model training and prediction with comprehensive user authentication, token-based access control, JWT security, logging system, and dual Streamlit dashboards.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Docker Setup (Recommended)](#docker-setup-recommended)
- [API Documentation](#api-documentation)
- [ML Capabilities](#ml-capabilities)
- [Usage Examples](#usage-examples)
- [Security Features](#security-features)
- [Token System](#token-system)
- [Educational Purpose](#educational-purpose)

---

## ✨ Features

### Core Functionality
- **🤖 Machine Learning**: Train and deploy 6 different ML models (Linear/Random Forest/SVM for regression & classification)
- **👤 User Management**: Secure user registration and authentication with bcrypt password hashing
- **🎟️ Token Economy**: Pay-per-use system with credit card validation for token purchases
- **🔐 JWT Authentication**: Secure Bearer token authentication with configurable expiration
- **📊 Dual Dashboards**: Admin dashboard for oversight and user dashboard for ML operations
- **📝 Comprehensive Logging**: Structured logging of all operations with context
- **⚡ Rate Limiting**: Configurable rate limiting (20 requests/minute per user)
- **💾 Model Persistence**: Automatic model saving with metadata and evaluation metrics
- **📈 Model Evaluation**: Detailed metrics for both regression and classification models

### API Endpoints
- **Public**: Health check, user signup/login, account deletion
- **Protected**: Token management, model training, predictions, model listing

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | FastAPI, Uvicorn (ASGI server) |
| **Database** | PostgreSQL, SQLAlchemy ORM |
| **Machine Learning** | scikit-learn, pandas, joblib |
| **Authentication** | JWT (python-jose), bcrypt, passlib |
| **UI/Dashboard** | Streamlit |
| **Environment** | python-dotenv |
| **Logging** | Python logging module |
| **Containerization** | Docker, Docker Compose |

---

## 📁 Project Structure

```
FINALSERVER/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection & session
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py               # User table schema
│   │   └── model_metadata.py    # ML model metadata schema
│   │
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── user_schemas.py       # User-related schemas
│   │   └── ml_schemas.py         # ML-related schemas
│   │
│   ├── routers/                   # API route handlers
│   │   ├── user_router.py        # User management endpoints
│   │   └── ml_router.py          # ML operations endpoints
│   │
│   ├── services/                  # Business logic layer
│   │   ├── user_service.py       # User CRUD & auth logic
│   │   └── ml_service.py         # ML training & prediction logic
│   │
│   └── utils/                     # Utility functions
│       ├── auth.py               # Password hashing
│       ├── jwt.py                # JWT token management
│       ├── dependencies.py       # FastAPI dependencies
│       ├── logger.py             # Logging configuration
│       └── rate_limiter.py       # Rate limiting logic
│
├── models/                        # Saved ML models (.pkl files)
├── logs/                          # Application log files
├── test_data/                     # Sample CSV datasets
│   ├── housing_data.csv
│   ├── salary_prediction.csv
│   └── customer_churn.csv
│
├── admin_dashboard.py             # Streamlit admin dashboard
├── user_dashboard.py              # Streamlit user interface
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (not in repo)
├── .env.example                  # Example environment file
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/finalserver.git
   cd finalserver
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Create PostgreSQL database**
   ```sql
   CREATE DATABASE finalserver_db;
   ```

2. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/finalserver_db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   HOST=0.0.0.0
   PORT=8000
   ```

3. **Generate SECRET_KEY**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

4. **Initialize database**

   The application will automatically create tables on first run, or you can manually create them:
   ```sql
   -- Users table
   CREATE TABLE users (
       id SERIAL PRIMARY KEY,
       username VARCHAR(255) UNIQUE NOT NULL,
       hashed_password VARCHAR(255) NOT NULL,
       tokens INTEGER DEFAULT 0
   );

   -- Model metadata table
   CREATE TABLE model_metadata (
       id SERIAL PRIMARY KEY,
       model_name VARCHAR(255) UNIQUE NOT NULL,
       model_type VARCHAR(255) NOT NULL,
       features JSON NOT NULL,
       label VARCHAR(255) NOT NULL,
       trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       file_path VARCHAR(255) NOT NULL,
       metrics JSON
   );
   ```

### Running the Application

**1. Start FastAPI Server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**2. Start Admin Dashboard (Optional)**
```bash
streamlit run admin_dashboard.py
```
- Dashboard: http://localhost:8501

**3. Start User Dashboard (Optional)**
```bash
streamlit run user_dashboard.py --server.port=8502
```
- User UI: http://localhost:8502

---

## 🐳 Docker Setup (Recommended)

**This is the easiest way to run the project!** Docker Compose will automatically set up PostgreSQL, FastAPI server, and both Streamlit dashboards with one command.

### Prerequisites

- **Docker Desktop**: Download and install from https://www.docker.com/products/docker-desktop
  - Windows: Docker Desktop for Windows
  - macOS: Docker Desktop for Mac
  - Linux: Docker Engine + Docker Compose

### What Docker Setup Includes

The Docker setup creates **4 services**:
1. **PostgreSQL Database** (port 5432) - Automatically initialized with tables
2. **FastAPI Server** (port 8000) - Your ML API with JWT authentication
3. **Admin Dashboard** (port 8501) - Streamlit dashboard for user management
4. **User Dashboard** (port 8502) - Streamlit interface for ML operations

All services are **automatically connected** and configured. No manual setup required!

### Quick Start with Docker

#### 1. Clone the repository
```bash
git clone https://github.com/yourusername/finalserver.git
cd finalserver
```

#### 2. Start all services (first time)
```bash
docker-compose up --build
```

**What happens:**
- Downloads PostgreSQL 15 image
- Builds FastAPI and Streamlit images
- Creates database and tables automatically (via init.sql)
- Starts all 4 services
- Services wait for dependencies (API waits for DB to be healthy)

**First-time startup:** ~2-3 minutes (downloads images)
**Subsequent startups:** ~10-20 seconds

#### 3. Access the application

Once you see `Application startup complete` in the logs:

- **FastAPI Server**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:8501
- **User Dashboard**: http://localhost:8502

### Docker Commands

**Start services (foreground with logs)**
```bash
docker-compose up
```

**Start services in background (detached mode)**
```bash
docker-compose up -d
```

**View logs from all services**
```bash
docker-compose logs -f
```

**View logs from specific service**
```bash
docker-compose logs -f api           # FastAPI logs
docker-compose logs -f db            # PostgreSQL logs
docker-compose logs -f admin_dashboard
```

**Stop services (keeps data)**
```bash
docker-compose down
```

**Stop and remove all data (fresh start)**
```bash
docker-compose down -v
```
⚠️ This deletes the database, all users, and trained models!

**Rebuild images (after code changes)**
```bash
docker-compose build --no-cache
docker-compose up
```

**Check running containers**
```bash
docker-compose ps
```

**Access PostgreSQL database directly**
```bash
docker exec -it finalserver_db psql -U postgres -d finalserver_db
```

### Docker Architecture

```
┌─────────────────────────────────────────────────────┐
│          Docker Compose Network                      │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│  │    db    │◄──┤   api    │◄──┤  admin_  │       │
│  │(postgres)│   │(fastapi) │   │dashboard │       │
│  │:5432     │   │:8000     │   │:8501     │       │
│  └──────────┘   └──────────┘   └──────────┘       │
│       ▲                                             │
│       │         ┌──────────┐                       │
│       └─────────┤  user_   │                       │
│                 │dashboard │                       │
│                 │:8502     │                       │
│                 └──────────┘                       │
└─────────────────────────────────────────────────────┘
```

### Data Persistence

Docker setup includes **volume mounting** for data persistence:

- **Database data**: Stored in Docker volume `postgres_data` (survives restarts)
- **Trained models**: `./models` directory (accessible on host machine)
- **Logs**: `./logs` directory (accessible on host machine)

Even after `docker-compose down`, your trained models and logs remain!

### Environment Variables (Pre-configured)

All environment variables are **hardcoded in docker-compose.yml** for convenience:

```yaml
DATABASE_URL: postgresql://postgres:postgres@db:5432/finalserver_db
SECRET_KEY: 9c6629dbe3912dcf7c2682102a6d0a4dea86948679835e11fe3be7cbba0df741
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30
```

No need to create a `.env` file when using Docker!

### Troubleshooting Docker

**Port already in use**
```bash
# Check what's using the port
netstat -ano | findstr :8000    # Windows
lsof -i :8000                   # macOS/Linux

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 on host instead
```

**Containers not starting**
```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs

# Restart specific service
docker-compose restart api
```

**Database connection errors**
```bash
# Verify database is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**Out of disk space**
```bash
# Remove unused Docker resources
docker system prune -a
```

**Complete reset**
```bash
# Nuclear option: delete everything
docker-compose down -v
docker system prune -a
docker-compose up --build
```

---

## 📚 API Documentation

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/signup` | Register new user |
| POST | `/login` | Login and get JWT token |
| DELETE | `/remove_user` | Delete user account |

### Protected Endpoints (JWT Required)

Add `Authorization: Bearer <your_jwt_token>` header to all requests.

| Method | Endpoint | Token Cost | Description |
|--------|----------|-----------|-------------|
| GET | `/tokens` | 0 | Get current token balance |
| POST | `/add_tokens` | 0 | Purchase tokens |
| POST | `/train` | 1 | Train ML model |
| POST | `/predict/{model_name}` | 5 | Make prediction |
| GET | `/models` | 1 | List all trained models |
| GET | `/models/{model_name}/metrics` | 1 | Get model evaluation metrics |

### Interactive API Documentation

FastAPI provides automatic interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🤖 ML Capabilities

### Supported Models

**Regression Models** (for continuous predictions):
- **Linear Regression**: Simple linear relationships
- **Random Forest Regressor**: Non-linear patterns with ensemble learning
- **Support Vector Regressor (SVR)**: Complex patterns with RBF kernel

**Classification Models** (for categorical predictions):
- **Logistic Regression**: Binary/multi-class classification
- **Random Forest Classifier**: Ensemble classification
- **Support Vector Classifier (SVC)**: Kernel-based classification

### Evaluation Metrics

**Regression Metrics**:
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)
- R² (Coefficient of Determination)

**Classification Metrics**:
- Accuracy
- Precision
- Recall
- F1 Score

---

## 💡 Usage Examples

### 1. User Registration and Authentication

**Sign Up**
```bash
curl -X POST "http://localhost:8000/signup" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "securepass123"}'
```

**Login to Get JWT Token**
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "securepass123"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Purchase Tokens

```bash
curl -X POST "http://localhost:8000/add_tokens" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"credit_card": "1234-5678-9999-0000", "amount": 20}'
```

### 3. Train a Model

```bash
curl -X POST "http://localhost:8000/train" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@test_data/housing_data.csv" \
  -F 'model_name=price_predictor' \
  -F 'model_type=linear_regression' \
  -F 'features=["age", "salary", "rooms"]' \
  -F 'label=price'
```

### 4. Make a Prediction

```bash
curl -X POST "http://localhost:8000/predict/price_predictor" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"age": 35, "salary": 70000, "rooms": 3}'
```

Response:
```json
{
  "prediction": 315000.5,
  "model_name": "price_predictor",
  "model_type": "linear_regression"
}
```

### 5. List All Models

```bash
curl -X GET "http://localhost:8000/models" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 6. Get Model Metrics

```bash
curl -X GET "http://localhost:8000/models/price_predictor/metrics" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🔒 Security Features

- **Password Hashing**: Bcrypt with automatic salt generation
- **JWT Tokens**: HS256 algorithm with configurable expiration (default: 30 minutes)
- **Token-Based Access**: Pay-per-use model prevents abuse
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Rate Limiting**: Configurable per-user rate limits (default: 20 req/min)
- **CORS**: Configured middleware for cross-origin requests
- **Audit Logging**: Comprehensive logging of all operations

---

## 🎯 Token System

### Token Costs

| Operation | Token Cost |
|-----------|-----------|
| Check token balance | 0 tokens (FREE) |
| Purchase tokens | 0 tokens (FREE) |
| Train model | 1 token |
| Make prediction | 5 tokens |
| List models | 1 token |
| Get model metrics | 1 token |

### Purchasing Tokens

Users can purchase tokens using credit card validation (format: `XXXX-XXXX-XXXX-XXXX`).
- Minimum: 1 token
- Maximum: 100 tokens per transaction
- **Note**: This is a simulated payment system for educational purposes

---

## 🎓 Educational Purpose

This project was developed as a final project for a Python AI course, demonstrating:
- RESTful API design with FastAPI
- Database design and ORM usage
- Machine learning model training and deployment
- User authentication and authorization
- Token-based access control
- Logging and monitoring
- Containerization with Docker
- Full-stack development with Python

---

**Made with ❤️ using Python and FastAPI**
