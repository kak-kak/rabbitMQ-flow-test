import pika
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading
import time

app = FastAPI()

# Connect to RabbitMQ
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

# Declare the exchange
output_exchange_name = 'value1_exchange'
channel.exchange_declare(exchange=output_exchange_name, exchange_type='fanout', durable=True)

# Declare a temporary queue
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# Bind the queue to the exchange
channel.queue_bind(exchange=output_exchange_name, queue=queue_name)

# Variable to store the latest value
latest_value = "No value"

def consume_messages():
    global latest_value

    def callback(ch, method, properties, body):
        global latest_value
        value_data = json.loads(body.decode())
        latest_value = value_data.get('value1', "No value")
        print(f"Received value1: {latest_value}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

# Start consuming messages in a separate thread
threading.Thread(target=consume_messages, daemon=True).start()

# HTML template
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Direction Compass</title>
    <style>
        #compass {
            width: 300px;
            height: 300px;
            border: 2px solid black;
            border-radius: 50%;
            position: relative;
            margin: 50px auto;
        }

        #arrow {
            width: 0;
            height: 0;
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-bottom: 50px solid red;
            position: absolute;
            top: 50%;
            left: 50%;
            transform-origin: bottom center;
            transform: translate(-50%, -100%);
        }
    </style>
    <script>
        function updateDirection() {
            fetch('/value')
                .then(response => response.json())
                .then(data => {
                    const direction = data.value * 10;
                    const arrow = document.getElementById('arrow');
                    arrow.style.transform = `translate(-50%, -100%) rotate(${direction}deg)`;
                });
        }
        setInterval(updateDirection, 2000); // Update every second
    </script>
</head>
<body>
    <div id="compass">
        <div id="arrow"></div>
    </div>
</body>
</html>
"""

# Endpoint to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def get():
    return HTMLResponse(content=html, status_code=200)

# Endpoint to get the latest value
@app.get("/value")
async def get_value():
    global latest_value
    return {"value": latest_value}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
