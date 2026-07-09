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
        CREATE TABLE IF NOT EXISTS bank (
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance NUMERIC(12,2) DEFAULT 0.00,
            contribution NUMERIC(12,2) DEFAULT 0.00,
            contribution_date TIMESTAMP
            )
        """)
        self.conn.commit()
        self.current_user = None

    def create(self):
        login = input("Enter your new login: ").strip()
        if not login:
            print("--Login must not be empty!")
            return self.run()

        self.c.execute("SELECT login FROM bank WHERE login = %s", (login,))
        if self.c.fetchone():
            print("--Login is already taken, choose another!")
            return self.run()

        password = input("Enter your new password: ").strip()
        if not password:
            print("--Password must not be empty!")
            return self.run()

        self.c.execute(
            "INSERT INTO bank (login, password) VALUES (%s, %s)",
            (login, password)
        )
        self.conn.commit()
        print("\n--- Account is successfully created!")
        self.current_user = login
        return self.menu()

    def sign_in(self):
        print("\n--- ENTER IN SYSTEM ---")
        login = input("Enter your login: ").strip()
        password = input("Enter your password: ").strip()

        if not login or not password:
            print("--Fields cannot be empty!")
            return self.run()

        self.c.execute(
            "SELECT login FROM bank WHERE login = %s AND password = %s",
            (login, password)
        )
        if self.c.fetchone():
            print("\n--- Successfully signed in!")
            self.current_user = login
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
            print(f"\n-- MENU (Logged in as: {self.current_user}) --")
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
                "UPDATE bank SET balance = balance + %s WHERE login = %s",
                (amount, self.current_user)
            )
            self.conn.commit()
            print("--Amount successfully added!")
        except ValueError:
            print("--Only numbers!")

    def withdraw(self):
        print("\n--- WITHDRAW MONEY ---")
        try:
            self.c.execute("SELECT balance FROM bank WHERE login = %s", (self.current_user,))
            row = self.c.fetchone()
            if not row:
                print("--User not found")
                return

            current_balance = float(row[0])
            amount = float(input("Enter the withdraw amount: "))

            if amount <= 0:
                print("--Amount must be more than 0")
            elif current_balance < amount:
                print("--You have not enough money on account!")
            else:
                self.c.execute(
                    "UPDATE bank SET balance = balance - %s WHERE login = %s",
                    (amount, self.current_user)
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

        self.c.execute("SELECT login FROM bank WHERE login = %s", (other_user,))
        if not self.c.fetchone():
            print("--Person is not found, try again")
            return

        print("-Person is found!")
        try:
            self.c.execute("SELECT balance FROM bank WHERE login = %s", (self.current_user,))
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
                    "UPDATE bank SET balance = balance + %s WHERE login = %s",
                    (amount, other_user)
                )
                self.c.execute(
                    "UPDATE bank SET balance = balance - %s WHERE login = %s",
                    (amount, self.current_user)
                )
                self.conn.commit()
                print("--Money successfully transferred!")
        except ValueError:
            print("--Only numbers!")

    def check(self):
        print("\n--- CHECK BALANCE ---")
        self.c.execute("SELECT balance FROM bank WHERE login = %s", (self.current_user,))
        row = self.c.fetchone()
        if row:
            print(f"Your balance now: {float(row[0]):.2f}")
        else:
            print("--Error! User not found")

    def contribution(self):
        print("\n--- CONTRIBUTION MANAGEMENT ---")
        self.c.execute(
            "SELECT contribution, contribution_date FROM bank WHERE login = %s",
            (self.current_user,)
        )
        row = self.c.fetchone()
        if not row:
            print("--Error! User not found")
            return

        contrib, contrib_date = row
        contrib = float(contrib)

        if contrib > 0 and contrib_date:
            now = datetime.now()
            time_passed = now - contrib_date
            periods_passed = int(time_passed.total_seconds() // 10)

            if periods_passed > 0:
                percent = 0.05
                for _ in range(periods_passed):
                    contrib += contrib * percent

                self.c.execute(
                    "UPDATE bank SET contribution = %s, contribution_date = %s WHERE login = %s",
                    (contrib, now, self.current_user)
                )
                self.conn.commit()
                print(f"You have new contribution amount: {contrib:.2f}. Periods passed: {periods_passed}")

        print(f"Your savings account: {contrib:.2f}")
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

                self.c.execute("SELECT balance FROM bank WHERE login = %s", (self.current_user,))
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
                    """
                    UPDATE bank SET
                        balance = balance - %s,
                        contribution = contribution + %s,
                        contribution_date = %s
                    WHERE login = %s
                    """,
                    (amount, amount, now, self.current_user)
                )
                self.conn.commit()
                print("---Money moved to contribution! Interest timer started.")
            except ValueError:
                print("--Only numbers!")

        elif choice == "2":
            try:
                amount = float(input("Enter how much you wanna withdraw: "))
                if amount <= 0:
                    print("--Amount must be more than 0")
                    return

                self.c.execute("SELECT contribution FROM bank WHERE login = %s", (self.current_user,))
                row = self.c.fetchone()
                if not row:
                    print("--User not found")
                    return

                current_contribution = float(row[0])
                if amount > current_contribution:
                    print("--Not enough money on your contribution!")
                    return

                now = datetime.now()
                self.c.execute(
                    """
                    UPDATE bank SET
                        balance = balance + %s,
                        contribution = contribution - %s,
                        contribution_date = %s
                    WHERE login = %s
                    """,
                    (amount, amount, now, self.current_user)
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