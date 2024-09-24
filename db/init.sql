CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);


CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);


CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT REFERENCES authors(author_id) ON DELETE SET NULL,
    genre_id INT REFERENCES genres(genre_id) ON DELETE SET NULL,
    published_year INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);


CREATE TABLE borrowers (
    borrower_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL
);


CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    book_id INT REFERENCES books(book_id) ON DELETE CASCADE,
    borrower_id INT REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    return_date DATE,
    CHECK (return_date IS NULL OR loan_date <= return_date)
);


CREATE OR REPLACE FUNCTION update_book_availability()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the availability status of the book associated with the loan
    UPDATE books
    SET is_available = FALSE
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger that calls the function after entering a loan
CREATE TRIGGER loan_insert_trigger
AFTER INSERT ON loans
FOR EACH ROW
EXECUTE FUNCTION update_book_availability();

-- Create the function to update the state of is_available to TRUE when the book is returned
CREATE OR REPLACE FUNCTION update_book_availability_on_return()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the availability status of the book associated with the loan
    UPDATE books
    SET is_available = TRUE
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger that calls the function after updating return_date in loans
CREATE TRIGGER loan_return_trigger
AFTER UPDATE OF return_date ON loans
FOR EACH ROW
WHEN (NEW.return_date IS NOT NULL)
EXECUTE FUNCTION update_book_availability_on_return();
