from typing import Optional, List
from sqlite3 import Connection
from schemas.authentication_schema import Authentication

class AuthenticationService:
    @staticmethod
    def authenticate_user(db: Connection, authentication: Authentication) -> bool:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT password FROM users WHERE username = %s", (authentication.username,))
            row = cursor.fetchone()
            return row[0] == authentication.password
        except Exception as e:
            return False