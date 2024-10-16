from database.config import get_settings
from database.database import get_session, init_db, engine
from sqlmodel import Session
from models.user import User
from services.user import create_user, get_all_users
from services.service import load_model, process_request, make_prediction, save_prediction

if __name__ == "__main__":
    test_user = User(username="john_doe", password='test', email='test@mail.ru', user_type='startup', fr_model_type='free')
    test_user_2 = User(username="john_doe_2", password='test', email='test_2@mail.ru', user_type='business', fr_model_type='advanced')
    test_user_3 = User(username="john_doe_3", password='test', email='test_3@mail.ru', user_type='market', fr_model_type='free')

    init_db()
    print("Init db successful")
    
    with Session(engine) as session:
        create_user(test_user, session)
        create_user(test_user_2, session)
        create_user(test_user_3, session)
        users = get_all_users(session)

    for user in users:
        print(f'id: {user.id} - {user.email}')