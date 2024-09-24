import pytest
from unittest.mock import patch
from app.db_connection import connect_to_db
from app.loans import view_loans, search_loan, borrow_book, return_book, modify_loan


# Fixture to connect to the test database and clean up after each test
@pytest.fixture(scope="function")
def db_connection():
    # Setup: Connect to the test database
    conn = connect_to_db()
    cur = conn.cursor()

    # Clean up any existing data before each test
    cur.execute("TRUNCATE TABLE books, borrowers, loans, authors, genres RESTART IDENTITY CASCADE;")
    conn.commit()

    # # Enter author and example genre
    cur.execute("INSERT INTO authors (name) VALUES ('Sample Author')")
    cur.execute("INSERT INTO genres (name) VALUES ('Sample Genre')")
    conn.commit()

    yield conn

    # Teardown: Clean up after each test
    cur.execute("TRUNCATE TABLE books, borrowers, loans, authors, genres RESTART IDENTITY CASCADE;")
    conn.commit()
    conn.close()



# Test viewing loans when there are loans in the database
def test_view_loans_with_data(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    cur.execute("INSERT INTO borrowers (name, email, phone) VALUES ('John Doe', 'john.doe@example.com', '123456789')")
    cur.execute("INSERT INTO books (title, author_id, genre_id, published_year) VALUES ('Book 1', 1, 1, 2022)")
    conn.commit()

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'john.doe@example.com'")
    borrower_id = cur.fetchone()[0]
    
    cur.execute("SELECT book_id FROM books WHERE title = 'Book 1'")
    book_id = cur.fetchone()[0]

    cur.execute("INSERT INTO loans (book_id, borrower_id) VALUES (%s, %s)", (book_id, borrower_id))
    conn.commit()

    view_loans()

    captured = capsys.readouterr()

    assert "Loan ID" in captured.out, "Loan ID header not found"
    assert "Book 1" in captured.out, "Book Title not found in output"
    assert "John Doe" in captured.out, "Borrower name not found in output"
    assert "Total number of loans: 1" in captured.out, "Total loan count incorrect"

    cur.close()

# Test viewing loans when there are no loans in the database
def test_view_loans_no_data(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE loans RESTART IDENTITY CASCADE")
    conn.commit()

    view_loans()

    captured = capsys.readouterr()

    assert "No loans found." in captured.out, "No loans message not found"
    
    cur.close()

# Test searching for a loan by a keyword that matches a loan
def test_search_loan_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    cur.execute("INSERT INTO borrowers (name, email, phone) VALUES ('Jane Doe', 'jane.doe@example.com', '987654321')")
    cur.execute("INSERT INTO books (title, author_id, genre_id, published_year) VALUES ('Test Book', 1, 1, 2023)")
    conn.commit()

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'jane.doe@example.com'")
    borrower_id = cur.fetchone()[0]
    
    cur.execute("SELECT book_id FROM books WHERE title = 'Test Book'")
    book_id = cur.fetchone()[0]

    cur.execute("INSERT INTO loans (book_id, borrower_id) VALUES (%s, %s)", (book_id, borrower_id))
    conn.commit()

    search_loan("Jane")

    captured = capsys.readouterr()

    assert "Loan ID" in captured.out, "Loan ID header not found in output"
    assert "Test Book" in captured.out, "Book Title not found in output"
    assert "Jane Doe" in captured.out, "Borrower name not found in output"
    assert "Total number of loans found: 1" in captured.out, "Total loans count incorrect"

    cur.close()

# Test searching for a loan with a keyword that does not match any loan
def test_search_loan_not_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    cur.execute("TRUNCATE TABLE loans RESTART IDENTITY CASCADE")
    conn.commit()

    search_loan("NonExistentLoan")

    captured = capsys.readouterr()

    assert "No loans found matching the keyword" in captured.out, "No loans found message not displayed"
    
    cur.close()

# Test returning a book successfully
def test_return_book_successful(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    cur.execute("INSERT INTO borrowers (name, email, phone) VALUES ('Jane Doe', 'jane.doe@example.com', '987654321')")
    cur.execute("INSERT INTO books (title, author_id, genre_id, published_year, is_available) VALUES ('Test Book', 1, 1, 2023, FALSE)")
    conn.commit()

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'jane.doe@example.com'")
    borrower_id = cur.fetchone()[0]
    
    cur.execute("SELECT book_id FROM books WHERE title = 'Test Book'")
    book_id = cur.fetchone()[0]

    cur.execute("INSERT INTO loans (book_id, borrower_id, loan_date) VALUES (%s, %s, CURRENT_DATE)", (book_id, borrower_id))
    conn.commit()


    cur.execute("SELECT loan_id FROM loans WHERE book_id = %s AND borrower_id = %s", (book_id, borrower_id))
    loan_id = cur.fetchone()[0]

    return_book(loan_id)

    captured = capsys.readouterr()
    assert f"Loan ID {loan_id}: Book 'Test Book' returned successfully." in captured.out, "Book return message not found"
    assert "Return Date" in captured.out, "Return date not displayed"

    cur.execute("SELECT is_available FROM books WHERE book_id = %s", (book_id,))
    is_available = cur.fetchone()[0]
    assert is_available is True, "Book was not marked as available after return"

    cur.close()

# Test attempting to return a book with a non-existent loan ID
def test_return_book_nonexistent(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    return_book(999)

    captured = capsys.readouterr()
    assert "Error: No active loan found with the provided loan ID." in captured.out, "No loan found message not displayed"

    cur.close()

# Test attempting to modify a loan that does not exist
def test_modify_loan_not_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    modify_loan(999)

    captured = capsys.readouterr()
    assert "Loan not found with ID: 999" in captured.out, "Loan not found message not displayed"

    cur.close()