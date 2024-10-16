from models.user import User
from typing import List, Optional


def create_user(username: str, password: str,
                email: str, user_type: str, session) -> None:
    new_user = User(username=username,
                password=password,
                email=email,
                user_type=user_type)
    session.add(new_user) 
    session.commit() 
    session.refresh(new_user)
    return new_user

def get_all_users(session) -> List[User]:
    return session.query(User).all()

def get_user_by_name(name: str, session) -> Optional[User]:
    user = session.query(User).filter(User.username == name).first()
    if user:
        return user
    return None

def get_user_by_email(email: str, session):
    user = session.query(User).filter(User.email == email).first()
    if user:
        return user
    return None

def authenticate(email: str, password: str, session):
    user = session.query(User).filter(User.email == email and User.password == password).first()
    if user:
        return user
    return None


def get_user_by_id(id: int, session) -> Optional[User]:
    users = session.get(User, id) 
    if users:
        return users 
    return None