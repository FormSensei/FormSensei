from sqlite3 import Connection
from typing import List
from schemas.comment_schema import CommentCreate, CommentResponse

class CommentService:
    @staticmethod
    def add_comment(db: Connection, comment: CommentCreate) -> int:
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO comments (post_id, text, user) VALUES (?, ?, ?)",
            (comment.post_id, comment.text, comment.user)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_comments_by_post(db: Connection, post_id: int) -> List[CommentResponse]:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM comments WHERE post_id = ? ORDER BY time_created ASC", (post_id,))
        rows = cursor.fetchall()
        return [CommentResponse(**row) for row in rows]
