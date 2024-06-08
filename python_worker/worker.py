import pika
import time
import json
import datetime
from pubInSubExchangeHandler import PubInSubExchangeHandler

EXCHANGE_NAME_SUB = 'logs2'
EXCHANGE_NAME_PUB = 'value1_exchange'

def start_worker():  

    def callback(ch, method, properties, body, handler):
        try:
            sensor_data = json.loads(body.decode())
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            print(f"Received sensor data {date}: {sensor_data}")
            
            handler.state["sensor0_values"].append(sensor_data[0]['sensor0'])
            if len(handler.state["sensor0_values"]) > 10:
                handler.state["sensor0_values"].pop(0)

            if len(handler.state["sensor0_values"]) == 10:
                
                # value1_message = json.dumps({'value1': handler.state["val"]})
                value1_message = json.dumps([handler.state["val"], handler.state["val"]])
                handler.state["val"] = handler.state["val"] + 1

                handler.channel.basic_publish(
                    exchange=EXCHANGE_NAME_PUB,
                    routing_key='',
                    body=value1_message,
                    properties=pika.BasicProperties(content_type='application/json')
                )
                print(f"Published value1: {value1_message}")
                
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

    state = {
        'sensor0_values': [],
        'val': 0
    }

    PubInSubExchangeHandler(EXCHANGE_NAME_SUB, EXCHANGE_NAME_PUB, callback, state)

if __name__ == "__main__":
    start_worker()