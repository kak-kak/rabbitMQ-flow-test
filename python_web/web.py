import pika
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading
import time

# AMQP
EXCHANGE_NAME = 'value1_exchange'  
IS_DURABLE = True  
KEY_OF_DISPLAY_VALUE_IN_JSON = "value1"

# HTML
HTML_FILE_NAME = "index.html"

app = FastAPI()

def connect_to_rabbitmq():
    max_retries = 5
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            return connection
        except Exception as e:
            print(f"Connection attempt {i+1}/{max_retries} failed: {e}")
            time.sleep(5)
    print("Failed to connect to RabbitMQ after several attempts.")
    exit(1)

connection = connect_to_rabbitmq()
channel = connection.channel()

channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout', durable=IS_DURABLE)

result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name)

latest_value = "No value"

def consume_messages():
    global latest_value

    def callback(ch, method, properties, body):
        global latest_value
        value_data = json.loads(body.decode())
        latest_value = value_data[0]
        print(f"Received {KEY_OF_DISPLAY_VALUE_IN_JSON}: {value_data}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

threading.Thread(target=consume_messages, daemon=True).start()

@app.get("/", response_class=HTMLResponse)
async def get():
    with open(HTML_FILE_NAME, "r") as file:
        html = file.read()
    return HTMLResponse(content=html, status_code=200)

@app.get("/value")
async def get_value():
    global latest_value
    return {"value": latest_value}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
