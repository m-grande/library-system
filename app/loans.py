from .db_connection import connect_to_db
from tabulate import tabulate
from datetime import datetime

def view_loans():
    # Fetch and display all loans with borrower and book details
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT loans.loan_id, books.title, borrowers.name, loans.loan_date, loans.return_date
        FROM loans
        JOIN books ON loans.book_id = books.book_id
        JOIN borrowers ON loans.borrower_id = borrowers.borrower_id
        ORDER BY loans.loan_date DESC
        """
    )

    loans = cur.fetchall()

    if loans:
        headers = ["Loan ID", "Book Title", "Borrower", "Loan Date", "Return Date"]
        print(tabulate(loans, headers, tablefmt="fancy_grid"))
        print(f"\nTotal number of loans: {len(loans)}\n")
    else:
        print("\nNo loans found.\n")

    cur.close()
    conn.close()


def search_loan(keyword):
    # Search for a loan by book title or borrower name using a single keyword
    conn = connect_to_db()
    cur = conn.cursor()

    query = """
        SELECT loans.loan_id, books.title, borrowers.name, loans.loan_date, loans.return_date
        FROM loans
        JOIN books ON loans.book_id = books.book_id
        JOIN borrowers ON loans.borrower_id = borrowers.borrower_id
        WHERE books.title ILIKE %s
           OR borrowers.name ILIKE %s
        """

    keyword_formatted = f"%{keyword}%"
    params = [keyword_formatted, keyword_formatted]

    cur.execute(query, params)
    loans = cur.fetchall()

    if loans:
        headers = ["Loan ID", "Book Title", "Borrower", "Loan Date", "Return Date"]
        print(tabulate(loans, headers, tablefmt="fancy_grid"))
        print(f"\nTotal number of loans found: {len(loans)}\n")
    else:
        print(f"\nNo loans found matching the keyword: '{keyword}'\n")

    cur.close()
    conn.close()


def borrow_book(book_id, borrower_id):
    # Borrow a book and create a loan record, ensuring that the book is available
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT title FROM books WHERE book_id = %s", (book_id,))
    book_exists = cur.fetchone()

    cur.execute("SELECT name FROM borrowers WHERE borrower_id = %s", (borrower_id,))
    borrower_exists = cur.fetchone()

    if not book_exists:
        print("\nError: Invalid book ID. This book does not exist.\n")
    elif not borrower_exists:
        print("\nError: Invalid borrower ID. This borrower does not exist.\n")
    else:
        cur.execute(
            "SELECT title FROM books WHERE book_id = %s AND is_available = TRUE", (book_id,)
        )
        book = cur.fetchone()

        if not book:
            print("\nError: This book is not available for borrowing.\n")
        else:
            title = book[0]

            cur.execute(
                """
                INSERT INTO loans (book_id, borrower_id, loan_date)
                VALUES (%s, %s, CURRENT_DATE)
                RETURNING loan_id, loan_date
                """,
                (book_id, borrower_id),
            )

            loan_id, loan_date = cur.fetchone()

            cur.execute("UPDATE books SET is_available = FALSE WHERE book_id = %s", (book_id,))
            conn.commit()

            borrower = borrower_exists[0]

            headers = ["Loan ID", "Title", "Borrower", "Loan Date", "Return Date"]
            loan_details = [(loan_id, title, borrower, loan_date, "")]
            print(tabulate(loan_details, headers, tablefmt="fancy_grid"))

            print(f"\nLoan ID {loan_id}: Book '{title}' borrowed successfully by {borrower}.\n")

    cur.close()
    conn.close()


def return_book(loan_id):
    # Return a book and update the loan record
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT loans.book_id, books.title, borrowers.name, loans.loan_date
        FROM loans
        JOIN books ON loans.book_id = books.book_id
        JOIN borrowers ON loans.borrower_id = borrowers.borrower_id
        WHERE loans.loan_id = %s AND loans.return_date IS NULL
        """,
        (loan_id,),
    )
    loan = cur.fetchone()

    if not loan:
        print("\nError: No active loan found with the provided loan ID.\n")
    else:
        book_id, title, borrower, loan_date = loan

        cur.execute("UPDATE loans SET return_date = CURRENT_DATE WHERE loan_id = %s", (loan_id,))
        cur.execute("UPDATE books SET is_available = TRUE WHERE book_id = %s", (book_id,))
        conn.commit()

        cur.execute("SELECT return_date FROM loans WHERE loan_id = %s", (loan_id,))
        return_date = cur.fetchone()[0]

        headers = ["Loan ID", "Title", "Borrower", "Loan Date", "Return Date"]
        loan_details = [(loan_id, title, borrower, loan_date, return_date)]
        print(tabulate(loan_details, headers, tablefmt="fancy_grid"))

        print(f"\nLoan ID {loan_id}: Book '{title}' returned successfully.\n")

    cur.close()
    conn.close()


def modify_loan(loan_id):
    # Modify loan details, ensuring return date is not earlier than loan date and only if the loan has been returned
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT loans.loan_id, books.title, borrowers.name, loans.loan_date, loans.return_date
        FROM loans
        JOIN books ON loans.book_id = books.book_id
        JOIN borrowers ON loans.borrower_id = borrowers.borrower_id
        WHERE loans.loan_id = %s
        """,
        (loan_id,),
    )
    loan = cur.fetchone()

    if loan:
        loan_id, book_title, borrower_name, loan_date, return_date = loan
        headers = ["Loan ID", "Book Title", "Borrower", "Loan Date", "Return Date"]
        print(tabulate([loan], headers, tablefmt="fancy_grid"))

        if return_date is None:
            print("\nError: This loan has not been returned yet. Modification is not allowed.\n")
        else:
            while True:
                confirm = input("Do you want to modify this loan's return date? (yes/no): ").strip().lower()
                if confirm in ["yes", "no"]:
                    break
                else:
                    print("\nPlease enter 'yes' or 'no'.")

            if confirm == "yes":
                while True:
                    new_return_date = input(f"\nEnter new return date in the format YYYY-MM-DD (current: {return_date}): ").strip()

                    # Validate if the input is a date in the correct format
                    try:
                        datetime.strptime(new_return_date, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("\nError: Please enter a valid date in the format YYYY-MM-DD.")

                # Ensure the new return date is not earlier than the loan date
                if new_return_date >= str(loan_date):
                    cur.execute(
                        """
                        UPDATE loans
                        SET return_date = %s
                        WHERE loan_id = %s
                        """,
                        (new_return_date, loan_id),
                    )
                    conn.commit()
                    print("\nLoan return date updated successfully.\n")
                else:
                    print("\nError: The return date cannot be earlier than the loan date.\n")
            else:
                print("\nModification cancelled.\n")
    else:
        print(f"\nLoan not found with ID: {loan_id}\n")

    cur.close()
    conn.close()
