from db_connection import connect_to_db
from tabulate import tabulate


def list_books():
    # List all available books with ID, author, genre, published year, and availability ordered by book ID
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT books.book_id, books.title, authors.name AS author, genres.name AS genre, books.published_year,
               CASE
                   WHEN books.is_available = TRUE THEN 'Available'
                   ELSE 'Borrowed'
               END AS availability
        FROM books
        JOIN authors ON books.author_id = authors.author_id
        JOIN genres ON books.genre_id = genres.genre_id
        ORDER BY books.book_id ASC
        """
    )

    books = cur.fetchall()

    if books:
        headers = ["Book ID", "Title", "Author", "Genre", "Published Year", "Availability"]
        print(tabulate(books, headers, tablefmt="fancy_grid"))
    else:
        print("\nNo books are currently available.\n")

    cur.close()
    conn.close()


def search_books(keyword):
    # Search for books by title, author, genre, or published year using a single keyword and display results
    conn = connect_to_db()
    cur = conn.cursor()

    query = """
        SELECT books.book_id, books.title, authors.name AS author, genres.name AS genre, books.published_year,
               CASE
                   WHEN books.is_available = TRUE THEN 'Available'
                   ELSE 'Borrowed'
               END AS availability
        FROM books
        JOIN authors ON books.author_id = authors.author_id
        JOIN genres ON books.genre_id = genres.genre_id
        WHERE books.title ILIKE %s
           OR authors.name ILIKE %s
           OR genres.name ILIKE %s
           OR CAST(books.published_year AS TEXT) ILIKE %s
    """

    keyword_formatted = f"%{keyword}%"
    params = [keyword_formatted, keyword_formatted, keyword_formatted, keyword_formatted]

    cur.execute(query, params)
    books = cur.fetchall()

    if books:
        headers = ["Book ID", "Title", "Author", "Genre", "Published Year", "Availability"]
        print(tabulate(books, headers, tablefmt="fancy_grid"))
        print(f"\nTotal number of books found: {len(books)}\n")
    else:
        print("\nNo books found matching the search criteria.\n")

    cur.close()
    conn.close()


def add_book(title, author_id, genre_id, published_year):
    # Insert a new book into the books table and display the added book, checking for correct input types

    if not title or not author_id or not genre_id or not published_year:
        print("\nError: All fields (title, author, genre, published year) are required.\n")
        return

    if not isinstance(title, str):
        print("\nError: Title must be a string.\n")
        return

    if (
        not isinstance(author_id, int)
        or not isinstance(genre_id, int)
        or not isinstance(published_year, int)
    ):
        print("\nError: Author ID, Genre ID, and Published Year must be integers.\n")
        return

    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO books (title, author_id, genre_id, published_year, is_available)
        VALUES (%s, %s, %s, %s, TRUE)
        RETURNING book_id
        """,
        (title, author_id, genre_id, published_year),
    )

    book_id = cur.fetchone()[0]
    conn.commit()

    cur.execute(
        """
        SELECT books.book_id, books.title, authors.name AS author, genres.name AS genre, books.published_year
        FROM books
        JOIN authors ON books.author_id = authors.author_id
        JOIN genres ON books.genre_id = genres.genre_id
        WHERE books.book_id = %s
        """,
        (book_id,),
    )

    added_book = cur.fetchall()

    headers = ["Book ID", "Title", "Author", "Genre", "Published Year"]
    print(tabulate(added_book, headers, tablefmt="fancy_grid"))

    print(f"\nBook '{title}' added successfully.\n")

    cur.close()
    conn.close()


def remove_book(book_id):
    try:
        book_id = int(book_id)
    except ValueError:
        print("\nInvalid input. The book ID must be an integer.\n")
        return

    # Remove a book from the books table after confirming
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT book_id, title, author_id, genre_id, published_year FROM books WHERE book_id = %s",
        (book_id,),
    )
    book = cur.fetchone()

    if book:
        headers = ["Book ID", "Title", "Author ID", "Genre ID", "Published Year"]
        book_table = [book]

        print(tabulate(book_table, headers, tablefmt="fancy_grid"))

        while True:
            confirmation = (
                input("Are you sure you want to remove this book (yes/no)? ").strip().lower()
            )
            if confirmation in ["yes", "no"]:
                break
            else:
                print("\nPlease enter 'yes' or 'no'.")

        if confirmation == "yes":
            cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
            conn.commit()
            print(f"\nBook with ID {book_id} removed successfully.\n")
        else:
            print("\nOperation cancelled.\n")
    else:
        print(f"\nNo book found with ID: {book_id}\n")

    cur.close()
    conn.close()


def modify_book(book_id):
    try:
        book_id = int(book_id)
    except ValueError:
        print("\nInvalid input. The book ID must be an integer.\n")
        return

    # Modify the details of a specific book, changing only the values provided by the user
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT books.book_id, books.title, authors.author_id, authors.name AS author, genres.genre_id, genres.name AS genre, books.published_year
        FROM books
        JOIN authors ON books.author_id = authors.author_id
        JOIN genres ON books.genre_id = genres.genre_id
        WHERE books.book_id = %s
    """,
        (book_id,),
    )
    book = cur.fetchone()

    if book:
        headers = ["Book ID", "Title", "Author", "Genre", "Published Year"]
        print(
            tabulate(
                [(book[0], book[1], book[3], book[5], book[6])], headers, tablefmt="fancy_grid"
            )
        )

        while True:
            confirm = input("Do you want to modify this book? (yes/no): ").strip().lower()
            if confirm in ["yes", "no"]:
                break
            else:
                print("\nPlease enter 'yes' or 'no'.")

        if confirm == "yes":
            print("\nEnter the data you want to modify\n")
            new_title = input(f"Enter new title: ").strip() or book[1]
            new_author_id = input(f"Enter new author ID: ").strip() or book[2]
            new_genre_id = input(f"Enter new genre ID: ").strip() or book[4]
            new_published_year = input(f"Enter new published year: ").strip() or book[6]

            cur.execute(
                """
                UPDATE books
                SET title = %s, author_id = %s, genre_id = %s, published_year = %s
                WHERE book_id = %s
            """,
                (new_title, new_author_id, new_genre_id, new_published_year, book_id),
            )
            conn.commit()

            print("\nBook updated successfully.\n")
        else:
            print("\nModification cancelled.\n")
    else:
        print("\nBook not found.\n")

    cur.close()
    conn.close()
