import random
import sqlite3

connection = sqlite3.connect('card.s3db')
cursor = connection.cursor()
cursor.execute('DROP TABLE IF EXISTS card')
cursor.execute('''CREATE TABLE card(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0)''')


class Account:
    def __init__(self):
        self.balance = 0
        self.card_number = create_card()
        self.pin = generate_pin()


def get_balance(user):
    x = cursor.execute("""select balance from card where number = '{}'""".format(user)).fetchone()
    if x:
        print(x[0])
    return x[0]


def add_income(user):
    value = int(input("Enter income:"))
    y = cursor.execute("""select balance from card where number = '{}'""".format(user)).fetchone()
    cursor.execute("""update card set balance = '{}' where number = '{}'""".format(y[0] + value, user)).fetchone()
    connection.commit()
    print("Income was added!")


def do_transfer(user):
    receivers_acc = int(input("Enter card number:"))

    x = cursor.execute("""select number from card where number = '{}'""".format(receivers_acc)).fetchone()
    y = cursor.execute("""select balance from card where number = '{}'""".format(user)).fetchone()
    z = cursor.execute("""select balance from card where number = '{}'""".format(receivers_acc)).fetchone()

    if int(receivers_acc) == int(user):
        print("You can't transfer money to the same account!")
    elif alg_luhn(receivers_acc) != 0:
        print("Probably you made a mistake in the card number. Please try again!")
    elif not x:
        print("Such a card does not exist.")
    else:
        money = int(input("Enter how much money you want to transfer:"))
        if money > y[0]:
            print("Not enough money!")
        else:
            cursor.execute("""update card set balance = '{}' where number = '{}'""".format(y[0] - money, user))
            connection.commit()
            cursor.execute("""update card set balance = '{}' where number = '{}'""".format(z[0] + money, receivers_acc))
            connection.commit()


def delete_account(user):
    cursor.execute(""" delete from card where number='{}'""".format(user))
    connection.commit()
    print("The account has been closed!")


def num_concat(num1, num2):
    # Convert both the numbers to
    # strings
    num1 = str(num1)
    num2 = str(num2)
    # Concatenate the strings
    num1 += num2
    return int(num1)


# Returns the checksum number if the string has 15 digits or the 16th checksum number is incorrect
def alg_luhn(number):
    number = str(number)
    last = 0
    number = list(map(int, number))
    if len(number) == 16:
        last = number[15]
        del number[-1]
    i = 0
    for y in number:
        if i % 2 == 0:  # Checks if the number is odd position and multiply by 2
            z = int(number[i]) * 2
            number[i] = z
            if number[i] > 9:  # Subtract 9 to numbers over 9
                number[i] -= 9
        i += 1
    total = sum(number)  # Add all numbers

    while total % 10 != 0:
        total += 1

    if last is not None and last == (total - sum(number)):
        return 0
    else:
        return total - sum(number)


# Returns a card number (with 15 digits)
def create_card():
    inn = str(400000)
    card_number = int(inn + str(random.randint(100000000, 999999999)))
    card_number = num_concat(card_number, alg_luhn(card_number))  # Adds the checksum digit
    print("Your card has been created")
    print("Your card number:")
    print(card_number)

    return card_number


# Returns a PIN number
def generate_pin():
    pin = random.randint(1000, 9999)
    print("Your card PIN:")
    print(pin)
    return pin


# Login authentication
def check_login():
    card = int(input("Enter your card number:"))
    pin = int(input("Enter your PIN:"))
    x = cursor.execute("""select pin from card where number = '{}'""".format(card)).fetchone()
    y = cursor.execute("""select number from card where pin = '{}'""".format(pin)).fetchone()

    if x and y:
        print("You have successfully logged in!")
        return card
    else:
        print("Wrong card number or PIN!")


users = []


def menu_global():
    option = input("1. Create an account \n2. Log into account \n0. Exit \n")
    global users
    if option == "1":
        alucard = Account()
        users.append(alucard)
        cursor.execute("INSERT INTO card (number, pin) VALUES (?, ?)",
                       (alucard.card_number, alucard.pin))
        connection.commit()
        menu_global()
    elif option == "2":
        menu_account(check_login())
    elif option == "3":
        print("Bye!")
    connection.commit()


def menu_account(num_card):
    option = input("1. Balance \n2. Add income \n3. Do transfer \n4. Close account \n5. Log out \n0. Exit \n")
    if option == "1":
        get_balance(num_card)
        menu_account(num_card)
    elif option == "2":
        add_income(num_card)
        menu_account(num_card)
    elif option == "3":
        do_transfer(num_card)
        menu_account(num_card)
    elif option == "4":
        delete_account(num_card)
        menu_account(num_card)
    elif option == "5":
        print("You have successfully logged out!")
        menu_global()
    elif option == "0":
        exit()


menu_global()
