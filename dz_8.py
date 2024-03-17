from collections import UserDict, UserList
import datetime  as dt
from datetime import datetime  as dtdt
from abc import ABC, abstractmethod

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    def __init__(self, value):
        # if value[0].isupper():
        self.value = value
        # else:
        #     raise ValueError("Incorect Name")
class Phone(Field):
    def __init__(self, value):
        if  int(value) == float(value) and len(value) == 10:
            self.value = value
        else:
            raise ValueError ("Incorect Phone")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = dtdt.strptime(value, "%d.%m.%Y").date()  # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
            
    def add_phone(self, phone):
        p = self.find_phone(phone)
        if p is None:
            self.phones.append(Phone(phone))
            
    def remove_phone(self, phone):
        p = self.find_phone(phone)
        self.phones.remove(p)
            
    def edit_phone(self, old_phone, new_phone):
        number = self.find_phone(old_phone)
        if number:
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"    

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        for names, record in self.data.items():
            if name in names:
                return self.data[names]
    
    def find_birthday(self, name):
        for names, record in self.data.items():
            if name in names:
                return f"Contact name:{name}, birthday: {record.birthday.value.strftime("%d.%m.%Y")}"
            
    def delete(self, name):
        self.data.pop(name)

    def all(self):
        for record in self.data.values():
            print(record)
    
    def get_upcoming_birthdays(self):
        now = dtdt.today().date() #поточний час
        birthdays = []
        for name, record in self.data.items():
            date_user = record.birthday.value
            week_day = date_user.isoweekday()
            difference_day = (date_user.day - now.day)
            if 1 <= difference_day < 7 :
                if difference_day < 6 :
                    birthdays.append({"name": name, "birthday":date_user.strftime("%d.%m.%Y")})
                else:
                    if difference_day == 7:
                        birthdays.append({"name": name, "birthday":(date_user + dt.timedelta(days = 1)).strftime("%d.%m.%Y")})
                    elif difference_day == 6:
                        birthdays.append({"name": name, "birthday":(date_user + dt.timedelta(days = 2)).strftime("%d.%m.%Y")})
        for birthday in birthdays:
            print(f"{birthday.get("name")}, {birthday.get("birthday")}")
        return "birthdays"

def parse_input(user_input):
    name, *args = user_input.split()
    name = name.strip().lower()
    return name, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."  
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    name_phone = book.find(name)
    name_phone.edit_phone(old_phone, new_phone)
    message = "Number changed."
    return message

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    return book.find(name)

# @input_error
# def show_all(book: AddressBook):  
#     return book.all()
    # message = "contact list"
    # return message

def delete(args, book: AddressBook):
    name, *_ = args
    book.delete(name)
    message = "Contact delete."
    return message

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    message = "Date of birth updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Date of birth added."
    record.add_birthday(birthday)
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    return book.find_birthday(name)

# @input_error
# def birthdays(book: AddressBook):
#     return book.get_upcoming_birthdays()

class AbstractBot(ABC):
    def return_all_users(self):
        raise NotImplementedError()
    
    def return_help(self):
        raise NotImplementedError()
    
class SimpleBot(AbstractBot):

    def return_all_users(self, addressbook: AddressBook):
        self.addressbook = addressbook
        return self.addressbook.all()
    
    def return_help(self, commands):
        print("Available commands:")
        for command in commands:
            print(f"- {command}")

import pickle

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено
    
def main():
    view = SimpleBot()
    book = load_data()
    print("Welcome to the assistant bot!")
    view.return_all_users(load_data())
    view.return_help(["add name phone", "change name old phone new phone","phone name","delete name ","all","add_birthday name date","show name","birthdays"])
    while True:
        
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "delete":
            print(delete(args, book))
        elif command == "all":
            print(book.all())
            # print(show_all(book))
        elif command == "add_birthday":
            print(add_birthday(args, book))
        elif command == "show":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(book.get_upcoming_birthdays())
            # print(birthdays(book)) 
        else:
            print("Invalid command.")
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

if __name__ == "__main__":
    main()
    