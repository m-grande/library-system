import pytest
from unittest.mock import patch
from app.db_connection import connect_to_db
from app.books import add_book, list_books, remove_book, modify_book, search_books


# Fixture to connect to the test database and clean up after each test
@pytest.fixture(scope="function")
def db_connection():
    # Setup: Connect to the test database
    conn = connect_to_db()
    cur = conn.cursor()

    # Clean up any existing data before each test
    cur.execute("TRUNCATE TABLE books, borrowers, loans, authors, genres RESTART IDENTITY CASCADE;")
    conn.commit()

    # Enter author and example genre
    cur.execute("INSERT INTO authors (name) VALUES ('Sample Author')")
    cur.execute("INSERT INTO genres (name) VALUES ('Sample Genre')")
    conn.commit()

    yield conn

    # Teardown: Clean up after each test
    cur.execute("TRUNCATE TABLE books, borrowers, loans, authors, genres RESTART IDENTITY CASCADE;")
    conn.commit()
    conn.close()


# Test listing all books in the database
def test_list_books(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    for i in range(5):
        add_book(f"Book {i+1}", 1, 1, 2020 + i)

    list_books()

    captured = capsys.readouterr()

    for i in range(5):
        assert f"Book {i+1}" in captured.out, f"Book {i+1} not found in the output"

    assert "Total number of books: 5" in captured.out, "Total book count is incorrect"

    cur.close()

# Test searching for a book that exists in the database
def test_search_books_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Search Book", 1, 1, 2024)

    search_books("Search")

    captured = capsys.readouterr()

    assert "Search Book" in captured.out, "Book not found in search results"
    assert "Total number of books found: 1" in captured.out, "Total count is incorrect"

    cur.close()

# Test searching for a book that does not exist in the database
def test_search_books_not_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Different Book", 1, 1, 2024)

    search_books("Nonexistent")

    captured = capsys.readouterr()

    assert "No books found matching the keyword: 'Nonexistent'" in captured.out, "No result message incorrect"

    cur.close()


# Test adding a book with valid author_id and genre_id
def test_add_book_success(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Valid Book", 1, 1, 2024)

    captured = capsys.readouterr()

    cur.execute("SELECT * FROM books WHERE title = 'Valid Book'")
    result = cur.fetchone()

    assert result is not None, "Book was not added to the database"
    assert "Book 'Valid Book' (ID: 1) added successfully." in captured.out, "Success message not found"

    cur.close()

# Test adding a book with an invalid author_id
def test_add_book_invalid_author(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Invalid Author Book", 999, 1, 2024)

    captured = capsys.readouterr()

    cur.execute("SELECT * FROM books WHERE title = 'Invalid Author Book'")
    result = cur.fetchone()

    assert result is None, "Book should not be added with invalid author_id"
    assert "Error: Author ID 999 does not exist. Book insertion cancelled." in captured.out, "Author ID error message not found"

    cur.close()

# Test adding a book with an invalid genre_id
def test_add_book_invalid_genre(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Invalid Genre Book", 1, 999, 2024)

    captured = capsys.readouterr()

    cur.execute("SELECT * FROM books WHERE title = 'Invalid Genre Book'")
    result = cur.fetchone()

    assert result is None, "Book should not be added with invalid genre_id"
    assert "Error: Genre ID 999 does not exist. Book insertion cancelled." in captured.out, "Genre ID error message not found"

    cur.close()


# Test removing a book that exists in the database
@patch("builtins.input", return_value="yes")
def test_remove_book_exists(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Book to Remove", 1, 1, 2024)

    cur.execute("SELECT book_id FROM books WHERE title = 'Book to Remove'")
    book_id = cur.fetchone()[0]

    remove_book(book_id)

    captured = capsys.readouterr()
    assert f"Book with ID {book_id} removed successfully." in captured.out, "Book removal message not found"

    cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    result = cur.fetchone()

    assert result is None, "Book was not removed from the database"

    cur.close()

# Test removing a book that does not exist in the database
@patch("builtins.input", return_value="yes")
def test_remove_book_not_exists(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    remove_book(999)

    captured = capsys.readouterr()
    assert "No book found with ID: 999" in captured.out, "No book found message not displayed"

    cur.close()


# Test modifying a book with correct parameters
@patch("builtins.input", side_effect=["yes", "New Title", "1", "1", "2025"])
def test_modify_book_correct(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Original Title", 1, 1, 2024)

    cur.execute("SELECT book_id FROM books WHERE title = 'Original Title'")
    book_id = cur.fetchone()[0]

    modify_book(book_id)

    captured = capsys.readouterr()
    assert "Book updated successfully" in captured.out, "Book update message not found"

    cur.execute("SELECT title, author_id, genre_id, published_year FROM books WHERE book_id = %s", (book_id,))
    modified_book = cur.fetchone()

    assert modified_book == ("New Title", 1, 1, 2025), "Book was not modified correctly"

    cur.close()

# Test modifying a book with invalid author ID
@patch("builtins.input", side_effect=["yes", "Invalid Title", "999", "1", "2025"])
def test_modify_book_invalid_author(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Original Title", 1, 1, 2024)

    cur.execute("SELECT book_id FROM books WHERE title = 'Original Title'")
    book_id = cur.fetchone()[0]

    modify_book(book_id)

    captured = capsys.readouterr()

    assert "Error: Author ID 999 does not exist" in captured.out, "Error message for invalid author ID not found"

    cur.close()

# Test modifying a book with invalid genre ID
@patch("builtins.input", side_effect=["yes", "Invalid Title", "1", "999", "2025"])
def test_modify_book_invalid_genre(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_book("Original Title", 1, 1, 2024)

    cur.execute("SELECT book_id FROM books WHERE title = 'Original Title'")
    book_id = cur.fetchone()[0]

    modify_book(book_id)

    captured = capsys.readouterr()

    assert "Error: Genre ID 999 does not exist" in captured.out, "Error message for invalid genre ID not found"

    cur.close()
