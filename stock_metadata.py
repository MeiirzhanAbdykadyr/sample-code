"""Create a SQLite table and indexes, then save real stock metadata."""

import sqlite3  # Python's built in library for working with SQLite databases.
from pathlib import Path  # Build file paths without depending on the current folder.

from stock_data import SAMPLE_STOCKS  # Hardcoded Yahoo Finance data from yfinance.


# Save the database beside this script.
# __file__ is this script's path; resolve() makes it absolute; parent is its folder.
DATABASE_PATH = Path(__file__).resolve().parent / "stock_metadata.db"

# The real company records live in stock_data.py. No internet is needed here.
# Category stores Yahoo Finance's sector. Country is the company's home country.
# Currency is the stock's trading currency, not its financial reporting currency.


def main():
    # Keep the database steps together in a function that runs below.
    print(f"Opening database: {DATABASE_PATH}")

    # The connection creates the database file if it does not exist.
    connection = sqlite3.connect(DATABASE_PATH)
    # try/finally ensures that the connection closes even if a database step fails.
    try:
        # Save (commit) the inserts on success; undo them if an exception occurs.
        with connection:
            # IF NOT EXISTS allows the script to run again using the same table.
            # TEXT stores text. NOT NULL prevents SQL NULL (a missing value).
            # PRIMARY KEY makes ticker unique, so two rows cannot share a ticker.
            connection.execute("""
                CREATE TABLE IF NOT EXISTS stock_metadata (
                    ticker TEXT PRIMARY KEY NOT NULL,
                    country TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    company_info TEXT NOT NULL,
                    category TEXT NOT NULL
                )
            """)

            # An index helps SQLite find rows without scanning the whole table.
            # This index supports queries such as WHERE category = 'Technology'.
            # IF NOT EXISTS allows repeat runs without creating the index twice.
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_metadata_category
                ON stock_metadata (category)
            """)
            # A second index helps searches by the company's home country.
            connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_stock_metadata_country
                ON stock_metadata (country)
            """)
            # The ticker primary key already has its own index, so do not add another.

            # Placeholders (?) pass values safely into SQL.
            # executemany runs this INSERT once for each tuple in SAMPLE_STOCKS.
            # The six values match the six columns listed in the INSERT statement.
            # Keep an existing row when its ticker is already in the table.
            connection.executemany("""
                INSERT INTO stock_metadata (
                    ticker, country, currency,
                    company_name, company_info, category
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(ticker) DO NOTHING
            """, SAMPLE_STOCKS)

        # SELECT reads the listed columns from the table.
        # ORDER BY sorts rows by ticker; fetchall() collects the results in a list.
        rows = connection.execute("""
            SELECT ticker, country, currency,
                   company_name, company_info, category
            FROM stock_metadata
            ORDER BY ticker
        """).fetchall()

        # len(rows) counts the records returned by the query.
        print(f"\nSaved records: {len(rows)}")
        for row in rows:
            # zip pairs each column name with its value in the returned tuple.
            # dict turns those pairs into a dictionary that is easy to read.
            print(dict(zip(
                ["ticker", "country", "currency", "company_name",
                 "company_info", "category"],
                row,
            )))
    finally:
        # Release the database connection after printing or after an error.
        connection.close()


# Run main() when this file is executed directly, but not when it is imported.
if __name__ == "__main__":
    main()
