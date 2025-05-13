import psycopg

with psycopg.connect("host=localhost port=5432 dbname=postgres connect_timeout=10 password=masface123 user=postgres") as conn:
    with conn.cursor() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS test (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            number integer
            )
        """)

        c.execute("""
            INSERT INTO test (username,number) VALUES (%s, %s)
        """, ('giorj', 132))

        c.execute("""
            SELECT * FROM test
        """)

        print(c.fetchone())

        c.executemany("""
        INSERT INTO test (username, number) VALUES(%s, %s)
        """, [
            ('dian', 12),
            ('chris', 0),
            ('michael', 99)
        ])

        conn.commit()

