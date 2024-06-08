FROM python:3.9-slim

RUN pip install pika

COPY . /usr/src

CMD ["sh", "-c", "sleep 5 && python /usr/src/worker.py"]