from db_connection import connect_to_db
from tabulate import tabulate


def view_loans():
    # View all loans with borrower and book details
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
    else:
        print("\nNo loans found matching the search criteria.\n")

    cur.close()
    conn.close()


def borrow_book(book_id, borrower_id):
    try:
        book_id = int(book_id)
        borrower_id = int(borrower_id)
    except ValueError:
        print("\nError: Both Book ID and Borrower ID must be integers.\n")
        return

    # Borrow a book, create a loan record, and display the loan details, including error handling for invalid input.
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
    try:
        loan_id = int(loan_id)
    except ValueError:
        print("\nError: Loan ID must be an integer.\n")
        return

    # Return a book by loan ID, update the loan record, and display the loan details
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
    try:
        loan_id = int(loan_id)
    except ValueError:
        print("\nError: Loan ID must be an integer.\n")
        return

    # Modify the details of a specific loan, ensuring the return date is not earlier than the loan date
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
        headers = ["Loan ID", "Book Title", "Borrower", "Loan Date", "Return Date"]
        print(tabulate([loan], headers, tablefmt="fancy_grid"))

        while True:
            confirm = input("Do you want to modify this loan? (yes/no): ").strip().lower()
            if confirm in ["yes", "no"]:
                break
            else:
                print("\nPlease enter 'yes' or 'no'.")

        if confirm == "yes":
            new_return_date = input(f"\nEnter new return date (current: {loan[4]}): ").strip()

            if new_return_date:
                loan_date = loan[3]
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

                    print("\nLoan updated successfully.\n")
                else:
                    print("\nError: The return date cannot be earlier than the loan date.\n")
            else:
                print("\nNo changes made to the return date.\n")
        else:
            print("\nModification cancelled.\n")
    else:
        print("\nLoan not found.\n")

    cur.close()
    conn.close()
