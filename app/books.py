from .db_connection import connect_to_db
from tabulate import tabulate


def list_books():
    # Fetch and display all books with their details including Book ID, Title, Author, Genre, Published Year, and Availability
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
        print(f"\nTotal number of books: {len(books)}\n")
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
        print(f"\nNo books found matching the keyword: '{keyword}'\n")

    cur.close()
    conn.close()


def add_book(title, author_id, genre_id, published_year):
    # Insert a new book into the books table after verifying author_id and genre_id exist in the database
    conn = connect_to_db()
    cur = conn.cursor()

    # Check if author_id exists in the authors table
    cur.execute("SELECT author_id FROM authors WHERE author_id = %s", (author_id,))
    if not cur.fetchone():
        print(f"\nError: Author ID {author_id} does not exist. Book insertion cancelled.\n")
        cur.close()
        conn.close()
        return

    # Check if genre_id exists in the genres table
    cur.execute("SELECT genre_id FROM genres WHERE genre_id = %s", (genre_id,))
    if not cur.fetchone():
        print(f"\nError: Genre ID {genre_id} does not exist. Book insertion cancelled.\n")
        cur.close()
        conn.close()
        return

    # Insert the book only if both IDs are valid
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

    # Retrieve and display the details of the newly added book
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

    print(f"\nBook '{title}' (ID: {book_id}) added successfully.\n")

    cur.close()
    conn.close()



def remove_book(book_id):
    # Remove a book by ID after confirming with the user
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
            confirmation = input("Are you sure you want to remove this book (yes/no)? ").strip().lower()
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
    # Modify a book's details by showing current information
    conn = connect_to_db()
    cur = conn.cursor()

    # Check if the book with the specified ID exists
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
        print(tabulate([(book[0], book[1], book[3], book[5], book[6])], headers, tablefmt="fancy_grid"))

        while True:
            confirm = input("Would you like to proceed with modifying the details of this book? (yes/no): ").strip().lower()
            if confirm in ["yes", "no"]:
                break
            else:
                print("\nPlease enter 'yes' or 'no'.")

        if confirm == "yes":
            print("\nEnter the data you want to change, leave blank for no change.\n")
            new_title = input(f"Enter new title (current: {book[1]}): ").strip() or book[1]
            try:
                new_author_id = int(input(f"Enter new author ID (current: {book[2]}): ").strip() or book[2])
                new_genre_id = int(input(f"Enter new genre ID (current: {book[4]}): ").strip() or book[4])
                new_published_year = int(input(f"Enter new published year (current: {book[6]}): ").strip() or book[6])
            except ValueError:
                print("\nError: The input must be an integer.\n")
                return

            # Check if the new author_id exists in the database
            if new_author_id:
                cur.execute("SELECT author_id FROM authors WHERE author_id = %s", (new_author_id,))
                if not cur.fetchone():
                    print(f"\nError: Author ID {new_author_id} does not exist. Modification cancelled.\n")
                    cur.close()
                    conn.close()
                    return

            # Check if the new genre_id exists in the database
            if new_genre_id:
                cur.execute("SELECT genre_id FROM genres WHERE genre_id = %s", (new_genre_id,))
                if not cur.fetchone():
                    print(f"\nError: Genre ID {new_genre_id} does not exist. Modification cancelled.\n")
                    cur.close()
                    conn.close()
                    return

            # Update the book with the new details
            cur.execute(
                """
                UPDATE books
                SET title = %s, author_id = %s, genre_id = %s, published_year = %s
                WHERE book_id = %s
                """,
                (new_title, new_author_id, new_genre_id, new_published_year, book_id),
            )
            conn.commit()

            print("\nBook updated successfully. Here are the updated details:\n")
            headers = ["Book ID", "Title", "Author", "Genre", "Published Year"]
            print(tabulate([(book_id, new_title, new_author_id, new_genre_id, new_published_year)], headers, tablefmt="fancy_grid"))
        else:
            print("\nModification cancelled.\n")
    else:
        print(f"\nBook not found with ID: {book_id}\n")

    cur.close()
    conn.close()
