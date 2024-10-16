FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app/

RUN pip install dvc

EXPOSE 8080

# COPY entrypoint.sh /app/entrypoint.sh

# ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "api.py"]