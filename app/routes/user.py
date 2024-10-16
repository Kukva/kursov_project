from fastapi import APIRouter, HTTPException, status, Depends
from databases.database import get_session
from models.user import User
from services import user as UserService
from typing import List

user_route = APIRouter(tags=['User'])

@user_route.post('/signup')
async def signup(username: str,password: str,
                 email: str, user_type: str,
                 session=Depends(get_session)) -> dict:
    if UserService.get_user_by_email(email, session) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with supplied email exists")
    if UserService.get_user_by_name(username, session) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with supplied username exists")
    
    user = UserService.create_user(username, password,
                                   email, user_type,
                                   session)
    return {
        "message": "User successfully registered!",
        "user_id": user.id 
    }

@user_route.post('/signin')
async def signin(email: str, password: str, session=Depends(get_session)) -> dict:
    user = UserService.authenticate(email, password, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    else:
        return {"message": "User signed in successfully",
                "user_id": user.id,
                "user_type": user.user_type}

@user_route.get('/all', response_model=List[User])
async def get_all_users(session=Depends(get_session)) -> list:
    return UserService.get_all_users(session)

@user_route.get('/users', response_model=List[User])
async def get_all_users(session=Depends(get_session)) -> list:
    return UserService.get_all_users(session)

@user_route.post('/add_credits/{user_id}')
def add_credits(user_id: int, amount: int, session=Depends(get_session)) -> dict:
    UserService.plus_balance(user_id, amount, session)
    return {f"Added to {user_id} user": f"{amount} credits"}

@user_route.get('/balance/{user_id}')
def show_balance(user_id: int, session=Depends(get_session)) -> dict:
    user = UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {user_id: user.balance}
    # balance = UserService.get_balance(user_id, session)
    # return {user_id: balance}