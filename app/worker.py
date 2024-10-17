import pika
import json
import pandas as pd
import os
from dotenv import load_dotenv
from databases.database import get_session
from databases.database import get_settings
from routes.config import MODE, MODEL_NAME, MODEL_CONTENT_PREPROC, TRAIN_COLUMNS, CATEGORY_MAPPINGS
from services import service as ModelService
import services.gpt as serpg

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
    blocked_connection_timeout=4
)

model_path = settings.MODEL_PATH
model = ModelService.load_model(model_path)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = 'ML_queue'
channel.queue_declare(queue=queue_name)

def callback(ch, method, properties, body):
    # print(body)
    body = json.loads(body)
    
    # print(body)
    # features = pd.DataFrame([body['data'].dict()])
    with next(get_session()) as session:
        features, data_prep = serpg.ready_features(data=body['data'],
                                    encoder=encoder, 
                                    category_mean=mean_cat,
                                    model_content=MODEL_CONTENT_PREPROC,
                                    model_name=MODEL_NAME,
                                    train_columns=TRAIN_COLUMNS,
                                    category_mapp=CATEGORY_MAPPINGS)
        print(features)
        print("----------------Данные обработаны и отправлены----------------------")
        process_response = ModelService.process_request(model,features)
        print("----------------Ответ от модели получен----------------------")
        product_analyse = serpg.product_analysis(startup_info=data_prep, mode=MODE, model=MODEL_NAME)
        creator_analyse = serpg.creator_analysis(startup_info=data_prep, mode=MODE, model=MODEL_NAME)
        process_response['recommendations'] = serpg.integrate_analyses(product_analyse,
                                                                       creator_analyse,
                                                                       process_response['predict'],
                                                                       process_response['succ_rate'],
                                                                       mode=MODE,
                                                                       model=MODEL_NAME) 
        print("----------------Анализ и рекомендации построены----------------------")
        ModelService.save_prediction(body['user_id'],
                                     features,
                                     process_response['predict'],
                                     process_response['succ_rate'],
                                     body['data']['project_name'],
                                     process_response['recommendations'],
                                     session)
        print("----------------Сохранение рекомендации----------------------")
    # if isinstance(process_response, pd.DataFrame):
    #     process_response = process_response.to_dict(orient='records')
    print(process_response['recommendations'])
    response_channel = connection.channel()
    response_channel.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        body=json.dumps(process_response),
        properties=pika.BasicProperties(
            correlation_id=properties.correlation_id
            )
    )
    response_channel.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    channel.basic_consume(queue=queue_name,
                          on_message_callback=callback,
                          auto_ack=False)
    print('Waiting for messages')
    channel.start_consuming()

