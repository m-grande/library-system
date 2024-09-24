import re
from .db_connection import connect_to_db
from tabulate import tabulate


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
        print(f"\nTotal number of borrowers: {len(borrowers)}\n")
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
        print(f"\nNo borrowers found matching the keyword: '{keyword}'\n")

    cur.close()
    conn.close()


def add_borrower(name, email, phone):
    # Insert a new borrower into the borrowers table, checking for correct input types and duplicates, and display the added borrower
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = %s OR phone = %s", (email, phone))
    duplicate = cur.fetchone()

    if duplicate:
        print(f"\nError: A borrower with email '{email}' or phone '{phone}' already exists. Please use different data.\n")
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
            print(f"\nBorrower '{borrower[1]}' cannot be removed because they have {books_borrowed} book(s) currently borrowed.\n")
        else:
            headers = ["Borrower ID", "Name", "Email", "Phone"]
            borrower_table = [borrower]

            print(tabulate(borrower_table, headers, tablefmt="fancy_grid"))

            while True:
                confirmation = input("Are you sure you want to remove this borrower (yes/no)? ").strip().lower()
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
    # Modify a borrower's details by showing existing 
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
            print("\nEnter the data you want to change, leave blank for no change.\n")

            new_name = input(f"Enter new name (current: {borrower[1]}): ").strip() or borrower[1]
            if not new_name.replace(" ", "").isalpha(): 
                print("\nError: Name must contain only letters and spaces.\n")
                return
                        
            new_email = input(f"Enter new email (current: {borrower[2]}): ").strip() or borrower[2]
            email_pattern = r"[^@]+@[^@]+\.[^@]+"
            if not re.match(email_pattern, new_email):
                print("\nError: Invalid email format.\n")
                return
            
            new_phone = input(f"Enter new phone (current: {borrower[3]}): ").strip() or borrower[3]
            if not new_phone.isdigit():
                print("\nError: Phone number must contain only digits.\n")
                return

        
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