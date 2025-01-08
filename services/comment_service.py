from psycopg2.extensions import connection as Connection
from typing import List
from schemas.comment_schema import CommentCreate, CommentResponse

class CommentService:
    @staticmethod
    def add_comment(db: Connection, comment: CommentCreate) -> dict:
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO comments (post_id, text, username) VALUES (%s, %s, %s) RETURNING id, time_created",
                (comment.post_id, comment.text, comment.username)
            )
            result = cursor.fetchone()  # Returns a tuple (id, time_created)
            db.commit()
            return {"id": result[0], "time_created": result[1]}  # Return both fields
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @staticmethod
    def get_comments_by_post(db: Connection, post_id: int) -> List[CommentResponse]:
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT id, post_id, text, username, time_created FROM comments WHERE post_id = %s ORDER BY time_created ASC",
                (post_id,)
            )
            rows = cursor.fetchall()
            return [
                CommentResponse(
                    id=row[0],
                    post_id=row[1],
                    text=row[2],
                    username=row[3],
                    time_created=row[4]
                )
                for row in rows
            ]
        except Exception as e:
            raise e
        finally:
            cursor.close()
