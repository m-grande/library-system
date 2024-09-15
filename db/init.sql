-- Creazione della tabella degli autori
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Creazione della tabella dei generi
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Creazione della tabella dei libri
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT REFERENCES authors(author_id) ON DELETE SET NULL,
    genre_id INT REFERENCES genres(genre_id) ON DELETE SET NULL,
    published_year INT NOT NULL,
    is_available BOOLEAN DEFAULT TRUE
);

-- Creazione della tabella dei prestatori (utenti)
CREATE TABLE borrowers (
    borrower_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- Creazione della tabella dei prestiti
CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    book_id INT REFERENCES books(book_id) ON DELETE CASCADE,
    borrower_id INT REFERENCES borrowers(borrower_id) ON DELETE CASCADE,
    loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
    return_date DATE,
    CHECK (return_date IS NULL OR loan_date <= return_date)
);

-- Creare la funzione per aggiornare lo stato di is_available a FALSE
CREATE OR REPLACE FUNCTION update_book_availability()
RETURNS TRIGGER AS $$
BEGIN
    -- Aggiornare lo stato di disponibilità del libro associato al prestito
    UPDATE books
    SET is_available = FALSE
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creare il trigger che chiama la funzione dopo l'inserimento di un prestito
CREATE TRIGGER loan_insert_trigger
AFTER INSERT ON loans
FOR EACH ROW
EXECUTE FUNCTION update_book_availability();

-- Creare la funzione per aggiornare lo stato di is_available a TRUE quando il libro viene restituito
CREATE OR REPLACE FUNCTION update_book_availability_on_return()
RETURNS TRIGGER AS $$
BEGIN
    -- Aggiornare lo stato di disponibilità del libro associato al prestito
    UPDATE books
    SET is_available = TRUE
    WHERE book_id = NEW.book_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creare il trigger che chiama la funzione dopo l'aggiornamento di return_date in loans
CREATE TRIGGER loan_return_trigger
AFTER UPDATE OF return_date ON loans
FOR EACH ROW
WHEN (NEW.return_date IS NOT NULL)
EXECUTE FUNCTION update_book_availability_on_return();
