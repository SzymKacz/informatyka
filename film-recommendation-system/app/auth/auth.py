import bcrypt
from db.db import get_user, create_user

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username: str, password: str) -> bool:
    if get_user(username) is not None:
        return False
    create_user(username, hash_password(password))
    return True

def login_user(username: str, password: str):
    user = get_user(username)
    if user is None:
        return None
    if not check_password(password, user["password_hash"]):
        return None
    return user  # <- zwracamy cały rekord