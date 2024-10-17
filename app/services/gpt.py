import openai
import json
from g4f.client import Client
import pandas as pd
from fastapi import HTTPException
from databases.config import get_settings
import joblib
import asyncio

settings = get_settings()

def get_response(sys_content: str, usr_content: str, model: str):
    client = Client()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_content},
            {"role": "user", "content": usr_content}
        ],
        # stream=True
    )
    return completion.choices[0].message.content


def process_row(row, sys_content, model):
    categories = get_response(sys_content, row, model)
    if categories:
        try:
            # Пробуем распарсить JSON
            startup_info = json.loads(categories)
            return startup_info  # Возвращаем индекс и данные
        except json.JSONDecodeError:
            # Если ошибка JSON, возвращаем индекс и None
            return None  
    return None 

def load_encoder_rf(path):
    """Загружает кодировщик из файла"""
    return joblib.load(path)

def load_model(path):
    """Загружает обученную модель"""
    return joblib.load(path)

def load_mean_dict(path):
    """Загружает закодированные по среднему категории"""
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def preprocess_features(data, category_mean):
    """Преобразовывает и подготовливает данные"""
    features = {}
    features['Nums_backed'] = int(data['num_projects_backed'])
    features['Nums_created'] = int(data['num_projects_created'])
    features['goal'] = int(data['goal_amount'])
    features['staff_pick'] = int(data['staff_pick'])
    features['name_len'] = len(data['project_name'].split())

    features['category_target_encoding'] = category_mean.get(data['category'], 0.5)

    # Преобразование дат
    create_date = pd.to_datetime(data['created_date'])
    launch_date = pd.to_datetime(data['launch_date'])
    deadline_date = pd.to_datetime(data['deadline_date'])
    features['create_launch'] = (launch_date - create_date).days
    features['launch_deadline'] = (deadline_date - launch_date).days
    features['launch_month_encoded'] = launch_date.month
    features['launch_weekday_encoded'] = launch_date.weekday()

    return features

def process_startup_info(data: dict, model_content: str, model_name: str) -> dict:
    """Processes the startup description and returns GPT analysis asynchronously."""
    startup_info = "Startup Description: " + data['project_description'] + " Founder Information: " + data['creator_description']
    json_data = process_row(startup_info, model_content, model_name)

    # Retry until valid response is obtained
    while json_data is None:
        json_data = process_row(startup_info, model_content, model_name)

    return json_data


def ready_features(data: dict, encoder, model, category_mean: dict, model_content: str, model_name: str, train_columns: list, category_mapp: dict) -> pd.DataFrame:
    """Filters the data and prepares it for model fitting."""
    json_data = process_startup_info(data, model_content, model_name)
    print("----------------Вызван получение json----------------------")
    
    # Process startup data
    if 'startup_analysis_responses' in json_data:
        startup_analysis_responses = json_data['startup_analysis_responses']
        json_df = pd.DataFrame([startup_analysis_responses])
    else:
        raise HTTPException(status_code=400, detail="'startup_analysis_responses' key not found in json_data.")

    for column, categories in category_mapp.items():
        json_df[column] = json_df[column].apply(lambda x: x if x in categories else "No answer")

    encoded_data = encoder.transform(json_df)[0]
    combined_df = pd.DataFrame({**dict(zip(json_df.columns, encoded_data)), **preprocess_features(data, category_mean)}, index=[0])

    # Filter columns
    filtered_dict = {key: combined_df[key] for key in train_columns if key in combined_df}
    return filtered_dict