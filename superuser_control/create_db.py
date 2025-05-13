import psycopg

with psycopg.connect("host=localhost port=5432 dbname=password_appdb connect_timeout=10 password=masface123 "
                     "user=postgres") as conn:
    with conn.cursor() as c:
        sql_query = """CREATE TABLE users (
    uuid UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    salt TEXT NOT NULL
);

        """

        c.execute(sql_query)

        sql_query = """
        CREATE TABLE credentials (
    id SERIAL PRIMARY KEY,
    user_uuid UUID REFERENCES users(uuid) ON DELETE CASCADE,
    service VARCHAR(255) NOT NULL,  -- Encrypt if needed
    username_encrypted BYTEA,       -- Encrypted
    password_encrypted BYTEA NOT NULL,
    password_iv BYTEA NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
        """
        c.execute(sql_query)

        sql_query = """
        CREATE INDEX idx_credentials_user_uuid ON credentials(user_uuid);
        """
        c.execute(sql_query)
        conn.commit()

