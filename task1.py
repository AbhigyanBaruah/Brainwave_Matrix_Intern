# MODULES
import sqlite3
import os

# ----------------------------------------------- #

class Database:
    def __init__(self, db_name="atm.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect_db()

    def connect_db(self): # Function to connect to the db 
        db_exists = os.path.exists(self.db_name)
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        if not db_exists:
            self.create_tables()

    def create_tables(self): # Function to create db if it does not exists
        self.cursor.execute(
            '''CREATE TABLE accounts (
                account_number TEXT PRIMARY KEY,
                pin TEXT,
                balance REAL DEFAULT 0
            )'''
        )
        self.cursor.execute(
            '''CREATE TABLE transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT,
                type TEXT,
                amount REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_number) REFERENCES accounts (account_number)
            )'''
        )
        self.connection.commit()

    def insert_account(self, account_number, pin, balance=0): # Creates new account and adds to the accounts table
        self.cursor.execute(
            "INSERT INTO accounts (account_number, pin, balance) VALUES (?, ?, ?)",
            (account_number, pin, balance)
        )
        self.connection.commit()

    def get_account(self, account_number): # Get the necessary data from the accounts table
        self.cursor.execute("SELECT * FROM accounts WHERE account_number=?", (account_number,))
        return self.cursor.fetchone()

    def update_balance(self, account_number, balance): # Update the balance in the accounts table
        self.cursor.execute("UPDATE accounts SET balance=? WHERE account_number=?", (balance, account_number))
        self.connection.commit()

    def update_pin(self, account_number, new_pin): # Update the pin in the accounts table
        self.cursor.execute("UPDATE accounts SET pin=? WHERE account_number=?", (new_pin, account_number))
        self.connection.commit()

    def record_transaction(self, account_number, type, amount): # Add data to the transactions table
        self.cursor.execute(
            "INSERT INTO transactions (account_number, type, amount) VALUES (?, ?, ?)",
            (account_number, type, amount)
        )
        self.connection.commit()

    def get_transaction_history(self, account_number): # Get the data from the transactions table
        self.cursor.execute("SELECT * FROM transactions WHERE account_number=?", (account_number,))
        return self.cursor.fetchall()

    def close(self): # CLosing the connection to the database
        self.connection.close()

# ----------------------------------------------- #

class Account:
    def __init__(self, account_number, pin, balance=0):
        self.account_number = account_number
        self.pin = pin
        self.balance = balance

    def check_balance(self): # Function to check the balance
        return self.balance

    def deposit(self, amount, db): # Function to deposit money
        if amount > 0:
            self.balance += amount
            db.update_balance(self.account_number, self.balance)
            db.record_transaction(self.account_number, 'deposit', amount)
            return True
        else:
            return False

    def withdraw(self, amount, db): # Function to withdraw money
        if 0 < amount <= self.balance:
            self.balance -= amount
            db.update_balance(self.account_number, self.balance)
            db.record_transaction(self.account_number, 'withdraw', amount)
            return True
        else:
            return False

    def change_pin(self, old_pin, new_pin, db): # Function to change the current pin
        if old_pin == self.pin:
            self.pin = new_pin
            db.update_pin(self.account_number, new_pin)
            return True
        else:
            return False

# ----------------------------------------------- #

class ATM:
    def __init__(self):
        self.db = Database()

    def authenticate(self): # Function to authenticate the user, called automatically on start
        account_number = input("Enter account number: ")
        pin = input("Enter PIN: ")

        account_data = self.db.get_account(account_number)
        if account_data:
            stored_pin = account_data[1]
            balance = account_data[2]
            if pin == stored_pin:
                return Account(account_number, pin, balance)
            else:
                print("Invalid PIN!")
                return None
        else:
            self.db.insert_account(account_number, pin)
            print("New account created successfully!")
            return Account(account_number, pin)

    def start(self): # Starting Function
        while True:
            print("\nWelcome to the ATM!")
            account = self.authenticate()
            if account:
                self.account_menu(account)
            else:
                print("Authentication failed!")

            exit_choice = input("Press 'q' to quit or any other key to continue: ")
            if exit_choice.lower() == 'q': # Option to exit the program completely
                print("Exiting...")
                self.db.close()
                break

    def account_menu(self, account): # Function to display the account menu, called after succesfull auhtentication 
        while True:
            print("\nAccount Menu:")
            print("1. Check Balance")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Change PIN")
            print("5. View Transaction History")
            print("6. Logout")
            choice = input("Enter your choice: ")
            print("\n")

            if choice == "1":
                print(f"Your balance is: Rs.{account.check_balance()}")

            elif choice == "2":
                amount = float(input("Enter amount to deposit: "))
                if account.deposit(amount, self.db):
                    print(f"Deposited Rs.{amount} successfully!")
                else:
                    print("Deposit failed!")

            elif choice == "3":
                amount = float(input("Enter amount to withdraw: "))
                if account.withdraw(amount, self.db):
                    print(f"Successfully withdrawn Rs.{amount}")
                else:
                    print("Insufficient balance!")
                    print(f"Current Balance: Rs.{Account.balance}")

            elif choice == "4":
                old_pin = input("Enter current PIN: ")
                new_pin = input("Enter new PIN: ")
                if account.change_pin(old_pin, new_pin, self.db):
                    print("PIN changed successfully!")
                else:
                    print("Current pin entered is not correct, please try again!")

            elif choice == "5":
                transactions = self.db.get_transaction_history(account.account_number)
                recent_transactions = transactions[-5:]
                print("Here is a list of your Recent Transactions: \n")
                print(f"{'Transaction ID':<18}{'Account Number':<18}{'Process Type':<18}{'Amount':<18}{'Timestamp'}")
                i = len(recent_transactions)
                for j in range(i):
                    print(f"{recent_transactions[j][0]:<18}{recent_transactions[j][1]:<18}{recent_transactions[j][2]:<18}{recent_transactions[j][3]:<18}{recent_transactions[j][4]}")

            elif choice == "6": # Logs out of current account
                print("Logging out...") 
                break

            else:
                print("Invalid choice! Please try again.")

            continue_choice = input("Do you want to continue? (y/n): ") # Allows the user to perform other process or else logout
            if continue_choice.lower() != 'y':
                print("Logging out...")
                break

# ----------------------------------------------- #

# Run the ATM Interface
if __name__ == "__main__":
    atm = ATM()
    atm.start()
