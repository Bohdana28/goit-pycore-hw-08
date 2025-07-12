from collections import UserDict
from datetime import datetime, timedelta, date
import pickle


def save_data(book, filename = "addressbook.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump(book, f)

def load_data(filename= "addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
             raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        self._validate(value)
        super().__init__(value)
    def _validate(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be exactly 10 digits")
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        raise ValueError("Old phone not found")
    
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        raise ValueError("Phone not found")
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        bday = f", Birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"{self.name.value}: {phones}{bday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    def find(self, name):
        return self.data.get(name)
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = date.today()
        next_week = today + timedelta(days= 7)
        result = []

        for record in  self.data.values():
            if record.birthday:
                bday = record.birthday.value
                bday_this_year = bday.replace(year = today.year)
                if today <= bday_this_year <= next_week:
                    result.append({"name": record.name.value, "congrats_date": bday_this_year.strftime("%d.%m.%Y")})
        return result                
        



def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "This contact was not found."
        except IndexError:
            return "Please enter a valid command." 

    return inner


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."
    

@input_error    
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    phones = "; ".join(p.value for p in record.phones)
    return f"{name}: {phones}"
   

def show_all(book):
    if not book.data:
        return "There are no contacts yet."
    
    result = []
    for record in book.data.values():
        result.append(str(record))
    return "\n".join(result)

@input_error
def delete_phone(args, book):
    name, phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.remove_phone(phone)
    return "Phone removed."

@input_error
def delete_contact(args, book):
    name = args[0]
    book.delete(name)
    return "Contact deleted."  

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    record.add_birthday(bday)
    return "Birthday added."  

@input_error
def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    result = []
    for entry in upcoming:
        result.append(f"{entry['name']} - {entry['congrats_date']}")
    return "\n".join(result)

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError("Contact not found.")
    if not record.birthday:
        return "Birthday not set for this contact."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m.%Y')}"

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
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
        elif command == "all":
            print(show_all(book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "remove-phone":
            print(delete_phone(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()