# Bank Simulator

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/Status-Study%20Project-success)

A simple terminal-based banking simulator written in Python with SQLite.

## Features

- Create an account
- Sign in with login and password
- Add money to your balance
- Withdraw money from your balance
- Transfer money to another user
- Move money to a savings account
- Savings account interest growth over time
- Check your current balance
- Local data storage with SQLite database

## Commands

| Action | Command |
|---|---|
| Run the program | `python bank_sim.py` |
| Create database automatically | `Bank.db` |
| Start the app | `python <file_name>.py` |
| Exit the app | `Save and exit` |

## How It Works

The program stores users in a local SQLite database called `Bank.db`.

Each user has:
- login
- password
- balance
- contribution
- contribution date

After signing in, you can use the main menu to manage your money.

## Main Menu

- Add amount to account
- Withdraw from balance
- Transfer money to another user
- Move money to contribution
- Check balance
- Save and exit

## Savings Account

The app includes a simple savings system:
- Deposit money into contribution.
- Money grows over time by interest.
- Withdraw money back to your main balance.

## Requirements

- Python 3
- SQLite3

SQLite is included in the Python standard library, so no extra installation is needed.

## Run Project

```bash
python bank_sim.py
```

## Example Usage

1. Launch the program.
2. Create a new account.
3. Sign in.
4. Add money.
5. Transfer money or move it to savings.
6. Check your balance anytime.

## Project Structure

```text
project/
├── bank_sim.py
└── Bank.db
```

## Notes

- Passwords are stored in plain text in this version.
- The savings interest timing is simplified for testing purposes.
- The database is created automatically on first launch.

## Author

Made as a learning project for practicing Python, OOP, and SQLite.# Bank-Simulator-CLI
