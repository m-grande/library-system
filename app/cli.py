import inquirer
from books import add_book, list_books, modify_book, remove_book, search_books
from borrowers import (
    add_borrower,
    modify_borrower,
    remove_borrower_by_id,
    search_borrowers,
    view_borrowers,
)
from loans import borrow_book, modify_loan, return_book, search_loan, view_loans


def main_menu():
    questions = [
        inquirer.List(
            "action",
            message="What would you like to do?",
            choices=["Manage Books", "Manage Borrowers", "Manage Loans", "Exit"],
        ),
    ]
    answer = inquirer.prompt(questions)
    return answer["action"]


def manage_books():
    questions = [
        inquirer.List(
            "action",
            message="Book Management Options",
            choices=[
                "List books",
                "Search books",
                "Add a book",
                "Remove a book",
                "Modify a book",
                "Back to Main Menu",
            ],
        ),
    ]
    answer = inquirer.prompt(questions)
    return answer["action"]


def manage_borrowers():
    questions = [
        inquirer.List(
            "action",
            message="Borrower Management Options",
            choices=[
                "View borrowers",
                "Search borrowers",
                "Add a borrower",
                "Remove a borrower",
                "Modify a borrower",
                "Back to Main Menu",
            ],
        ),
    ]
    answer = inquirer.prompt(questions)
    return answer["action"]


def manage_loans():
    questions = [
        inquirer.List(
            "action",
            message="Loan Management Options",
            choices=[
                "View loans",
                "Search loans",
                "Borrow a book",
                "Return a book",
                "Modify a loan",
                "Back to Main Menu",
            ],
        ),
    ]
    answer = inquirer.prompt(questions)
    return answer["action"]


def search_books_interaction():
    keyword = input(
        "Enter a keyword to search for books (title, author, genre, or published year): "
    ).strip()

    if keyword:
        search_books(keyword)
    else:
        print("\nNo keyword entered. Please try again.\n")

# ----------->>>>>>>>>>>>>>>Controllare che gli input siano int<<<<<<<<<<<-----------
def add_book_interaction():
    title = input("Enter book title: ")
    author_id = input("Enter author ID: ")
    genre_id = input("Enter genre ID: ")
    published_year = input("Enter published year: ")

    add_book(title, author_id, genre_id, published_year)


def remove_book_interaction():
    book_id = input("Enter the book ID to remove: ")

    remove_book(book_id)


def modify_book_interaction():
    book_id = input("Enter the book ID to remove: ")

    modify_book(book_id)


def search_borrowers_interaction():
    keyword = input("Enter a keyword to search for borrowers (name, email, or phone): ").strip()

    if keyword:
        search_borrowers(keyword)
    else:
        print("\nNo keyword entered. Please try again.\n")


def add_borrower_interaction():
    name = input("Enter borrower's name: ")
    email = input("Enter borrower's email: ")
    phone = input("Enter borrower's phone number: ")

    add_borrower(name, email, phone)


def remove_borrower_interaction():
    id = input("Enter the borrower ID: ")

    remove_borrower_by_id(id)


def modify_borrower_interaction():
    id = input("Enter the borrower ID: ")

    modify_borrower(id)


def search_loans_interaction():
    keyword = input("Enter a keyword to search for loans (book title or borrower name): ").strip()

    if keyword:
        search_loan(keyword)
    else:
        print("\nNo keyword entered. Please try again.\n")


def borrow_book_interaction():
    book_id = input("Enter the book ID to borrow: ")
    borrower_id = input("Enter the borrower ID: ")

    borrow_book(book_id, borrower_id)


def return_book_interaction():
    loan_id = input("Enter the loan ID to return: ")

    return_book(loan_id)


def modify_loan_interaction():
    loan_id = input("Enter the loan ID to return: ")

    modify_loan(loan_id)


def run():
    while True:
        action = main_menu()

        if action == "Manage Books":
            while True:
                book_action = manage_books()
                if book_action == "List books":
                    list_books()
                elif book_action == "Search books":
                    search_books_interaction()
                elif book_action == "Add a book":
                    add_book_interaction()
                elif book_action == "Remove a book":
                    remove_book_interaction()
                elif book_action == "Modify a book":
                    modify_book_interaction()
                elif book_action == "Back to Main Menu":
                    break

        elif action == "Manage Borrowers":
            while True:
                borrower_action = manage_borrowers()
                if borrower_action == "View borrowers":
                    view_borrowers()
                elif borrower_action == "Search borrowers":
                    search_borrowers_interaction()
                elif borrower_action == "Add a borrower":
                    add_borrower_interaction()
                elif borrower_action == "Remove a borrower":
                    remove_borrower_interaction()
                elif borrower_action == "Modify a borrower":
                    modify_borrower_interaction()
                elif borrower_action == "Back to Main Menu":
                    break

        elif action == "Manage Loans":
            while True:
                loan_action = manage_loans()
                if loan_action == "View loans":
                    view_loans()
                elif loan_action == "Search loans":
                    search_loans_interaction()
                elif loan_action == "Borrow a book":
                    borrow_book_interaction()
                elif loan_action == "Return a book":
                    return_book_interaction()
                elif loan_action == "Modify a loan":
                    modify_loan_interaction()
                elif loan_action == "Back to Main Menu":
                    break

        elif action == "Exit":
            print("Thank you for using our library system!")
            break


if __name__ == "__main__":
    run()