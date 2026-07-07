import sqlite3
import datetime
class BankSim:
    def __init__(self):
        self.conn=sqlite3.connect("Bank.db")
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS Bank (
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            contribution REAL DEFAULT 0.0,
            contribution_date TEXT
        )""")
        self.conn.commit()
        self.current_user = None

    def create(self):
        login=input("Enter your new login: ").strip()
        self.c.execute("SELECT login FROM Bank WHERE login=?", (login,))
        if self.c.fetchone():
            print("--Login is already taken, choose another!")
            return self.run()
        if not login:
            print("--Login must not be empty!")
            return self.run()
        else:
            passw=input("Enter your a new password: ").strip()
        if not passw:
            print("--Password must not be empty!")
            return self.run()
        else:
            self.c.execute("INSERT INTO Bank (login, password) VALUES (?, ?)", (login, passw))
            print("\n---Account is successfully created!")
            self.current_user = login
            return self.menu()
        
    def sign_in(self):
        print("\n--- ENTER IN SYSTEM ---")
        login = input("Enter your login: ").strip()
        password = input("Enter your password: ").strip()
        if not login or not password:
            print(" Fields cannot be empty!")
            return self.run()
        self.c.execute("SELECT login FROM Bank WHERE login=? AND password=?", (login, password))
        if self.c.fetchone():
            print("\n---Successfully signed in!")
            self.current_user = login
            return self.menu()
        else:
            print("--Wrong login or password!")
            return self.run()
                
    def run(self):
        print("Hello there! This is Bank Simulator!")
        print("*1. Sign in \n*2.Create an account")
        cho=input("Enter the choice: ").strip()
        if cho=='1':
            return self.sign_in()
        if cho=="2":
            return self.create()

    def menu(self):
        print(f"\n-- MENU (Logged in as: {self.current_user}) --")
        print("*1.Add amount to account")
        print("*2.Withdraw of balance")
        print("*3.Move money to other people")
        print("*4.Move your money to contribution")
        print("*5.Check the balance")
        print("*6.Save and exit")
        while True:
            choice=input("Enter the choice: ").strip()
            if choice=="1":
                self.add()
            if choice=="2":
                return self.withdraw()
            if choice=="3":
                return self.people()
            if choice=="4":
                self.contribution()
            if choice=="5":
                return self.check()
            if choice=="6":
                print("\n---Goodbye!")
                break
            else:
                print("Enter only 1-6!")
        
    def add(self):
        print("\n--- AMOUNT TO YOUR ACCOUNT ---")
        try:
            addm = float(input("Enter the amount to your account: "))
            if addm <= 0:
                print("--Amount gotta be more than 0")
            else:
                self.c.execute("UPDATE Bank SET balance = balance + ? WHERE login = ?", (addm, self.current_user))
                self.conn.commit()
                print("\n--Amount successfully added!")
        except ValueError:
            print("--Only numbers!")
            
        return self.menu()
            
    def withdraw(self):
        print("\n--- WITHDRAW OF YOUR ACCOUNT ---")
        try:
            self.c.execute("SELECT balance FROM Bank WHERE login = ?", (self.current_user,))
            current_balance = self.c.fetchone()[0]
            addm = float(input("Enter the withdraw of your account: "))
            if current_balance<addm:
                print("You have not enough money on account!")
            elif addm <= 0:
                print("--The Withdraw gotta be more than 0")
            else:
                self.c.execute("UPDATE Bank SET balance = balance - ? WHERE login = ?", (addm, self.current_user))
                self.conn.commit()
                print(" \n---The withdraw successfully done!")
        except ValueError:
            print("--Only numbers!")
            
        return self.menu()
    
    def people(self):
        other_p=input("Enter who you wanna send the amount: ")
        self.c.execute("SELECT login FROM Bank WHERE login=? ", (other_p,))
        if self.c.fetchone():
            print("-Person is found!")
            self.c.execute("SELECT balance FROM Bank WHERE login = ?", (self.current_user,))
            current_balance = self.c.fetchone()[0]
            try:
                mon=int(input(f"Enter how much you wanna send to this person *{other_p}*: "))
                if current_balance<mon:
                    print("--You have not enough money on account!")
                else:
                    self.c.execute("UPDATE Bank SET balance = balance + ? WHERE login =?", (mon, other_p))
                    self.c.execute("UPDATE Bank SET balance = balance - ? WHERE login =?", (mon, self.current_user))
                    self.conn.commit()
            except ValueError:
                print("--Only numbers!")
        else:
            print("--Person is not found, try again")
            input(f"Enter how much you wanna send to this person *{other_p}*: ").strip()
            
        return self.menu()
            
    def check(self):
        print("\n---CHECK BALANCE---")
        self.c.execute("SELECT balance FROM Bank WHERE login=?", (self.current_user,))
        result=self.c.fetchone()
        if result:
            print(f"Your balance now: {result[0]}")
        else:
            print("--Error! User not found")
            
        return self.menu()
    
    def contribution(self):
        from datetime import datetime
        print("\n--CONTRIBUTION MANAGMENT--")
        self.c.execute("SELECT contribution, contribution_date FROM Bank WHERE login = ?", (self.current_user,))
        contrib, contrib_date_str = self.c.fetchone()
        if contrib > 0 and contrib_date_str:
            last_date = datetime.strptime(contrib_date_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            time_passed=now-last_date
            
            #test (one week for a 10 sec)
            weeks_passed = int(time_passed.total_seconds() // 10) #604800 it is week
                
            if weeks_passed>0:
                precent=0.05
                for _ in range(weeks_passed):
                    contrib=contrib + (contrib*precent)
                    
                new_date_str = now.strftime("%Y-%m-%d %H:%M:%S")
                self.c.execute("UPDATE Bank SET contribution = ?, contribution_date = ? WHERE login = ?", (contrib, new_date_str, self.current_user))
                self.conn.commit()
                print(f"You have new amount of you contribution by precent: {contrib}! Weeks passed: {weeks_passed}")
            
        print(f"Your savings account: {contrib:.2f}")
        print("1. Put money into contribution")
        print("2. Withdraw money out of contribution")
        print("3. Back to main menu")
        choice = input("Choice: ").strip()
        if choice == "1":
            try:
                amount = float(input("How much to deposit? ")).strip()
  
                self.c.execute("SELECT balance FROM Bank WHERE login = ?", (self.current_user,))
                current_balance = self.c.fetchone()[0]
                
                if amount > current_balance:
                    print("--Not enough money on main balance!")
                elif amount <= 0:
                    print("--Amount must be more than 0")
                else:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.c.execute("""UPDATE Bank SET 
                                      balance = balance - ?, 
                                      contribution = contribution + ?, 
                                      contribution_date = ? 
                                      WHERE login = ?""", (amount, amount, now_str, self.current_user))
                    self.conn.commit()
                    print("---Money moved to contribution! Percentages started ticking.")
                    return self.contribution()
            except ValueError:
                print("Only numbers!")
                
        if choice == "2":
            try:
                amount=float(input("Enter how much you wanna withdraw: ")).strip()
                self.c.execute("SELECT contribution FROM Bank WHERE login = ?", (self.current_user,))
                current_balance = self.c.fetchone()[0]
                
                if amount==0:
                    print("You no have money on your contribution!")
                elif amount <= 0:
                    print("--Amount must be more than 0")
                else:
                    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.c.execute("""UPDATE Bank SET 
                                      balance = balance + ?, 
                                      contribution = contribution - ?, 
                                      contribution_date = ? 
                                      WHERE login = ?""", (amount, amount, now_str, self.current_user))
                    self.conn.commit()
                    print("---Money moved to account!")
                    return self.contribution()
            except ValueError:
                print("Only numbers!")
                
        if choice == "3":
            return self.menu()
                
        
if __name__ == "__main__":
    bank = BankSim()
    bank.run()