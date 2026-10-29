"""ECON7890 Week 9: save posts in SQLite and filter by sentiment.

PURPOSE
Last week, you collected social media posts and used an LLM to label them.
This exercise adds database storage so you can keep those posts and retrieve
the ones you need later. Adapt the stock database examples to a new dataset.

GOALS
By completing this exercise, you should be able to:
1. Create a table with suitable columns and a unique post ID.
2. Explain which values the table requires and why duplicate IDs are rejected.
3. Write a Python function that reads saved posts filtered by sentiment.
4. Inspect the saved records in a database viewer and check the query result.

YOUR WORK
Complete the two functions marked TODO.
Use the supplied stock_metadata.py and read_stock_metadata.py as examples.
The core exercise needs no API key, internet request or LLM call.

TASK 1: CREATE THE TABLE
Complete create_table(). Create a table called twitter_posts with these columns:

    Column          Data type   Can be missing?   Unique row ID?
    screen_name     TEXT        No                No
    datetime        TEXT        No                No
    text            TEXT        No                No
    sentiment       TEXT        No                No
    category        TEXT        No                No
    post_id         TEXT        No                Yes

Use IF NOT EXISTS so the script can run again. Use PRIMARY KEY and NOT NULL
for post_id. Use NOT NULL for the other columns. The ID is text, even when a
real service supplies an ID containing only digits.

datetime means when the post was published, including its time zone. The
invented examples use UTC, shown by Z at the end. category is the topic label
from last week. A missing value means SQL NULL, which differs from empty text.

TASK 2: READ POSTS WITH ONE SENTIMENT
Complete get_posts_by_sentiment(sentiment).

    Input:  a sentiment string, such as "positive".
    Return: a list of dictionaries containing all six fields for matching posts.
    Order:  sort by post_id in ascending order.
    No matching posts: return an empty list, [].

Use a SELECT query with a WHERE condition. Pass the sentiment separately
using a ? placeholder. Do not build SQL by joining the input into the query.
Return the records. Printing alone does not satisfy the task.

GIVEN CODE
The code below inserts four invented posts after you create the table.
Keep that code. You do not need to write an insertion function.

The database file is social_media_posts.db in the same folder as this file.
twitter_posts is the table inside that database.

CHECK YOUR RESULT
The supplied examples should give:

    positive:     demo-001 and demo-003
    negative:     demo-002
    neutral:      demo-004
    not_a_label:  no records, []

Open social_media_posts.db in DB Browser for SQLite. Use Database Structure to
check the columns and Browse Data to inspect the four invented records.
Run the file again. The supplied insertion code skips existing IDs, so it
should still have four records. This is a repeat check, not an extra task.

BONUS: SAVE REAL POSTS
Use what you learned last week to fetch real Twitter/X posts, obtain their
sentiment and category labels, and save them in twitter_posts.

Extend last week's extraction to retain the screen name and original post
time. Its supplied helper kept only post_id and text. Map the LLM's topic
field to this table's category field. Keep source timestamps and their time
zones. Do not invent a missing timestamp or a label after a failed request.

Match labels to posts using post_id. Keep IDs as text. Save all six fields,
then use get_posts_by_sentiment("positive") to read the saved positive posts.
Import the same posts again and check that no duplicate IDs appear.

Use your existing approved API route and account access. Read keys from .env
as last week. Never put keys in this file. Keep real post data and the database
local. The four record counts above apply only before adding bonus posts.
"""

import sqlite3
from pathlib import Path


# GIVEN: put the database beside this Python file, regardless of where it runs.
DATABASE_PATH = Path(__file__).resolve().parent / "social_media_posts.db"


def create_table():
    """TODO 1: create twitter_posts with the six columns and rules above.

    Follow the stock table example: open a connection, execute your CREATE
    TABLE statement, commit the change and close the connection.
    This function does not need to return a value.
    """
    raise NotImplementedError("Complete create_table() first.")


def get_posts_by_sentiment(sentiment):
    """TODO 2: return all saved posts whose sentiment equals the input.

    Follow read_stock_metadata.py. Set connection.row_factory = sqlite3.Row
    before reading. This lets you turn a returned row into dict(row).
    Run your parameterised SELECT, use fetchall(), convert each result to a
    dictionary, then close the connection and return the list.
    A list containing one parameter can be written as [sentiment].
    """
    raise NotImplementedError("Complete get_posts_by_sentiment(sentiment).")


# GIVEN: every value below is invented for this exercise.
# Tuple values follow the column order in the supplied INSERT statement.
SAMPLE_POSTS = [
    (
        "demo_user_a", "2026-10-14T01:00:00Z",
        "I like the new charging app. It is much easier to use.",
        "positive", "Tesla", "demo-001",
    ),
    (
        "demo_user_b", "2026-10-14T02:00:00Z",
        "The charging app failed again. This is frustrating.",
        "negative", "Tesla", "demo-002",
    ),
    (
        "demo_user_c", "2026-10-14T03:00:00Z",
        "I enjoyed watching the rocket launch. Great work.",
        "positive", "SpaceX Launch", "demo-003",
    ),
    (
        "demo_user_d", "2026-10-14T04:00:00Z",
        "Tesla published its product announcement today.",
        "neutral", "Tesla", "demo-004",
    ),
]


def save_sample_posts():
    """GIVEN: save the invented posts, keeping any ID already in the table."""
    connection = sqlite3.connect(DATABASE_PATH)
    try:
        # ? placeholders keep data values separate from the SQL statement.
        # executemany runs the INSERT once for each tuple in SAMPLE_POSTS.
        # ON CONFLICT skips an ID already saved. It does not update its labels.
        connection.executemany("""
            INSERT INTO twitter_posts (
                screen_name, datetime, text, sentiment, category, post_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(post_id) DO NOTHING
        """, SAMPLE_POSTS)
        connection.commit()
        count = connection.execute("SELECT COUNT(*) FROM twitter_posts").fetchone()[0]
        print(f"Saved records in twitter_posts: {count}")
    finally:
        connection.close()


def main():
    """GIVEN: run the two tasks in order and display results for inspection."""
    print(f"Database file: {DATABASE_PATH}")
    print("Task 1: create the table.")
    try:
        create_table()
    except NotImplementedError as error:
        print(error)
        return

    print("Given helper: save the four invented posts.")
    save_sample_posts()

    print("Task 2: read posts by sentiment.")
    for sentiment in ["positive", "negative", "neutral", "not_a_label"]:
        try:
            posts = get_posts_by_sentiment(sentiment)
        except NotImplementedError as error:
            print(error)
            return
        if not isinstance(posts, list):
            print("Your function must return a list. Printing is not enough.")
            return
        print(f"\nSentiment: {sentiment}. Returned records: {len(posts)}")
        print(posts)


if __name__ == "__main__":
    try:
        main()
    except sqlite3.Error as error:
        print(f"Database error in {DATABASE_PATH}: {error}")
        print("Check your table name, column names and SQL statement.")
        raise SystemExit(1)
