from collections import UserDict
from datetime import datetime, timedelta

# ------------------- Field -------------------
class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# ------------------- Record -------------------
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old, new):
        for i, p in enumerate(self.phones):
            if p.value == old:
                self.phones[i] = Phone(new)
                return True
        return False

    def add_birthday(self, bday):
        self.birthday = Birthday(bday)

# ------------------- AddressBook -------------------
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if today <= bday_this_year <= today + timedelta(days=7):
                    greet_day = bday_this_year
                    if greet_day.weekday() >= 5:  # Если суббота или воскресенье
                        greet_day += timedelta(days=(7 - greet_day.weekday()))
                    upcoming.append({"name": record.name.value, "birthday": greet_day.strftime("%d.%m.%Y")})
        return upcoming

# ------------------- Error decorator -------------------
def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except (IndexError, ValueError) as e:
            return f"Error: {str(e)}"
    return wrapper

# ------------------- Хендлери команд -------------------
@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.edit_phone(old_phone, new_phone):
        return "Phone updated."
    return "Contact or phone not found."

@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join([p.value for p in record.phones])
    return "Contact not found."

def show_all(book):
    result = []
    for record in book.data.values():
        phones = ", ".join([p.value for p in record.phones])
        bday = f", birthday: {record.birthday.value}" if record.birthday else ""
        result.append(f"{record.name.value}: {phones}{bday}")
    return "\n".join(result) if result else "Address book is empty."

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.add_birthday(bday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    return "Birthday not set or contact not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join([f"{p['name']}: {p['birthday']}" for p in upcoming])

# ------------------- Командний парсер -------------------
def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0].lower(), parts[1:]

# ------------------- Показать список команд -------------------
def print_commands():
    print("\nДобро пожаловать в помощника!")
    print("Доступные команды:")
    print(" add [имя] [телефон]           - Добавить контакт или телефон")
    print(" change [имя] [старый] [новый] - Изменить номер телефона")
    print(" phone [имя]                   - Показать телефоны контакта")
    print(" all                           - Показать все контакты")
    print(" add-birthday [имя] [дата]    - Добавить день рождения (ДД.MM.ГГГГ)")
    print(" show-birthday [имя]           - Показать день рождения контакта")
    print(" birthdays                    - Показать дни рождения на ближайшие 7 дней")
    print(" hello                        - Приветствие от бота")
    print(" close / exit                 - Выйти из программы\n")

# ------------------- Основна логіка -------------------
def main():
    print_commands()
    book = AddressBook()
    while True:
        user_input = input("Введите команду: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("До свидания!")
            break

        elif command == "hello":
            print("Привет! Чем могу помочь?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Неверная команда. Введите 'hello' для помощи.")

if __name__ == '__main__':
    main()
