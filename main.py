import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# File paths
DATA_DIR = "data"
BOOKS_FILE = os.path.join(DATA_DIR, "books.csv")
USERS_FILE = os.path.join(DATA_DIR, "users.csv")
LOGS_FILE = os.path.join(DATA_DIR, "logs.csv")

FINE_PER_DAY = 5  # ₹5 per day fine after 14 days

def ensure_files():
    """Ensure all required CSV files exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BOOKS_FILE):
        pd.DataFrame(columns=["BookID", "Title", "Author", "TotalCopies", "AvailableCopies"]).to_csv(BOOKS_FILE, index=False)
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["UserID", "Name", "BookID", "IssueDate", "ReturnDate"]).to_csv(USERS_FILE, index=False)
    if not os.path.exists(LOGS_FILE):
        pd.DataFrame(columns=["UserID", "BookID", "Action", "Date"]).to_csv(LOGS_FILE, index=False)

def load_data():
    """Load CSV data into DataFrames."""
    books = pd.read_csv(BOOKS_FILE)
    users = pd.read_csv(USERS_FILE, parse_dates=["IssueDate", "ReturnDate"])
    logs = pd.read_csv(LOGS_FILE, parse_dates=["Date"])
    return books, users, logs

def save_data(books, users, logs):
    """Save DataFrames back to CSV."""
    books.to_csv(BOOKS_FILE, index=False)
    users.to_csv(USERS_FILE, index=False)
    logs.to_csv(LOGS_FILE, index=False)

def add_book(books):
    print("\n--- Add New Book ---")
    book_id = input("Enter Book ID: ").strip()
    if book_id in books["BookID"].values:
        print("Book ID already exists.")
        return books
    title = input("Enter Title: ").strip()
    author = input("Enter Author: ").strip()
    try:
        copies = int(input("Enter Number of Copies: ").strip())
        if copies < 1:
            raise ValueError
    except ValueError:
        print("Invalid number of copies.")
        return books
    new_row = pd.DataFrame([[book_id, title, author, copies, copies]], columns=books.columns)
    books = pd.concat([books, new_row], ignore_index=True)
    print("Book added successfully.")
    return books

def issue_book(books, users, logs):
    print("\n--- Issue Book ---")
    user_id = input("Enter User ID: ").strip()
    name = input("Enter User Name: ").strip()
    book_id = input("Enter Book ID to Issue: ").strip()

    if book_id not in books["BookID"].values:
        print("Book not found.")
        return books, users, logs

    book_row = books[books["BookID"] == book_id].iloc[0]
    if book_row["AvailableCopies"] <= 0:
        print("No copies available.")
        return books, users, logs

    issue_date = pd.to_datetime(datetime.today())
    users = pd.concat([users, pd.DataFrame([[user_id, name, book_id, issue_date, pd.NaT]], columns=users.columns)], ignore_index=True)
    books.loc[books["BookID"] == book_id, "AvailableCopies"] -= 1
    logs = pd.concat([logs, pd.DataFrame([[user_id, book_id, "Issued", issue_date]], columns=logs.columns)], ignore_index=True)
    print("Book issued.")
    return books, users, logs

def return_book(books, users, logs):
    print("\n--- Return Book ---")
    user_id = input("Enter User ID: ").strip()
    book_id = input("Enter Book ID to Return: ").strip()

    mask = (users["UserID"] == user_id) & (users["BookID"] == book_id) & (users["ReturnDate"].isna())
    if not mask.any():
        print("No active issue found.")
        return books, users, logs

    today = pd.to_datetime(datetime.today())
    issue_date = users.loc[mask, "IssueDate"].iloc[0]
    return_days = (today - issue_date).days
    fine = max(0, (return_days - 14) * FINE_PER_DAY)

    users.loc[mask, "ReturnDate"] = today
    books.loc[books["BookID"] == book_id, "AvailableCopies"] += 1
    logs = pd.concat([logs, pd.DataFrame([[user_id, book_id, "Returned", today]], columns=logs.columns)], ignore_index=True)

    print("Book returned.")
    if fine > 0:
        print(f"Late return. Fine: ₹{fine}")
    return books, users, logs

def view_books(books):
    print("\n--- Book Inventory ---")
    print(books.to_string(index=False))

def visualize_top_books(users, books):
    print("\n--- Top 5 Most Borrowed Books ---")
    if users.empty:
        print("No borrowing records yet.")
        return
    top_books = users["BookID"].value_counts().nlargest(5)
    book_titles = books.set_index("BookID")["Title"]
    labels = [book_titles.get(bid, bid) for bid in top_books.index]
    plt.bar(labels, top_books.values, color='steelblue')
    plt.ylabel("Number of Borrows")
    plt.title("Most Borrowed Books")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def export_logs(logs):
    export_path = os.path.join(DATA_DIR, "user_logs_export.csv")
    logs.to_csv(export_path, index=False)
    print(f"Logs exported to {export_path}")

def main():
    ensure_files()
    books, users, logs = load_data()

    while True:
        print("\nLibrary Management Menu:")
        print("1. Add Book")
        print("2. Issue Book")
        print("3. Return Book")
        print("4. View Book Inventory")
        print("5. Show Top Borrowed Books")
        print("6. Export User Logs")
        print("7. Exit")

        choice = input("Enter choice: ").strip()
        if choice == "1":
            books = add_book(books)
        elif choice == "2":
            books, users, logs = issue_book(books, users, logs)
        elif choice == "3":
            books, users, logs = return_book(books, users, logs)
        elif choice == "4":
            view_books(books)
        elif choice == "5":
            visualize_top_books(users, books)
        elif choice == "6":
            export_logs(logs)
        elif choice == "7":
            save_data(books, users, logs)
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
