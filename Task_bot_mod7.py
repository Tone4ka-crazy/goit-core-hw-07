from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            value = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def edit_phone(self, old_phone, new_phone):
        old_phone = self.find_phone(old_phone)
        if not old_phone:
            raise ValueError("Phone not found")
        new_phone_obj = Phone(new_phone)
        old_phone.value = new_phone_obj.value

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_this_year = record.birthday.value.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                congratulation_date = birthday_this_year
                weekday = congratulation_date.weekday()
                if weekday == 5:
                    congratulation_date += timedelta(days=2)
                elif weekday == 6:
                    congratulation_date += timedelta(days=1)

                congratulation_date_str = congratulation_date.strftime("%d.%m.%Y")
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "birthday": congratulation_date_str
                })
        return upcoming_birthdays

    def __str__(self):
        lines = []
        for record in self.data.values():
            lines.append(str(record))
        return "\n".join(lines)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return str(ve) if str(ve) else "Enter correct data"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter all required arguments for this command."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated"
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added"
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contacts(args, book:AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact changed."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book:AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.phones:
            phones_str = ";".join(phone.value for phone in record.phones)
            return f"{record.name.value}'s phone(s): {phones_str}"
        else:
            return f"{record.name.value} has no saved phones."
    else:
        return "Contact not found."


@input_error
def show_all(book:AddressBook):
    if not book:
        return "No contacts found."
    lines = []
    for record in book.values():
        phones_str = "; ".join(p.value for p in record.phones) if record.phones else "no phones"
        birthday_str = f", birthday: {record.birthday}" if record.birthday else "N/A"
        lines.append(f"{record.name.value}: {phones_str},{birthday_str}")
    return "\n".join(lines)

@input_error
def add_birthday(args, book:AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    else:
        record.add_birthday(birthday)
        return "Birthday added."

@input_error
def show_birthday(args, book:AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return f"{record.name.value}'s birthday: {record.birthday}"
        else:
            return f"{record.name.value} has no saved birthdays."
    else:
        return "Contact not found."

@input_error
def birthdays(args, book:AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays(7)
    if upcoming_birthdays:
        return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming_birthdays)
    else:
        return "No upcoming birthdays."

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contacts(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()