import psycopg2
from psycopg2 import sql


def get_db():
    conn = psycopg2.connect(
        dbname="mydb",
        user="myuser",
        password="mypassword",
        host="db",  # This should match the name of the service in docker-compose.yml
        port=5432
    )
    return conn


async def init_db():
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Create 'posts' table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            image TEXT,
            text TEXT,
            username TEXT,  -- Changed from "user"
            time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
        print("Table 'posts' created or already exists.")

        # Create 'users' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password TEXT
            )
        ''')
        print("Table 'users' created or already exists.")

        # Create 'comments' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES posts(id),
                text TEXT NOT NULL,
                username TEXT NOT NULL,  -- Renamed from "user" to "username"
                time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("Table 'comments' created or already exists.")

        conn.commit()
        print("All tables initialized successfully.")

    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()

    finally:
        conn.close()
