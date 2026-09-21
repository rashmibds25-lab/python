# Birthday Reminder

**Python Programming Lab (N-PCCCD304P) – Experiential Learning Utility**
Name: Rashmi Mahendra Borikar | ID: CD25034 | CSE (Data Science), Semester III
S. B. Jain Institute of Technology, Management & Research, Nagpur

## Utility Overview
A menu-based Python application that stores birthday details of friends,
family and employees and reminds the user about upcoming birthdays.

**Features**
- Add a birthday (name, date, category, optional phone)
- Update an existing record
- Search by name or category
- Delete a record (with confirmation)
- View all birthdays, nearest first
- Upcoming birthdays (next 30 days)
- Notifications for today and the next 7 days (shown automatically at start)
- Statistics (average age, people per category, busiest month)
- Data saved permanently in `birthdays.csv`; reminders logged in `reminder_log.txt`

## Installation
1. Install Python 3.8 or higher.
2. Install the libraries:
   ```
   pip install numpy pandas
   ```
3. Download this repository and run:
   ```
   python birthday_reminder.py
   ```

## Summary of Logic
1. On start, the program loads records from `birthdays.csv` (if present) using Pandas.
2. Each record is stored as a `Person` object (OOP); `BirthdayManager` keeps the list of people.
3. Dates are entered as `DD-MM-YYYY` and validated.
4. To find the next birthday, the birth date is moved to the current year; if it has already passed, it moves to next year. 29 Feb is handled in non-leap years.
5. Days left = next birthday − today. Sorting and filtering on this value gives the *upcoming* list and notifications.
6. Every change is saved immediately to the CSV file and written to the log file.

## Python Concepts Used
| Module | Concepts |
|---|---|
| 1 | Variables, input/output, if-elif-else, while/for loops |
| 2 | String, list, tuple (categories), set (unique months), dictionary (month count) |
| 3 | Functions with parameters and return values |
| 4 | NumPy (age statistics), Pandas (CSV read/write, value_counts) |
| 5 | File handling (CSV, text log), classes and objects |

## Sample Test Cases
| Input | Expected Result |
|---|---|
| Add "Asha", 15-03-2005, Friend | Added successfully |
| Add same name again | "This name already exists." |
| Date `31-02-2005` | "Invalid date" and asks again |
| Phone `123` | "Phone must be 10 digits" |
| Search `asha` | Shows Asha's record |
| Delete unknown name | "Person not found." |

## Files
- `birthday_reminder.py` – main program
- `birthdays.csv` – saved data (created automatically)
- `reminder_log.txt` – log file (created automatically)
- `Report.pdf` – consolidated report