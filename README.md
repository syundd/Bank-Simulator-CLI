# Bank Simulator CLI

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-used-2496ED?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Study%20Project-success)

A terminal-based banking simulator written in Python with PostgreSQL running in Docker.

## Features

- Create a new account.
- Sign in with login and password.
- Add money to your main balance.
- Withdraw money from your main balance.
- Transfer money to another user.
- Move money to a savings account.
- Savings balance grows over time.
- For testing, interest is applied every 10 seconds instead of one real week.
- Check your current balance.
- Store data in PostgreSQL instead of SQLite.
- Keep sensitive settings in a `.env` file.

## What's new

- Replaced SQLite with PostgreSQL.
- Connected the app to a PostgreSQL container in Docker.
- Moved database settings into `.env`.
- Added `requirements.txt` for easy dependency installation.
- Added `.gitignore` to keep secrets and cache files out of Git.
- Improved money display formatting with 2 decimal places.

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create `.env`

Create a file named `.env` in the project root:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=YOUR DB NAME
DB_USER=YOUR LOGIN
DB_PASSWORD=YOUR PASSWORD
```

### 3. Start PostgreSQL in Docker

```bash
docker run -d \
  --name banksim-postgres \
  -e POSTGRES_USER=YOUR LOGIN \
  -e POSTGRES_PASSWORD=YOUR PASSWORD\
  -e POSTGRES_DB=YOUR DB \
  -p 5433:5432 \
  -v banksim_pgdata:/var/lib/postgresql/data \
  postgres:16
```

### 4. Run the app

```bash
python3 bank.py
```

## Project Logic

The app stores users in PostgreSQL, and the Python code connects to it through Docker using `localhost:5433`.

Each account has:
- login
- password
- balance
- contribution
- contribution date

After signing in, you can manage your money through the terminal menu.

## Main Actions

- Add money to your balance.
- Withdraw money from your balance.
- Send money to another user.
- Deposit money into savings.
- Withdraw money from savings.
- Check your balance.
- Save and exit.

## Savings System

The savings account uses a simplified test mode.

For demo purposes, interest is applied every 10 seconds instead of one week, so the feature is easier to test and demonstrate.

## Requirements

- Python 3
- Docker
- PostgreSQL runs in a container
- `psycopg[binary]`
- `python-dotenv`

## Project Structure

```text
project/
├── bank.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Notes

- Passwords are stored in plain text in this version.
- The interest timing is accelerated for testing.
- PostgreSQL runs in Docker, while the app itself runs on your laptop.
- If port `5432` is busy, `5433:5432` avoids the conflict.

## Author

Made as a learning project for practicing Python, OOP, Docker, and PostgreSQL.