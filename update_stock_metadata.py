"""Fetch current metadata with yfinance and update existing SQLite rows.

Run stock_metadata.py first. This script needs internet access.
It updates the database only. Run fetch_stock_data.py to rebuild the hardcoded files.
"""

import sqlite3

from fetch_stock_data import FIELDS, fetch_records
from stock_metadata import DATABASE_PATH


def main():
    # Check before connecting, so a missing database is not silently created.
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Run stock_metadata.py first to create the database.")

    # Fetch and validate all companies before opening the write transaction.
    # A missing Yahoo field stops the update instead of replacing saved data with blanks.
    records, _ = fetch_records()
    print(f"Updating database: {DATABASE_PATH}")
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        with connection:
            for record in records:
                # UPDATE changes an existing row. WHERE limits it to this ticker.
                # Placeholders keep company text separate from the SQL statement.
                cursor = connection.execute("""
                    UPDATE stock_metadata
                    SET country = :country, currency = :currency,
                        company_name = :company_name, company_info = :company_info,
                        category = :category
                    WHERE ticker = :ticker
                """, {field: record[field] for field in FIELDS})
                if cursor.rowcount != 1:
                    raise ValueError(f"{record['ticker']}: missing from database; run stock_metadata.py")
                print(f"Updated: {record['ticker']}")
        # The with block commits all updates together; errors undo the batch.
        print(f"Committed {connection.total_changes} updated records.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
