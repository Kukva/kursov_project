from models.userr import Userr
from typing import List, Optional


def create_user(username: str, password: str,
                email: str, user_type: str, session) -> None:
    new_user = Userr(username=username,
                password=password,
                email=email,
                user_type=user_type)
    session.add(new_user) 
    session.commit() 
    session.refresh(new_user)
    return new_user

def get_all_users(session) -> List[Userr]:
    return session.query(Userr).all()

def get_user_by_name(name: str, session) -> Optional[Userr]:
    user = session.query(Userr).filter(Userr.username == name).first()
    if user:
        return user
    return None

def get_user_by_email(email: str, session):
    user = session.query(Userr).filter(Userr.email == email).first()
    if user:
        return user
    return None

def authenticate(email: str, password: str, session):
    user = session.query(Userr).filter(Userr.email == email and Userr.password == password).first()
    if user:
        return user
    return None


def get_user_by_id(id: int, session) -> Optional[Userr]:
    users = session.get(Userr, id) 
    if users:
        return users 
    return None