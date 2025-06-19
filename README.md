# Lending Service - Loan Billing System

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)

This repository contains a application designed to manage a lending service. It provides functionalities for creating loans, tracking payments, calculating outstanding balances, generating repayment schedules, and monitoring loan delinquency statuses.

## Features

- 📅 **Loan Schedule Generation**: 50-week repayment plans with flat 10% interest
- 💰 **Payment Tracking**: Record weekly payments automatically
- ⚠️ **Delinquency Detection**: Flag borrowers missing 2+ consecutive payments
- 📊 **Outstanding Balance Calculation**: Real-time remaining balance
- 🔐 **SSH Authentication**: Secure GitHub integration


## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: SQLite

## Installation

### Prerequisites
- Python 3.9+
- Git (configured with SSH)

```bash
# Clone via SSH
git clone git@github.com:aalviian/lending-service.git
cd lending-service

# Set up environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### 1. Create .env file:
```bash
DEBUG=True
SECRET_KEY=your_django_secret
DB_NAME=lending_db
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=localhost
TIME_ZONE=Asia/Jakarta
```

### 2. Run migrations:
```bash
python manage.py migrate
```

### 3. Running the Application
Start the development server:
```bash
python manage.py runserver
```
The API will now be accessible at http://127.0.0.1:8000/.

## Sequence Diagram
<img width="883" alt="Screenshot 2025-06-19 at 17 43 11" src="https://github.com/user-attachments/assets/17d01345-5cd8-4b8f-b91d-e8d2e38efe6e" />

## ERD
<img width="796" alt="Screenshot 2025-06-19 at 17 50 14" src="https://github.com/user-attachments/assets/6ea6c49d-4484-42da-9df0-4c30da3b0b71" />


## APIs
### User Authentication
1. Register a New User

This endpoint allows new users to register for the lending service.

* **URL:** `/api/register/`
* **Method:** `POST`
* **Permissions:** `AllowAny`
* **Request Body:**
    * `username` (string, required)
    * `password` (string, required)
    * `email` (string, required)

**cURL Example:**

```bash
curl -X POST \
  [http://127.0.0.1:8000/api/register/](http://127.0.0.1:8000/api/register/) \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your_username",
    "password": "your_password",
    "email": "your_email@example.com"
}'
```

2. User Login and Token Generation

This endpoint allows registered users to log in and obtain JWT (JSON Web Token) access and refresh tokens. The `access` token should be used for authenticating subsequent API requests.

* **URL:** `/api/login/`
* **Method:** `POST`
* **Permissions:** `AllowAny`
* **Request Body:**
    * `username` (string, required)
    * `password` (string, required)

**cURL Example:**

```bash
curl -X POST \
  [http://127.0.0.1:8000/api/login/](http://127.0.0.1:8000/api/login/) \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "your_username",
    "password": "your_password"
}'
```

### Billing APIs
1. Create New Loan

This endpoint allows the creation of a new loan with a specified principal amount. A 50-week repayment plan with a flat 10% interest is automatically generated.

* **URL:** `/billing/loans/`
* **Method:** `POST`
* **Permissions:** `IsAuthenticated`
* **Request Body:**
    * `loan_id` (string, required): A unique identifier for the loan.
    * `principal_amount` (decimal, required): The initial amount of the loan.

**cURL Example:**

```bash
curl -X POST \
  [http://127.0.0.1:8000/billing/loans/](http://127.0.0.1:8000/billing/loans/) \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer <your_access_token>' \
  -d '{
    "loan_id": "LOAN-001",
    "principal_amount": "2000000.00"
}'
```

# API Endpoints

| Endpoint                          | Method | Description                          | Example Response |
|-----------------------------------|--------|--------------------------------------|------------------|
| `/loans/`                         | POST   | Create new loan                      | ```json {"loan_id": 1, "principal_amount": "2000000.00", "start_date": "2025-06-18", "weekly_payment": "44000.00", "total_amount": "2200000.00"}``` |
| `/loans/<loan_id>/schedule/`      | GET    | View repayment schedule             | ```json {"loan_id": 1, "schedule": {"W1": {"due_amount": 44000.0, "paid": false, "payment_date": null}, "W2": {"due_amount": 44000.0, "paid": false, "payment_date": null},}}``` |
| `/loans/<loan_id>/outstanding/`   | GET    | Check outstanding balance           | ```json {"outstanding_balance": 4400000}``` |
| `/payments/`                      | POST   | Record payment                     | ```json {"id": 19, "loan": 2, "amount": "44000.00", "payment_date": "2025-06-18T09:54:31.976252Z"}``` |
| `/loans/<loan_id>/status/`        | GET    | Check delinquency status            | ```json {"is_delinquent": false}``` |


### Security Best Practices
1. Input Validation (prevent SQL Injection, XSS)
2. Rate Limiting (mencegah DDoS)
3. Secret Management (Vault, AWS Secrets Manager)

### Compliance & Audit
1. Logging (track data changes)
2. GDPR/Data Privacy (enkripsi PII)

### DevOps & Observability
a. CI/CD Pipeline
1. GitHub Actions/GitLab CI
2. Docker & Kubernetes
3. Infrastructure as Code (Terraform)

b. Monitoring & Alerting
1. Metrics (Prometheus, Datadog)
2. Issue alert (Sentry)
3. Log Aggregation (ELK Stack)
