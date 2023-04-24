"""
An ATM machine has dispatching 100, 200, and 500 currency notes on a priority
 and requested amount basis.
 Write a Python Program and take input from the command line
  and display how many types of currency notes will dispatch out using Class Based Functions.
"""
from datetime import datetime
#import pymongo
import pymongo


class ATM:
    """
    creating the class for access ATM and withdraw amount from ATM.
    """

    def __init__(self):
        self.balance = 125000
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db_connection = self.client["ATM"]
        self.transactions = self.db_connection["transactions"]

    def _dispatch_notes(self, amount):
        """
        Amount will be dispatch_notes from account..
        """
        remaining_amount = amount
        five_hundred_notes = remaining_amount // 500
        remaining_amount = remaining_amount % 500
        two_hundred_notes = remaining_amount // 200
        remaining_amount = remaining_amount % 200
        hundred_notes = remaining_amount // 100
        remaining_amount = remaining_amount % 100
        return five_hundred_notes, two_hundred_notes, hundred_notes, remaining_amount

    def _get_transaction_details(self, amount):
        dispatched_notes = self._dispatch_notes(amount)
        transaction_details = {
            "datetime": datetime.now(),
            "amount_withdrawn": amount,
            "500_notes_dispatched": dispatched_notes[0],
            "200_notes_dispatched": dispatched_notes[1],
            "100_notes_dispatched": dispatched_notes[2],
            "balance": self.balance - amount
        }
        self.transactions.insert_one(transaction_details)
        self.balance = transaction_details["balance"]
        return dispatched_notes

    def withdraw(self, amount):
        """
        Amount withdraw from account.
        """

        if amount > 125000:
            raise ValueError("Amount exceeds maximum balance limit.")
        if amount > 10000:
            raise ValueError("Maximum withdrawal limit is 10000.")
        if amount % 100 != 0:
            raise ValueError("Amount should be in multiples of 100.")
        dispatched_notes = self._get_transaction_details(amount)
        return dispatched_notes
#for show balance
    def show_balance(self):
        """
        This function shows balance in account
        """
        return f"Your balance is {self.balance}"

if __name__ == "__main__":
    atm = ATM()
    try:
        amount = int(input("Enter the amount to withdraw: "))
        dispatched_notes = atm.withdraw(amount)
        print("Dispensed notes:")
        if dispatched_notes[0] > 0:
            print("500 Currency Notes:", dispatched_notes[0])
        if dispatched_notes[1] > 0:
            print("200 Currency Notes:", dispatched_notes[1])
        if dispatched_notes[2] > 0:
            print("100 Currency Notes:", dispatched_notes[2])
        print(atm.show_balance())
    except ValueError as e:
        print(e)

    print("Transaction History:")
    for transaction in atm.transactions.find().sort("datetime", pymongo.DESCENDING):
        print(transaction)
