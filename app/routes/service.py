from fastapi import APIRouter, Depends
from databases.database import get_session
from databases.config import get_settings
import services.gpt as serpg
from models.request import PredictItem
from models.prediction import Prediction
from services import service as ModelService
from typing import List
import uuid
import pika
import json


# Загружаем необходимые найстройки, модели и т.п.
settings = get_settings()
encoder = serpg.load_encoder_rf(settings.ENCODER_RF_PATH)
model = serpg.load_model(settings.MODEL_PATH)
mean_cat = serpg.load_mean_dict(settings.ENCODED_CATEGORY_PATH)

connection_params = pika.ConnectionParameters(
    host=settings.RABBITMQ_HOST,  # Замените на адрес вашего RabbitMQ сервера
    port=int(settings.RABBITMQ_PORT),          # Порт по умолчанию для RabbitMQ
    virtual_host='/',   # Виртуальный хост (обычно '/')
    credentials=pika.PlainCredentials(
        username=settings.RABBITMQ_DEFAULT_USER,  # Имя пользователя
        password=settings.RABBITMQ_DEFAULT_PASS,   # Пароль
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)


service_route = APIRouter(tags=['Service'])

@service_route.post('/process_request/{user_id}', response_model=dict)
def create_process(user_id: int, dataset: PredictItem):
    # ModelService.process_request(mlservice, user_id, data, session)
    data = dataset.model_dump()


    message = {'user_id': user_id, 'data': data}
    req_id = str(uuid.uuid4())
    response_queue = 'response_queue_' + req_id
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue=response_queue, exclusive=True)

    def on_response(ch, method, properties, body):
        if properties.correlation_id == req_id:
            global response
            response = json.loads(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()

    channel.basic_consume(queue=response_queue,
                          on_message_callback=on_response,
                          auto_ack=False)
    channel.basic_publish(
        exchange='',
        routing_key='ML_queue',
        body=json.dumps(message),
        properties=pika.BasicProperties(reply_to=response_queue,
                                        correlation_id=req_id))

    channel.start_consuming()
    print('Message send, waiting for response from worker')
    connection.close()

    return {'prediction': "made successfully",
            'features': data}

@service_route.get("/prediction_history/{user_id}", response_model=List[Prediction])
def pred_hist(user_id: int, session=Depends(get_session)) -> List[Prediction]:
    return ModelService.get_prediction(user_id, session)

@service_route.get("/predictions", response_model=List[Prediction])
def pred_hist(session=Depends(get_session)) -> List[Prediction]:
    return ModelService.view_all_predictions(session)
