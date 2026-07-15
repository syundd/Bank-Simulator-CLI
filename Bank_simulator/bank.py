import os
from datetime import datetime
from dotenv import load_dotenv
import psycopg

load_dotenv()

class BankSim:
    def __init__(self):
        self.conn = psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "banksim_db"),
            user=os.getenv("DB_USER", "banksim"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        self.c = self.conn.cursor()
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS accounts (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                balance NUMERIC(18,2) DEFAULT 0.00
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                from_user_id INT REFERENCES users(id) ON DELETE CASCADE,
                to_user_id INT REFERENCES users(id) ON DELETE CASCADE,
                amount NUMERIC(18,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contributions (
                id SERIAL PRIMARY KEY,
                account_id INT REFERENCES accounts(id) ON DELETE CASCADE,
                amount NUMERIC(18,2) NOT NULL DEFAULT 0.00,
                percent NUMERIC(4,2) DEFAULT 5.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_months INT DEFAULT 12
            );
        """)
        self.conn.commit()
        self.current_user_id = None
        self.current_user_login = None

    def create(self):
        login = input("Enter your new login: ").strip()
        if not login:
            print("--Login must not be empty!")
            return self.run()

        self.c.execute("SELECT id FROM users WHERE login = %s", (login,))
        if self.c.fetchone():
            print("--Login is already taken, choose another!")
            return self.run()

        password = input("Enter your new password: ").strip()
        if not password:
            print("--Password must not be empty!")
            return self.run()

        self.c.execute(
            "INSERT INTO users (login, password) VALUES (%s, %s) RETURNING id",
            (login, password)
        )
        user_id = self.c.fetchone()[0]
        
        self.c.execute(
            "INSERT INTO accounts (user_id, balance) VALUES (%s, 0.00)",
            (user_id,)
        )
        self.conn.commit()
        
        print("\n--- Account is successfully created!")
        self.current_user_id = user_id
        self.current_user_login = login
        return self.menu()

    def sign_in(self):
        print("\n--- ENTER IN SYSTEM ---")
        login = input("Enter your login: ").strip()
        password = input("Enter your password: ").strip()

        if not login or not password:
            print("--Fields cannot be empty!")
            return self.run()

        self.c.execute(
            "SELECT id, login FROM users WHERE login = %s AND password = %s",
            (login, password)
        )
        row = self.c.fetchone()
        if row:
            print("\n--- Successfully signed in!")
            self.current_user_id = row[0]
            self.current_user_login = row[1]
            return self.menu()

        print("--Wrong login or password!")
        return self.run()

    def run(self):
        print("Hello there! This is Bank Simulator!")
        print("1. Sign in")
        print("2. Create an account")
        choice = input("Enter the choice: ").strip()

        if choice == "1":
            return self.sign_in()
        elif choice == "2":
            return self.create()
        else:
            print("Enter only 1 or 2!")
            return self.run()

    def menu(self):
        while True:
            print(f"\n-- MENU (Logged in as: {self.current_user_login}) --")
            print("1. Add amount to account")
            print("2. Withdraw from balance")
            print("3. Transfer money to another user")
            print("4. Move money to savings")
            print("5. Check the balance")
            print("6. Save and exit")

            choice = input("Enter the choice: ").strip()

            if choice == "1":
                self.add()
            elif choice == "2":
                self.withdraw()
            elif choice == "3":
                self.people()
            elif choice == "4":
                self.contribution()
            elif choice == "5":
                self.check()
            elif choice == "6":
                print("\n--- Goodbye!")
                self.conn.close()
                break
            else:
                print("Enter only 1-6!")

    def add(self):
        print("\n--- ADD MONEY ---")
        try:
            amount = float(input("Enter the amount to add: "))
            if amount <= 0:
                print("--Amount must be more than 0")
                return

            self.c.execute(
                "UPDATE accounts SET balance = balance + %s WHERE user_id = %s",
                (amount, self.current_user_id)
            )
            self.conn.commit()
            print("--Amount successfully added!")
        except ValueError:
            print("--Only numbers!")

    def withdraw(self):
        print("\n--- WITHDRAW MONEY ---")
        try:
            self.c.execute("SELECT balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
            row = self.c.fetchone()
            if not row:
                print("--User account not found")
                return

            current_balance = float(row[0])
            amount = float(input("Enter the withdraw amount: "))

            if amount <= 0:
                print("--Amount must be more than 0")
            elif current_balance < amount:
                print("--You have not enough money on account!")
            else:
                self.c.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE user_id = %s",
                    (amount, self.current_user_id)
                )
                self.conn.commit()
                print("--The withdraw successfully done!")
        except ValueError:
            print("--Only numbers!")

    def people(self):
        other_user = input("Enter who you wanna send the amount: ").strip()
        if not other_user:
            print("--Login cannot be empty!")
            return

        if other_user == self.current_user_login:
            print("--You cannot send money to yourself!")
            return

        self.c.execute("SELECT id FROM users WHERE login = %s", (other_user,))
        target_row = self.c.fetchone()
        if not target_row:
            print("--Person is not found, try again")
            return

        to_user_id = target_row[0]
        print("-Person is found!")
        
        try:
            self.c.execute("SELECT balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
            row = self.c.fetchone()
            if not row:
                print("--User not found")
                return

            current_balance = float(row[0])
            amount = float(input(f"Enter how much you wanna send to {other_user}: "))

            if amount <= 0:
                print("--Amount must be more than 0")
            elif current_balance < amount:
                print("--You have not enough money on account!")
            else:
                self.c.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE user_id = %s",
                    (amount, to_user_id)
                )
                self.c.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE user_id = %s",
                    (amount, self.current_user_id)
                )
                self.c.execute(
                    "INSERT INTO transactions (from_user_id, to_user_id, amount) VALUES (%s, %s, %s)",
                    (self.current_user_id, to_user_id, amount)
                )
                self.conn.commit()
                print("--Money successfully transferred!")
        except ValueError:
            print("--Only numbers!")

    def check(self):
        print("\n--- CHECK BALANCE ---")
        self.c.execute("SELECT balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
        row = self.c.fetchone()
        if row:
            print(f"Your balance now: {float(row[0]):.2f}")
        else:
            print("--Error! User account not found")

    def contribution(self):
        print("\n--- CONTRIBUTION MANAGEMENT ---")
        
        self.c.execute("SELECT id FROM accounts WHERE user_id = %s", (self.current_user_id,))
        account_row = self.c.fetchone()
        if not account_row:
            print("--Error! Account not found")
            return
        account_id = account_row[0]

        self.c.execute(
            "SELECT id, amount, created_at, percent FROM contributions WHERE account_id = %s",
            (account_id,)
        )
        contrib_row = self.c.fetchone()

        contrib_id = None
        contrib_amount = 0.00
        contrib_date = None
        percent = 0.05

        if contrib_row:
            contrib_id, contrib_amount, contrib_date, percent_db = contrib_row
            contrib_amount = float(contrib_amount)
            percent = float(percent_db) / 100.0

            if contrib_amount > 0 and contrib_date:
                now = datetime.now()
                time_passed = now - contrib_date
                periods_passed = int(time_passed.total_seconds() // 10) #604800 sec - week

                if periods_passed > 0:
                    for _ in range(periods_passed):
                        contrib_amount += contrib_amount * percent

                    self.c.execute(
                        "UPDATE contributions SET amount = %s, created_at = %s WHERE id = %s",
                        (contrib_amount, now, contrib_id)
                    )
                    self.conn.commit()
                    print(f"You have new contribution amount: {contrib_amount:.2f}. Periods passed: {periods_passed}")

        print(f"Your savings account: {contrib_amount:.2f}")
        print("1. Put money into contribution")
        print("2. Withdraw money from contribution")
        print("3. Back to main menu")

        choice = input("Choice: ").strip()

        if choice == "1":
            try:
                amount = float(input("How much to deposit? "))
                if amount <= 0:
                    print("--Amount must be more than 0")
                    return

                self.c.execute("SELECT balance FROM accounts WHERE user_id = %s", (self.current_user_id,))
                row = self.c.fetchone()
                if not row:
                    print("--User not found")
                    return

                current_balance = float(row[0])
                if amount > current_balance:
                    print("--Not enough money on main balance!")
                    return

                now = datetime.now()
                
                self.c.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE id = %s",
                    (amount, account_id)
                )

                if contrib_row:
                    self.c.execute(
                        "UPDATE contributions SET amount = amount + %s, created_at = %s WHERE id = %s",
                        (amount, now, contrib_id)
                    )
                else:
                    self.c.execute(
                        "INSERT INTO contributions (account_id, amount, created_at, percent) VALUES (%s, %s, %s, 5.00)",
                        (account_id, amount, now)
                    )
                
                self.conn.commit()
                print("---Money moved to contribution! Interest timer started.")
            except ValueError:
                print("--Only numbers!")

        elif choice == "2":
            if contrib_amount <= 0:
                print("--You have no active contributions!")
                return
            try:
                amount = float(input("Enter how much you wanna withdraw: "))
                if amount <= 0:
                    print("--Amount must be more than 0")
                    return

                if amount > contrib_amount:
                    print("--Not enough money on your contribution!")
                    return

                now = datetime.now()
                self.c.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                    (amount, account_id)
                )
                self.c.execute(
                    "UPDATE contributions SET amount = amount - %s, created_at = %s WHERE id = %s",
                    (amount, now, contrib_id)
                )
                self.conn.commit()
                print("---Money moved to account!")
            except ValueError:
                print("--Only numbers!")

        elif choice == "3":
            return
        else:
            print("Enter only 1-3!")


if __name__ == "__main__":
    bank = BankSim()
    bank.run()