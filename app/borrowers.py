from db_connection import connect_to_db
from tabulate import tabulate
import re


def view_borrowers():
    # Fetch and display all borrowers with their details, including Borrower ID and number of books borrowed
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT borrowers.borrower_id, borrowers.name, borrowers.email, borrowers.phone,
               COUNT(loans.book_id) AS books_borrowed
        FROM borrowers
        LEFT JOIN loans ON borrowers.borrower_id = loans.borrower_id
        GROUP BY borrowers.borrower_id
        ORDER BY borrowers.borrower_id
    """
    )

    borrowers = cur.fetchall()

    if borrowers:
        headers = ["Borrower ID", "Name", "Email", "Phone", "Books Borrowed"]
        print(tabulate(borrowers, headers, tablefmt="fancy_grid"))
    else:
        print("\nNo borrowers found.\n")

    cur.close()
    conn.close()


def search_borrowers(keyword):
    # Search for borrowers by name, email, or phone using a single keyword and display all details, including books borrowed

    conn = connect_to_db()
    cur = conn.cursor()

    query = """
        SELECT borrowers.borrower_id, borrowers.name, borrowers.email, borrowers.phone,
               COUNT(loans.book_id) AS books_borrowed
        FROM borrowers
        LEFT JOIN loans ON borrowers.borrower_id = loans.borrower_id
        WHERE borrowers.name ILIKE %s
           OR borrowers.email ILIKE %s
           OR borrowers.phone ILIKE %s
        GROUP BY borrowers.borrower_id
        ORDER BY borrowers.borrower_id
    """

    keyword_formatted = f"%{keyword}%"
    params = [keyword_formatted, keyword_formatted, keyword_formatted]

    cur.execute(query, params)
    borrowers = cur.fetchall()

    if borrowers:
        headers = ["Borrower ID", "Name", "Email", "Phone", "Books Borrowed"]

        print(tabulate(borrowers, headers, tablefmt="fancy_grid"))
        print(f"\nTotal number of borrowers found: {len(borrowers)}\n")
    else:
        print("\nNo borrowers found matching the search criteria.\n")

    cur.close()
    conn.close()


def add_borrower(name, email, phone):
    # Insert a new borrower into the borrowers table, checking for correct input types and duplicates, and display the added borrower

    if not name or not email or not phone:
        print("\nError: All fields (name, email, phone) are required.\n")
        return

    if not name.isalpha():
        print("\nError: Name must contain only letters.\n")
        return

    email_pattern = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_pattern, email):
        print("\nError: Invalid email format.\n")
        return

    if not phone.isdigit():
        print("\nError: Phone number must contain only digits.\n")
        return

    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = %s OR phone = %s", (email, phone))
    duplicate = cur.fetchone()

    if duplicate:
        print(
            f"\nError: A borrower with email '{email}' or phone '{phone}' already exists. Please use different data.\n"
        )
    else:
        cur.execute(
            """
            INSERT INTO borrowers (name, email, phone)
            VALUES (%s, %s, %s)
            RETURNING borrower_id
            """,
            (name, email, phone),
        )

        borrower_id = cur.fetchone()[0]
        conn.commit()

        cur.execute(
            """
            SELECT borrower_id, name, email, phone
            FROM borrowers
            WHERE borrower_id = %s
            """,
            (borrower_id,),
        )

        added_borrower = cur.fetchall()

        headers = ["Borrower ID", "Name", "Email", "Phone"]
        print(tabulate(added_borrower, headers, tablefmt="fancy_grid"))

        print(f"\nBorrower '{name}' added successfully.\n")

    cur.close()
    conn.close()


def remove_borrower_by_id(borrower_id):
    # Remove a borrower by ID after confirming with the user
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT borrower_id, name, email, phone FROM borrowers WHERE borrower_id = %s",
        (borrower_id,),
    )
    borrower = cur.fetchone()

    if borrower:
        cur.execute(
            "SELECT COUNT(*) FROM loans WHERE borrower_id = %s AND return_date IS NULL",
            (borrower_id,),
        )
        books_borrowed = cur.fetchone()[0]

        if books_borrowed > 0:
            print(
                f"\nBorrower '{borrower[1]}' cannot be removed because has {books_borrowed} book(s) currently borrowed.\n"
            )
        else:
            headers = ["Borrower ID", "Name", "Email", "Phone"]
            borrower_table = [borrower]

            print(tabulate(borrower_table, headers, tablefmt="fancy_grid"))

            while True:
                confirmation = (
                    input("Are you sure you want to remove this borrower (yes/no)? ")
                    .strip()
                    .lower()
                )
                if confirmation in ["yes", "no"]:
                    break
                else:
                    print("\nPlease enter 'yes' or 'no'.")

            if confirmation == "yes":
                cur.execute("DELETE FROM borrowers WHERE borrower_id = %s", (borrower_id,))
                conn.commit()
                print(f"\nBorrower '{borrower[1]}' removed successfully.\n")
            else:
                print("\nOperation cancelled.\n")
    else:
        print(f"\nNo borrower found with ID: {borrower_id}\n")

    cur.close()
    conn.close()


def modify_borrower(borrower_id):
    try:
        borrower_id = int(borrower_id)
    except ValueError:
        print("\nError: Borrower ID must be an integer.\n")
        return

    # Modify the details of a specific borrower, changing only the values provided by the user
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT borrower_id, name, email, phone FROM borrowers WHERE borrower_id = %s",
        (borrower_id,),
    )
    borrower = cur.fetchone()

    if borrower:
        headers = ["Borrower ID", "Name", "Email", "Phone"]
        print(tabulate([borrower], headers, tablefmt="fancy_grid"))

        while True:
            confirm = input("Do you want to modify this borrower? (yes/no): ").strip().lower()
            if confirm in ["yes", "no"]:
                break
            else:
                print("\nPlease enter 'yes' or 'no'.")

        if confirm == "yes":
            new_name = input(f"\nEnter new name (current: {borrower[1]}): ").strip() or borrower[1]
            new_email = input(f"Enter new email (current: {borrower[2]}): ").strip() or borrower[2]
            new_phone = input(f"Enter new phone (current: {borrower[3]}): ").strip() or borrower[3]

            cur.execute(
                """
                UPDATE borrowers
                SET name = %s, email = %s, phone = %s
                WHERE borrower_id = %s
                """,
                (new_name, new_email, new_phone, borrower_id),
            )
            conn.commit()

            print("\nBorrower updated successfully.\n")
        else:
            print("\nModification cancelled.\n")
    else:
        print("\nBorrower not found.\n")

    cur.close()
    conn.close()
