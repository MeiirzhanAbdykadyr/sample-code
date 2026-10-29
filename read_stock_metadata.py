"""Read and print all stock metadata saved in stock_metadata.db."""

import sqlite3  # Connect to the database and run a SELECT query.
from pathlib import Path  # Find the database file beside this script.


# Use an absolute path so running from another folder still finds the same file.
DATABASE_PATH = Path(__file__).resolve().parent / "stock_metadata.db"


def main():
    # Check that the database exists before connecting.
    # Otherwise SQLite would create an empty database with no stock table.
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run stock_metadata.py first to create stock_metadata.db.")

    print(f"Reading database: {DATABASE_PATH}")
    connection = sqlite3.connect(DATABASE_PATH)
    # Return rows with column names, so each row can become a dictionary.
    connection.row_factory = sqlite3.Row
    try:
        # SELECT chooses the columns to read; FROM names the source table.
        # ORDER BY ticker sorts the results alphabetically by ticker.
        # fetchall() collects every result row in a Python list.
        rows = connection.execute("""
            SELECT ticker, country, currency,
                   company_name, company_info, category
            FROM stock_metadata
            ORDER BY ticker
        """).fetchall()

        # Count the returned rows, then print each row as a dictionary.
        # Each dictionary maps column names to their saved values.
        print(f"Records found: {len(rows)}")
        for row in rows:
            print(dict(row))
    finally:
        # Always close the connection, even if reading or printing raises an error.
        connection.close()


# Run the reader when executed directly; importing it does not run the query.
if __name__ == "__main__":
    main()
