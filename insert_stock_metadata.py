"""Read real stock metadata from CSV and insert it into stock_metadata.db.

Run stock_metadata.py first to create the table.
"""

import csv  # Read rows from a file containing values separated by commas.
import sqlite3  # Connect to SQLite and run SQL statements.
from pathlib import Path  # Build paths to the input file and database.


# Find files beside this script, even when it is run from another folder.
FOLDER = Path(__file__).resolve().parent
DATABASE_PATH = FOLDER / "stock_metadata.db"
CSV_PATH = FOLDER / "sample_stocks.csv"


def main():
    # This example expects the table created by stock_metadata.py.
    # Check first because sqlite3.connect would otherwise create an empty database.
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run stock_metadata.py first to create stock_metadata.db.")

    # DictReader uses the header row as field names.
    # sample_stocks.csv has six columns and real Yahoo Finance company data:
    # ticker: a unique stock symbol; country: the company's home country;
    # currency: the stock's trading currency; company_name: the company's name;
    # company_info: a short business description; category: its business sector.
    # CSV files have no standard comment format, so their explanation lives here.
    # newline="" lets csv handle line endings; encoding="utf-8" reads Unicode text.
    # The with block closes the CSV file automatically after reading it.
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        # Each dictionary is one CSV row. list() keeps all rows after the file closes.
        stocks = list(csv.DictReader(file))

    # These are the required CSV column names and database field names.
    fields = [
        "ticker", "country", "currency", "company_name", "company_info", "category"
    ]
    # Check every row before inserting anything. Row 1 contains the column names.
    for line_number, stock in enumerate(stocks, start=2):
        for field in fields:
            # get supplies an empty string for a missing column.
            # strip removes surrounding spaces, so spaces alone count as empty.
            if not stock.get(field, "").strip():
                raise ValueError(f"CSV line {line_number}: missing {field}")

    print(f"Read {len(stocks)} records from {CSV_PATH}")
    print(f"Opening database: {DATABASE_PATH}")

    connection = sqlite3.connect(DATABASE_PATH)
    try:
        # Commit all inserts together on success; undo them if an exception occurs.
        with connection:
            # Process one dictionary (one company) at a time.
            for stock in stocks:
                # Named placeholders match the CSV column names.
                # SQLite binds each value safely rather than building SQL from text.
                # Keep existing rows when the ticker is already saved.
                # The dictionary below removes surrounding spaces from each value.
                cursor = connection.execute("""
                    INSERT INTO stock_metadata (
                        ticker, country, currency,
                        company_name, company_info, category
                    ) VALUES (
                        :ticker, :country, :currency,
                        :company_name, :company_info, :category
                    )
                    ON CONFLICT(ticker) DO NOTHING
                """, {field: stock[field].strip() for field in fields})

                # rowcount is 1 for an inserted row and 0 for a skipped duplicate.
                # These messages describe progress; the commit happens on leaving with.
                action = "Inserted" if cursor.rowcount == 1 else "Skipped existing"
                print(f"{action}: {stock['ticker']}")

        # total_changes counts the rows inserted using this connection.
        print(f"Committed {connection.total_changes} new records.")
    finally:
        # Close the connection on success and on error.
        connection.close()


# Execute main() only when this script is run directly.
if __name__ == "__main__":
    main()
