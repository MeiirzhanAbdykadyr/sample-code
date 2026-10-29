"""Invented example: overlapping collection can inflate a sentiment count.

Compare a CSV style append with database insertion using a unique post ID.
The database keeps the first saved label. Skipping a repeat does not update it.
SQL references: https://sqlite.org/lang_upsert.html
https://sqlite.org/lang_select.html
"""
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / 'invented_analytics.db'
FIRST_BATCH = [('demo-001', 'positive'), ('demo-002', 'negative'),
               ('demo-003', 'positive')]
SECOND_BATCH = [('demo-003', 'positive'), ('demo-004', 'neutral')]


def main():
    appended = FIRST_BATCH + SECOND_BATCH
    print('All posts and labels in this demonstration are invented.')
    print('Appended rows:', len(appended))
    print('Positive rows after append:', sum(row[1] == 'positive' for row in appended))
    connection = sqlite3.connect(DATABASE)
    try:
        connection.execute('''CREATE TABLE IF NOT EXISTS demo_posts (
            post_id TEXT PRIMARY KEY NOT NULL,
            sentiment TEXT NOT NULL
        )''')
        for batch in (FIRST_BATCH, SECOND_BATCH):
            for post in batch:
                connection.execute('''INSERT INTO demo_posts VALUES (?, ?)
                    ON CONFLICT(post_id) DO NOTHING''', post)
        connection.commit()
        total = connection.execute('SELECT COUNT(*) FROM demo_posts').fetchone()[0]
        summary = connection.execute('''SELECT sentiment, COUNT(*) AS total
            FROM demo_posts GROUP BY sentiment ORDER BY sentiment''').fetchall()
        negative = connection.execute('''SELECT post_id, sentiment FROM demo_posts
            WHERE sentiment = ? ORDER BY post_id''', ('negative',)).fetchall()
        print('Database:', DATABASE)
        print('Distinct saved posts:', total)
        print('Sentiment summary:', summary)
        print('Negative posts:', negative)
        assert len(appended) == 5 and total == 4
        assert summary == [('negative', 1), ('neutral', 1), ('positive', 2)]
        assert negative == [('demo-002', 'negative')]
        print('Checks passed. Repeating this collection keeps the same four IDs.')
    finally:
        connection.close()


if __name__ == '__main__':
    main()
