import pytest
from unittest.mock import patch
from app.db_connection import connect_to_db
from app.borrowers import view_borrowers, search_borrowers, add_borrower, remove_borrower_by_id, modify_borrower


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

# Test viewing all borrowers in the database
def test_view_borrowers(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    borrowers_data = [
        ("Borrower 1", "borrower1@example.com", "1234567890"),
        ("Borrower 2", "borrower2@example.com", "0987654321"),
        ("Borrower 3", "borrower3@example.com", "1122334455"),
    ]
    
    for name, email, phone in borrowers_data:
        add_borrower(name, email, phone)

    view_borrowers()

    captured = capsys.readouterr()

    for name, email, phone in borrowers_data:
        assert name in captured.out, f"{name} not found in the output"
        assert email in captured.out, f"{email} not found in the output"
        assert phone in captured.out, f"{phone} not found in the output"

    assert "Total number of borrowers: 3" in captured.out, "Total borrower count is incorrect"

    cur.close()

# Test for searching a borrower that exists in the database
def test_search_borrower_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("Borrower Test", "test@example.com", "1234567890")

    search_borrowers("Borrower Test")

    captured = capsys.readouterr()

    assert "Borrower Test" in captured.out, "Borrower name not found in search results"
    assert "test@example.com" in captured.out, "Borrower email not found in search results"
    assert "1234567890" in captured.out, "Borrower phone not found in search results"

    assert "Total number of borrowers found: 1" in captured.out, "Incorrect number of borrowers found"

    cur.close()

# Test for searching a borrower that does not exist in the database
def test_search_borrower_not_found(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    search_borrowers("Nonexistent Borrower")

    captured = capsys.readouterr()

    assert "No borrowers found matching the keyword" in captured.out, "Error message not shown when borrower is not found"

    cur.close()

# Test adding a borrower
def test_add_borrower(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("John Doe", "john.doe@example.com", "1234567890")

    cur.execute("SELECT * FROM borrowers WHERE email = 'john.doe@example.com'")
    result = cur.fetchone()

    assert result is not None, "Borrower was not added to the database"

    captured = capsys.readouterr()
    assert "Borrower 'John Doe' added successfully" in captured.out, "Success message not shown after adding borrower"
    assert "john.doe@example.com" in captured.out, "Borrower email not found in the output"
    assert "1234567890" in captured.out, "Borrower phone not found in the output"

    cur.close()

# Test adding a borrower that already exists
def test_add_borrower_duplicate(db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("Alice Smith", "alice.smith@example.com", "9876543210")
    add_borrower("Alice Smith", "alice.smith@example.com", "9876543210")

    captured = capsys.readouterr()
    assert "Error: A borrower with email 'alice.smith@example.com' or phone '9876543210' already exists." in captured.out, "Duplicate borrower error not shown"

    cur.execute("SELECT COUNT(*) FROM borrowers WHERE email = 'alice.smith@example.com'")
    count = cur.fetchone()[0]
    assert count == 1, "Duplicate borrower was added to the database"

    cur.close()

# Test removing a borrower that exists in the database
@patch("builtins.input", return_value="yes")
def test_remove_borrower_exists(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("John Doe", "john.doe@example.com", "1234567890")

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'john.doe@example.com'")
    borrower_id = cur.fetchone()[0]

    remove_borrower_by_id(borrower_id)

    captured = capsys.readouterr()
    assert f"Borrower 'John Doe' removed successfully" in captured.out, "Borrower was not removed successfully"
    
    cur.execute("SELECT * FROM borrowers WHERE borrower_id = %s", (borrower_id,))
    result = cur.fetchone()
    assert result is None, "Borrower was not removed from the database"

    cur.close()

# Test removing a borrower that does not exist
@patch("builtins.input", return_value="yes")
def test_remove_borrower_not_exists(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    non_existent_borrower_id = 999
    remove_borrower_by_id(non_existent_borrower_id)

    captured = capsys.readouterr()
    assert f"No borrower found with ID: {non_existent_borrower_id}" in captured.out, "Non-existent borrower case not handled correctly"

    cur.close()

# Test modifying a borrower with correct parameters
@patch("builtins.input", side_effect=["yes", "Jane Smith", "jane.smith@example.com", "9876543210"])
def test_modify_borrower_correct(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("John Doe", "john.doe@example.com", "1234567890")

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'john.doe@example.com'")
    borrower_id = cur.fetchone()[0]

    modify_borrower(borrower_id)

    captured = capsys.readouterr()

    assert "Borrower updated successfully" in captured.out, "Borrower was not updated successfully"

    cur.execute("SELECT name, email, phone FROM borrowers WHERE borrower_id = %s", (borrower_id,))
    updated_borrower = cur.fetchone()
    assert updated_borrower == ("Jane Smith", "jane.smith@example.com", "9876543210"), "Borrower details were not updated correctly"

    cur.close()

# Test modifying a borrower with incorrect parameters
@patch("builtins.input", side_effect=["yes", "Invalid123", "invalid_email", "invalid_phone"])
def test_modify_borrower_incorrect(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("John Doe", "john.doe@example.com", "1234567890")

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'john.doe@example.com'")
    borrower_id = cur.fetchone()[0]

    modify_borrower(borrower_id)

    captured = capsys.readouterr()

    assert "Error: Name must contain only letters and spaces." in captured.out, "Name validation error not triggered"
    assert "Error: Invalid email format." not in captured.out, "Email validation triggered too early"
    assert "Error: Phone number must contain only digits." not in captured.out, "Phone validation triggered too early"

    cur.close()

# Test modifying aaborrower with an invalid email
@patch("builtins.input", side_effect=["yes", "Valid Name", "invalid_email", "9876543210"])
def test_modify_borrower_invalid_email(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("John Doe", "john.doe@example.com", "1234567890")

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'john.doe@example.com'")
    borrower_id = cur.fetchone()[0]

    modify_borrower(borrower_id)

    captured = capsys.readouterr()

    assert "Error: Invalid email format." in captured.out, "Email validation error not triggered"

    cur.close()

# Test modifying a borrower with an invalid phone number
@patch("builtins.input", side_effect=["yes", "Valid Name", "valid.email@example.com", "invalid_phone"])
def test_modify_borrower_invalid_phone(mock_input, db_connection, capsys):
    conn = db_connection
    cur = conn.cursor()

    add_borrower("John Doe", "john.doe@example.com", "1234567890")

    cur.execute("SELECT borrower_id FROM borrowers WHERE email = 'john.doe@example.com'")
    borrower_id = cur.fetchone()[0]

    modify_borrower(borrower_id)

    captured = capsys.readouterr()

    assert "Error: Phone number must contain only digits." in captured.out, "Phone validation error not triggered"

    cur.close()