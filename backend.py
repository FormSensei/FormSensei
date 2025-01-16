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
def add_post(conn, image_full, image_reduced, text, username):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO posts (image_full, image_reduced, text, username) VALUES (%s, %s, %s, %s)",
            (image_full, image_reduced, text, username)
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
                "image_full": post[1],
                "image_reduced": post[2],
                "text": post[3],
                "username": post[4],
                "time_created": post[5]
            }
        else:
            return None
    except Exception as e:
        print(f"Error fetching the latest post: {e}")
    finally:
        cursor.close()


# Sample posts with full-size and reduced-size images
posts = [
    {"image_full": "uploads/image1.jpg", "image_reduced": "uploads/reduced/image1.jpg", "text": "First post!", "username": "User1"},
    {"image_full": "uploads/image2.jpg", "image_reduced": "uploads/reduced/image2.jpg", "text": "Second post!", "username": "User2"},
    {"image_full": "uploads/image3.jpg", "image_reduced": "uploads/reduced/image3.jpg", "text": "Third post!", "username": "User3"},
]

if __name__ == "__main__":
    conn = get_db()
    try:
        # Insert sample posts
        for post in posts:
            add_post(conn, post["image_full"], post["image_reduced"], post["text"], post["username"])
            print(f"Inserted post: {post}")

        # Fetch the latest post
        latest_post = get_latest_post(conn)
        print("Latest post:", latest_post)
    finally:
        conn.close()
