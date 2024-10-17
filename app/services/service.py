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


def process_request(model, data) -> dict:
    data = pd.DataFrame(data)
    prediction = make_prediction(model, data)
    return prediction

def make_prediction(model, data):
    json_result = data.to_json(orient='records')
    predict = model.predict(data)[0].item()
    succ_rate = model.predict_proba(data)[0][1]
    return {'predict': predict,
            'succ_rate': succ_rate,
            'data': data}


def save_prediction(user_id: int, request_data: pd.DataFrame,
                    prediction: int, succ_rate: float, project_name: str, analysis: str, session):
    print(f'user_id: {user_id},\n' \
      f'request_data: {request_data}, \n' \
      f'prediction: {prediction}, \n' \
      f'succ_rate: {succ_rate}, \n' \
      f'analysis: {analysis}, \n')
    print("Тип:", type(request_data))
    prediction_record = Prediction(
        user_id=user_id,
        project_name=project_name,
        request_data=request_data,
        prediction=prediction,
        pred_rate=succ_rate,
        analysis=analysis,
        timestamp=datetime.now()
    )
    session.add(prediction_record)
    session.commit()
    session.refresh(prediction_record)

def get_prediction(user_id: int, session):
    return session.query(Prediction).filter(Prediction.user_id == user_id).all()