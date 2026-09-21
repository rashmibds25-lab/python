"""
Birthday Reminder
-----------------
Python Programming Lab (N-PCCCD304P) - Experiential Learning Utility

Stores birthdays of friends, family and employees and reminds the user
about upcoming birthdays. Supports: add, update, search, delete, view,
upcoming birthdays, today's notification and simple statistics.

Concepts used (matches the 5 syllabus modules):
  Module 1 - variables, input/output, if/elif/else, while and for loops
  Module 2 - string, list, tuple, set, dictionary
  Module 3 - functions with parameters and return values
  Module 4 - NumPy and Pandas
  Module 5 - file handling (CSV + text log) and OOP (classes)
"""

from datetime import date, datetime

import numpy as np
import pandas as pd

# ---------------------------------------------------------------
# Constants
# ---------------------------------------------------------------
DATA_FILE = "birthdays.csv"          # where birthdays are saved
LOG_FILE = "reminder_log.txt"        # where reminders are logged
COLUMNS = ["Name", "Birthday", "Category", "Phone"]   # list
CATEGORIES = ("Friend", "Family", "Employee")         # tuple (cannot change)
DATE_FORMAT = "%d-%m-%Y"                              # e.g. 25-12-2005


# ---------------------------------------------------------------
# MODULE 3 - Helper functions
# ---------------------------------------------------------------
def parse_date(text):
    """Convert 'DD-MM-YYYY' text into a date. Returns None if invalid."""
    try:
        parsed = datetime.strptime(text.strip(), DATE_FORMAT).date()
    except ValueError:
        return None
    if parsed > date.today():        # birthday cannot be in the future
        return None
    return parsed


def next_birthday(birth_date, today=None):
    """Return the date of the next birthday (today counts)."""
    if today is None:
        today = date.today()
    year = today.year
    while True:
        try:
            candidate = birth_date.replace(year=year)
        except ValueError:           # 29 Feb in a non-leap year
            candidate = date(year, 2, 28)
        if candidate >= today:
            return candidate
        year += 1


def days_until(birth_date, today=None):
    """How many days are left for the next birthday."""
    if today is None:
        today = date.today()
    return (next_birthday(birth_date, today) - today).days


def age_turning(birth_date, today=None):
    """Age the person will turn on the next birthday."""
    if today is None:
        today = date.today()
    return next_birthday(birth_date, today).year - birth_date.year


def ask_category():
    """Ask the user to choose a category using a loop."""
    while True:
        print("Category:")
        for number, name in enumerate(CATEGORIES, start=1):
            print(f"  {number}. {name}")
        choice = input("Choose 1-3: ").strip()
        if choice in ("1", "2", "3"):
            return CATEGORIES[int(choice) - 1]
        print("Invalid choice. Try again.\n")


def ask_date(prompt):
    """Keep asking until a valid date is entered."""
    while True:
        value = parse_date(input(prompt))
        if value is not None:
            return value
        print("Invalid date. Use DD-MM-YYYY (past date), e.g. 25-12-2005.")


def is_valid_phone(phone):
    """Phone is optional. If given it must be 10 digits."""
    return phone == "" or (phone.isdigit() and len(phone) == 10)


def write_log(message):
    """MODULE 5 - append a line to the log file with time stamp."""
    stamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{stamp}] {message}\n")


# ---------------------------------------------------------------
# MODULE 5 - OOP : classes
# ---------------------------------------------------------------
class Person:
    """One person and his/her birthday."""

    def __init__(self, name, birth_date, category, phone=""):
        self.name = name
        self.birth_date = birth_date
        self.category = category
        self.phone = phone

    def to_dict(self):
        """Dictionary form, used while saving to CSV."""
        return {
            "Name": self.name,
            "Birthday": self.birth_date.strftime(DATE_FORMAT),
            "Category": self.category,
            "Phone": self.phone,
        }

    def __str__(self):
        phone = self.phone if self.phone else "-"
        return (f"{self.name:<18} {self.birth_date.strftime(DATE_FORMAT)}  "
                f"{self.category:<9} {phone}")


class BirthdayManager:
    """Keeps all birthdays and does add/update/search/delete etc."""

    def __init__(self):
        self.people = []             # list of Person objects
        self.load()

    # ---------- file handling with pandas (Module 4 + 5) ----------
    def load(self):
        """Read birthdays from the CSV file (if it exists)."""
        try:
            data = pd.read_csv(DATA_FILE, dtype=str).fillna("")
        except FileNotFoundError:
            return                   # first run: no file yet
        except pd.errors.EmptyDataError:
            return
        for _, row in data.iterrows():
            birth = parse_date(row["Birthday"])
            if birth is not None:
                self.people.append(
                    Person(row["Name"], birth, row["Category"], row["Phone"]))

    def save(self):
        """Write all birthdays to the CSV file."""
        rows = [person.to_dict() for person in self.people]
        pd.DataFrame(rows, columns=COLUMNS).to_csv(DATA_FILE, index=False)

    # ---------- helpers ----------
    def find_exact(self, name):
        """Return the Person with this exact name (ignore case) or None."""
        for person in self.people:
            if person.name.lower() == name.strip().lower():
                return person
        return None

    # ---------- 1. Add ----------
    def add_person(self, name, birth_date, category, phone=""):
        name = name.strip()
        if name == "":
            return False, "Name cannot be empty."
        if self.find_exact(name) is not None:
            return False, "This name already exists."
        if not is_valid_phone(phone):
            return False, "Phone must be 10 digits (or leave empty)."
        self.people.append(Person(name, birth_date, category, phone))
        self.save()
        write_log(f"Added {name}")
        return True, f"{name} added successfully."

    # ---------- 2. Update ----------
    def update_person(self, name, new_name=None, new_date=None,
                      new_category=None, new_phone=None):
        person = self.find_exact(name)
        if person is None:
            return False, "Person not found."
        if new_name:
            other = self.find_exact(new_name)
            if other is not None and other is not person:
                return False, "That new name already exists."
            person.name = new_name.strip()
        if new_date:
            person.birth_date = new_date
        if new_category:
            person.category = new_category
        if new_phone is not None:
            if not is_valid_phone(new_phone):
                return False, "Phone must be 10 digits (or leave empty)."
            person.phone = new_phone
        self.save()
        write_log(f"Updated {name}")
        return True, "Record updated."

    # ---------- 3. Search ----------
    def search(self, keyword):
        """Search by part of name OR by category. Returns a list."""
        keyword = keyword.strip().lower()
        return [p for p in self.people
                if keyword in p.name.lower() or keyword == p.category.lower()]

    # ---------- 4. Delete ----------
    def delete_person(self, name):
        person = self.find_exact(name)
        if person is None:
            return False, "Person not found."
        self.people.remove(person)
        self.save()
        write_log(f"Deleted {name}")
        return True, f"{person.name} deleted."

    # ---------- 5. View all ----------
    def sorted_by_upcoming(self):
        """People sorted by who has the nearest birthday."""
        return sorted(self.people, key=lambda p: days_until(p.birth_date))

    # ---------- 6. Upcoming ----------
    def upcoming(self, days=30):
        """People whose birthday comes within the next `days` days."""
        return [p for p in self.sorted_by_upcoming()
                if days_until(p.birth_date) <= days]

    # ---------- 7. Notify ----------
    def notify(self):
        """Show today's birthdays and birthdays in next 7 days."""
        today_list = [p for p in self.people if days_until(p.birth_date) == 0]
        soon_list = [p for p in self.upcoming(7) if days_until(p.birth_date) > 0]

        print("\n*** BIRTHDAY NOTIFICATIONS ***")
        if not today_list and not soon_list:
            print("No birthdays today or in the next 7 days.")
        for person in today_list:
            age = age_turning(person.birth_date)
            print(f"TODAY: It's {person.name}'s birthday! (turns {age})")
            write_log(f"Reminder: today is {person.name}'s birthday")
        for person in soon_list:
            left = days_until(person.birth_date)
            print(f"SOON : {person.name}'s birthday is in {left} day(s) "
                  f"on {next_birthday(person.birth_date).strftime('%d-%m-%Y')}")
            write_log(f"Reminder: {person.name} in {left} day(s)")

    # ---------- 8. Statistics (NumPy + Pandas + set + dict) ----------
    def statistics(self):
        if not self.people:
            print("No data for statistics.")
            return
        frame = pd.DataFrame([p.to_dict() for p in self.people])
        frame["Date"] = pd.to_datetime(frame["Birthday"], format=DATE_FORMAT)

        today = date.today()
        ages = np.array([today.year - p.birth_date.year -
                         ((today.month, today.day) <
                          (p.birth_date.month, p.birth_date.day))
                         for p in self.people])

        print("\n--- Statistics ---")
        print("Total records   :", len(self.people))
        print("Average age     :", round(float(np.mean(ages)), 1))
        print("Youngest / Oldest:", int(np.min(ages)), "/", int(np.max(ages)))

        print("\nPeople per category:")
        print(frame["Category"].value_counts().to_string())

        # dictionary: month name -> count
        month_count = {}
        for month in frame["Date"].dt.month_name():
            month_count[month] = month_count.get(month, 0) + 1
        busiest = max(month_count, key=month_count.get)
        print("\nBusiest birthday month:", busiest,
              f"({month_count[busiest]})")

        # set: unique months that have at least one birthday
        unique_months = set(frame["Date"].dt.month)
        print("Months with birthdays:", len(unique_months), "of 12")


# ---------------------------------------------------------------
# MODULE 1 - Menu / control structures
# ---------------------------------------------------------------
def print_table(people, title):
    """Print a list of Person objects as a small table."""
    print(f"\n{title}")
    if not people:
        print("  (nothing to show)")
        return
    print(f"{'Name':<18} {'Birthday':<11} {'Category':<9} Phone")
    print("-" * 50)
    for person in people:
        print(person)


def menu():
    print("\n========== BIRTHDAY REMINDER ==========")
    print("1. Add birthday")
    print("2. Update birthday")
    print("3. Search")
    print("4. Delete")
    print("5. View all (nearest first)")
    print("6. Upcoming birthdays (next 30 days)")
    print("7. Notifications (today / next 7 days)")
    print("8. Statistics")
    print("9. Exit")


def main():
    manager = BirthdayManager()
    manager.notify()                 # remind automatically at start

    while True:
        menu()
        choice = input("Enter your choice (1-9): ").strip()

        if choice == "1":
            name = input("Name: ")
            birth = ask_date("Birthday (DD-MM-YYYY): ")
            category = ask_category()
            phone = input("Phone (10 digits, optional): ").strip()
            print(manager.add_person(name, birth, category, phone)[1])

        elif choice == "2":
            name = input("Name of the person to update: ")
            if manager.find_exact(name) is None:
                print("Person not found.")
                continue
            print("Leave blank to keep the old value.")
            new_name = input("New name: ").strip()
            date_text = input("New birthday (DD-MM-YYYY): ").strip()
            new_date = None
            if date_text:
                new_date = parse_date(date_text)
                if new_date is None:
                    print("Invalid date. Update cancelled.")
                    continue
            change_cat = input("Change category? (y/n): ").strip().lower()
            new_cat = ask_category() if change_cat == "y" else None
            new_phone = input("New phone (blank = keep): ").strip()
            new_phone = new_phone if new_phone else None
            print(manager.update_person(name, new_name, new_date,
                                        new_cat, new_phone)[1])

        elif choice == "3":
            word = input("Enter name or category to search: ")
            print_table(manager.search(word), "Search results")

        elif choice == "4":
            name = input("Name to delete: ")
            sure = input(f"Delete '{name}'? (y/n): ").strip().lower()
            if sure == "y":
                print(manager.delete_person(name)[1])
            else:
                print("Cancelled.")

        elif choice == "5":
            print_table(manager.sorted_by_upcoming(), "All birthdays")

        elif choice == "6":
            print_table(manager.upcoming(30), "Birthdays in next 30 days")

        elif choice == "7":
            manager.notify()

        elif choice == "8":
            manager.statistics()

        elif choice == "9":
            print("Goodbye! Never miss a birthday.")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


if __name__ == "__main__":
    main()