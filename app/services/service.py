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


def process_request(model, user_id: int, data, session):
    data = pd.DataFrame([data])
    prediction = make_prediction(model, data)
    # print(f"made prediction: {prediction}")
    save_prediction(user_id, data, prediction['predict'], prediction['succ_rate'], session)
    # print(f"saved predictions")

def make_prediction(model, data):
    # print(data)
    # return data
    return {'predict': model.predict(data)[0].item(),
            'succ_rate': model.predict_proba(data)[0].item(),
            'data': data}


def save_prediction(user_id: int, request_data: pd.DataFrame,
                    prediction, succ_rate, session):
    prediction_record = Prediction(
        user_id=user_id,
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