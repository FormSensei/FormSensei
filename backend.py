import sqlite3

conn = sqlite3.connect("posts.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image TEXT,
        text TEXT,
        user TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

def add_post(conn, image, text, user):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (image, text, user) VALUES (?, ?, ?)", (image, text, user))
    conn.commit()
    print("Post added successfully!")

def get_latest_post(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC, id DESC LIMIT 1")
    post = cursor.fetchone()
    if post:
        return {
            "id": post[0],
            "image": post[1],
            "text": post[2],
            "user": post[3],
            "timestamp": post[4]
        }
    else:
        return "No posts found."

posts = [
    {"image": "image1.jpg", "text": "First post!", "user": "User1"},
    {"image": "image2.jpg", "text": "Here's another post.", "user": "User2"},
    {"image": "image3.jpg", "text": "Third time's the charm.", "user": "User3"}
]

for post in posts:
    add_post(conn, post["image"], post["text"], post["user"])

latest_post = get_latest_post(conn)
print("Latest post:", latest_post)

conn.close()

# testing test.yml