from random import sample
# import database as db

# -------------start database.py--------------
# ---I have to copy code from database.py here,
# because hyperskill test system can't find this file ---
import sqlite3

CREATE_ACCOUNTS_TABLE = 'CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);'
INSERT_ACCOUNT = 'INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);'
CHECK_ACCOUNT_LOGIN = 'SELECT * FROM card WHERE number = ? AND pin = ?;'
ADD_INCOME = 'UPDATE card SET balance = balance + ? WHERE number = ?;'
READ_BALANCE = 'SELECT balance FROM card WHERE number = ?;'
REDUCE_BALANCE = 'UPDATE card SET balance = balance - ? WHERE number = ?;'
DELETE_CC = 'DELETE FROM card WHERE number = ?;'


def connect_db():
    return sqlite3.connect('card.s3db')


def create_tables_db(connection):
    cur = connection.cursor()
    cur.execute(CREATE_ACCOUNTS_TABLE)
    connection.commit()


def add_account_db(connection, number, pin, balance):
    with connection:
        connection.execute(INSERT_ACCOUNT, (number, pin, balance))


def check_login_db(connection, number, pin):
    with connection:
        return connection.execute(CHECK_ACCOUNT_LOGIN, (number, pin)).fetchone()


def add_income_db(connection, number, income):
    with connection:
        try:
            connection.execute(ADD_INCOME, (income, number))
        finally:
            print("Income was added!")


def read_balance_db(connection, number):
    with connection:
        return connection.execute(READ_BALANCE, (number,)).fetchone()[0]


def check_cc_db(connection, number):
    with connection:
        return connection.execute('SELECT number FROM card WHERE number = ?;', (number,)).fetchone()


def transfer_money_db(connection, number_from, number_to, money):
    with connection:
        connection.execute(REDUCE_BALANCE, (money, number_from))
        connection.execute(ADD_INCOME, (money, number_to))
    return "Success!"


def delete_cc_db(connection, number):
    with connection:
        connection.execute(DELETE_CC, (number,))
    return "The account has been closed!"


# -------------end database.py--------------

usr_choice = ""


def menu(logged_in=None, connection=None, usr_cc=None):
    if logged_in:
        print("\nYou have successfully logged in!\n")
        while True:
            print("""
1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
            user_logged_in_option = input()
            if user_logged_in_option == "1":  # Balance
                print("Balance:", read_balance_db(connection, usr_cc))
            elif user_logged_in_option == "2":  # Add income
                add_income_db(connection, usr_cc, int(input("Enter income:")))
            elif user_logged_in_option == "3":  # Do transfer
                usr_cc_to = input("Transfer\nEnter card number:\n")
                if usr_cc_to[-1] != str(luhn_check(usr_cc_to)):
                    print("Probably you made mistake in the card number. Please try again!")
                else:
                    if check_cc_db(connection, usr_cc_to):
                        money_to_transfer = int(input("Enter how much money you want to transfer:"))
                        if read_balance_db(connection, usr_cc) >= money_to_transfer:
                            print(transfer_money_db(connection, usr_cc, usr_cc_to, money_to_transfer))
                        else:
                            print("Not enough money!")
                    else:
                        print("Such a card does not exist.")
            elif user_logged_in_option == "4":  # Close account
                print(delete_cc_db(connection, usr_cc))
                break
            elif user_logged_in_option == "5":  # Log out
                print("You have successfully logged out!\n")
                break
            elif user_logged_in_option == "0":  # Exit
                global state
                state = False
                break
    else:
        print("1. Create an account\n2. Log into account\n0. Exit")
        global usr_choice
        usr_choice = input()


def luhn_check(card):
    evens = [int(i) for i in card[1:-1:2]]
    odds = []
    for i in range(0, len(card), 2):
        dbl_i = int(card[i]) * 2
        odds.append(dbl_i if dbl_i <= 9 else dbl_i - 9)
    sum_odds = sum(odds)
    sum_evens = sum(evens)
    control_sum = sum_odds + sum_evens
    checksum = 10 - control_sum % 10 if control_sum % 10 != 0 else 0
    return checksum


def create_account(connection):
    create_tables_db(connection)
    card_num = "400000" + "".join(sample("0123456789", 9))
    card_num = card_num + str(luhn_check(card_num))
    pin_code = "".join(sample("0123456789", 4))
    add_account_db(connection, card_num, pin_code, 0)
    print("Your card has been created")
    print("Your card number:")
    print(card_num)
    print("Your card PIN:")
    print(pin_code)
    print()


state = True

while state:
    connection = connect_db()
    create_tables_db(connection)
    menu()
    print()

    if usr_choice == "1":
        create_account(connection)
        continue
    elif usr_choice == "2":
        usr_cc = input("Enter your card number:\n")
        usr_pin = input("Enter your PIN:\n")
        if check_login_db(connection, usr_cc, usr_pin):
            menu(True, connection, usr_cc)
            continue
        else:
            print("\nWrong card number or PIN!\n")
            continue

    state = False
else:
    print("Bye!")
