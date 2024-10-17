import os
import pickle
import pandas as pd
from datetime import datetime
from models.prediction import Prediction

def load_model(model_path: str):
    if os.path.exists(model_path):
        with open(model_path, 'rb') as model_file:
            model = pickle.load(model_file)
    else:
        raise FileNotFoundError(f"Model file {model_path} \
                                not found.")
    return model


def process_request(model, user_id: int, data, project_name, session) -> dict:
    data = pd.DataFrame(data)
    prediction = make_prediction(project_name, model, data)
    save_prediction(user_id, data, prediction['predict'], prediction['succ_rate'], project_name, session)
    return prediction

def make_prediction(project_name, model, data):
    # print(data)
    # return data
    predict = model.predict(data)[0].item()
    succ_rate = model.predict_proba(data)[0][1]
    return {'predict': predict,
            'succ_rate': succ_rate,
            'data': data.to_json(orient='records')}


def save_prediction(user_id: int, request_data: pd.DataFrame,
                    prediction, succ_rate, project_name, session):
    print(f'user_id: {user_id},\n' \
      f'request_data: {request_data}, \n' \
      f'prediction: {prediction}, \n' \
      f'succ_rate: {succ_rate}, \n')
    print("Тип:", type(request_data))
    prediction_record = Prediction(
        user_id=user_id,
        project_name=project_name,
        request_data=request_data.to_json(),
        prediction=prediction,
        pred_rate=succ_rate,
        timestamp=datetime.now()
    )
    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

def get_prediction(user_id: int, session):
    return session.query(Prediction).filter(Prediction.user_id == user_id).all()