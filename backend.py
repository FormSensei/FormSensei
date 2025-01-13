import psycopg2

# Establish connection to the PostgreSQL database
def get_db():
    conn = psycopg2.connect(
        dbname="mydb",
        user="myuser",
        password="mypassword",
        host="db",  # Matches the name of the PostgreSQL service in docker-compose.yml
        port=5432
    )
    return conn

# Function to add a post to the database
def add_post(conn, image, text, username):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO posts (image, text, username) VALUES (%s, %s, %s)",
            (image, text, username)
        )
        conn.commit()
        print("Post added successfully!")
    except Exception as e:
        print(f"Error adding post: {e}")
        conn.rollback()
    finally:
        cursor.close()

# Function to fetch the latest post
def get_latest_post(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM posts ORDER BY time_created DESC, id DESC LIMIT 1")
        post = cursor.fetchone()
        if post:
            return {
                "id": post[0],
                "image": post[1],
                "text": post[2],
                "username": post[3],
                "time_created": post[4]
            }
        else:
            return "No posts found."
    except Exception as e:
        print(f"Error fetching the latest post: {e}")
    finally:
        cursor.close()

# Sample posts to insert
posts = [
    {"image": "image1.jpg", "text": "First post!", "username": "User1"},
    {"image": "image2.jpg", "text": "Here's another post.", "username": "User2"},
    {"image": "image3.jpg", "text": "Third time's the charm.", "username": "User3"}
]

# Main block to insert posts and fetch the latest post
if __name__ == "__main__":
    conn = get_db()
    try:
        # Insert sample posts
        for post in posts:
            add_post(conn, post["image"], post["text"], post["username"])

        # Fetch the latest post
        latest_post = get_latest_post(conn)
        print("Latest post:", latest_post)
    finally:
        conn.close()
