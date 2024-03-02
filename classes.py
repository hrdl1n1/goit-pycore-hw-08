import pickle
from datetime import datetime, timedelta, date
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self._validate_phone(value):
            raise ValueError("Номер телефону має містити 10 цифр")
        super().__init__(value)

    def _validate_phone(self, value):
        return isinstance(value, str) and len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        if not self._validate_date(value):
            raise ValueError("Невірний формат дати. Використовуйте ДД.ММ.РРРР")
        super().__init__(value)

    def _validate_date(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False

    def get_date_object(self):
        return datetime.strptime(self.value, "%d.%m.%Y").date()

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        if not self.find_phone(old_phone):
            raise ValueError("Номер телефону для редагування не існує")
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        if self.birthday:
            raise ValueError("Дата народження вже існує для цього контакту")
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Ім'я контакту: {str(self.name)}, телефони: {'; '.join(str(p) for p in self.phones)}, дата народження: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_bdays = []

        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.get_date_object()
                bday_this_year = bday.replace(year=today.year)

                if bday_this_year < today:
                    bday = bday.replace(year=today.year + 1)
                else:
                    bday = bday_this_year

                days_until_bday = (bday - today).days

                if 0 <= days_until_bday <= 7:
                    if bday.weekday() >= 5:
                        days_until_monday = (7 - bday.weekday())
                        bday += timedelta(days_until_monday)

                    upcoming_bdays.append({
                        "name": record.name.value,
                        "congratulation_date": bday.strftime("%Y.%m.%d")
                    })

        return upcoming_bdays
    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
