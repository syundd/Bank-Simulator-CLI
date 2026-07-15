# Bank Simulator CLI

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-used-2496ED?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Study%20Project-success)

A terminal-based banking simulator written in Python with PostgreSQL running in Docker. Now upgraded with a normalized database schema consisting of four connected tables.

## Features

- **User Authentication**: Simple sign-up and sign-in using login and password.
- **Balance Management**: Add funds to or withdraw from your main account.
- **Inter-user Transfers**: Seamlessly transfer money to another user by their login.
- **Savings System (Contributions)**: Move money to a savings account and watch it grow.
- **Transaction Ledger**: Every single transfer is securely logged in a dedicated history table.
- **Fast Testing Mode**: Interest on savings accumulates every 10 seconds (for demonstration/testing purposes) instead of one real-world week.

---

## 🚀 What's New (v2.0)

- **Database Normalization (4 Connected Tables)**: Split the single database table into four distinct, logically linked tables (`users`, `accounts`, `transactions`, `contributions`).
- **ID-Based Internal Logic**: Replaced old text-based query references with auto-incrementing integer IDs (`SERIAL PRIMARY KEY`).
- **Data Integrity**: Handled clean record removal using `ON DELETE CASCADE` foreign keys.
- **Detailed Transactions**: Added a separate table to keep track of all user-to-user transfers.

---

## Database Schema (PostgreSQL)

  ┌──────────────┐          ┌──────────────┐
  │    users     │          │   accounts   │
  ├──────────────┤          ├──────────────┤
  │ id (PK)  ───┼─────────>│ id (PK)      │
  │ login        │ 1:1      │ user_id (FK) │
  │ password     │          │ balance      │
  └──────────────┘          └──────┬───────┘
         │                         │
         │ 1:N                     │ 1:1 (Optional)
         ▼                         ▼
  ┌──────────────┐          ┌───────────────┐
  │ transactions │          │ contributions │
  ├──────────────┤          ├───────────────┤
  │ id (PK)      │          │ id (PK)       │
  │ from_user_id │          │ account_id(FK)│
  │ to_user_id   │          │ amount        │
  │ amount       │          │ percent       │
  │ created_at   │          │ created_at    │
  └──────────────┘          └───────────────┘

---

## How to Run

### 1. Install dependencies

Make sure to install the required libraries:

pip install -r requirements.txt

### 2. Create `.env`

Create a `.env` file in your project root folder:

DB_HOST=localhost
DB_PORT=5433
DB_NAME=YOUR DB NAME
DB_USER=YOUR LOGIN
DB_PASSWORD=YOUR PASSWORD

### 3. Start PostgreSQL in Docker

Run this command to spin up your database container on port 5433:

docker run -d \
  --name banksim-postgres \
  -e POSTGRES_USER="YOUR LOGIN" \
  -e POSTGRES_PASSWORD="YOUR PASSWORD" \
  -e POSTGRES_DB="YOUR DB" \
  -p 5433:5432 \
  -v banksim_pgdata:/var/lib/postgresql/data \
  postgres:16

### 4. Run the app

python bank.py

---

## Requirements

- Python 3.x
- Docker
- `psycopg` (for database connection)
- `python-dotenv` (for loading environment variables)

Add these to your `requirements.txt`:

psycopg[binary]
python-dotenv

---

## Project Structure

project/
├── bank.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md

---

## Notes

- **Password Storage**: Passwords are stored in plain text in this version.
- **Dockerized Storage**: Database volume mapping (`banksim_pgdata`) ensures your simulated bank accounts remain safe even if the Docker container is stopped or removed.

## Author

Made as an advanced learning project to practice Python OOP, relational database design (PostgreSQL), and Docker environments.