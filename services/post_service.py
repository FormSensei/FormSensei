from typing import List, Optional
from sqlite3 import Connection
from schemas.post_schema import PostCreate, PostResponse
import logging

logger = logging.getLogger(__name__)

class PostService:
    @staticmethod
    def add_post(db: Connection, post: PostCreate) -> int:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO posts (image, text, user) VALUES (?, ?, ?)",
            (post.image, post.text, post.user)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_post(db: Connection, post_id: int) -> Optional[PostResponse]:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        row = cursor.fetchone()
        if row:
            return PostResponse(**row)
        return None

    @staticmethod
    def list_posts(db: Connection, page: int, limit: int) -> List[PostResponse]:
        offset = (page - 1) * limit
        logger.info(f"Fetching posts from DB with offset={offset}, limit={limit}")
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset))
            rows = cursor.fetchall()
            logger.info(f"Posts fetched from DB: {len(rows)}")
            return [PostResponse(**row) for row in rows]
        except Exception as e:
            logger.error(f"Error querying posts from DB: {e}")
            raise
