# Library System

## Description
The **Library System** is a Python application designed to manage a library's books, loans, and borrowers. The application uses PostgreSQL as its database backend and provides a command-line interface (CLI) to interact with the system. You can add, modify, and delete books, borrowers, and manage loans. This application also supports test environments, ensuring that the functionality is thoroughly verified.

## Prerequisites
Before running the application, make sure you have PostgreSQL and Python installed and running on your system.

## Setup Instructions

### Step 1: Open psql
Open your terminal and launch `psql` to interact with PostgreSQL:
```
psql
```

### Step 2: Create Databases
Create two local databases - one for production and one for testing:
```
CREATE DATABASE library_db;
CREATE DATABASE library_test_db;
```

### Step 3: Exit psql
Once the databases have been created, exit `psql` by running:
```
\q
```

### Step 4: Initialize Database Structure
For each database, initialize the table structures using the `init.sql` file:
```
psql -d library_db -U your_username -h localhost -f db/init.sql
psql -d library_test_db -U your_username -h localhost -f db/init.sql
```

### Step 5: Import Sample Data
Next, import the data for authors, genres, books, and borrowers into the `library_db`:
```
psql -d library_db -U your_username -h localhost -f db/data/authors.sql
psql -d library_db -U your_username -h localhost -f db/data/genres.sql
psql -d library_db -U your_username -h localhost -f db/data/books.sql
psql -d library_db -U your_username -h localhost -f db/data/borrowers.sql
```


### Step 6: Update Database Configuration
Modify the `DATABASE_CONFIG` in `app/db_connection.py`. Replace `your_username` with your PostgreSQL username:
```python
DATABASE_CONFIG = {
    "production": {
        "dbname": "library_db",
        "user": "your_username",
        "host": "localhost",
        "port": "5432",
    },
    "test": {
        "dbname": "library_test_db",
        "user": "your_username",
        "host": "localhost",
        "port": "5432",
    }
}
```

## Step 7: Set Up a Virtual Environment
It's recommended to run the application in a virtual environment:

1. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

3. To deactivate the virtual environment, run:
   ```
   deactivate
   ```

## Step 8: Install Dependencies
Install the required Python dependencies:
```
pip install -r requirements.txt
```

## Running the Application
To run the application in the production environment, use:
```
ENV=production python3 -m app.cli
```

## Running the Tests
To run the test suite, use the following command:
```
ENV=test pytest -v
```

## Additional Notes
- Make sure your PostgreSQL server is running and accessible at `localhost` on port `5432`.
- The test database (`library_test_db`) is used to isolate test runs from the production database.
- The CLI allows for easy management of the library, including adding books, borrowers, and managing loans.

If you encounter any issues or have questions, feel free to raise an issue or contribute to the project.# library-system