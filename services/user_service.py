from typing import Optional, List
from sqlite3 import Connection
from schemas.user_schema import UserCreate, UserResponse

class UserService:
    @staticmethod
    def add_user(db: Connection, user: UserCreate) -> int:
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (user.username, user.email, user.password)
            )
            db.commit()
            return cursor.lastrowid
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create user: {e}")

    @staticmethod
    def get_user_by_id(db: Connection, user_id: int) -> Optional[UserResponse]:
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        if row:
            return UserResponse(**row)
        return None

    @staticmethod
    def search_users(db: Connection, username: Optional[str], email: Optional[str], page: int, limit: int) -> List[UserResponse]:
        query = "SELECT id, username, email FROM users WHERE 1=1"
        params = []

        if username:
            query += " AND username LIKE %s"
            params.append(f"%{username}%")
        if email:
            query += " AND email LIKE %s"
            params.append(f"%{email}%")

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, (page - 1) * limit])

        cursor = db.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [UserResponse(**row) for row in rows]
    
    @staticmethod
    def authenticate_user(db: Connection, username: str, password: str):
        cursor = db.cursor()
        try:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            row = cursor.fetchone()
            return row[0] == password
        except Exception as e:
            return False