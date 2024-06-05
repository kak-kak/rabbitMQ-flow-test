import pika
import time
import json
import datetime

# 接続の再試行ロジック
max_retries = 5
for i in range(max_retries):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        break
    except Exception as e:
        print(f"Connection attempt {i+1}/{max_retries} failed: {e}")
        time.sleep(5)  # 5秒待機
else:
    print("Failed to connect to RabbitMQ after several attempts.")
    exit(1)

channel = connection.channel()

# ファンアウト型の交換所を宣言
exchange_name = 'logs2'
channel.exchange_declare(exchange=exchange_name, exchange_type='fanout', durable=True)

# 一時的なキューを宣言（RabbitMQが自動生成するキュー）
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# キューをファンアウト型の交換所にバインド
channel.queue_bind(exchange=exchange_name, queue=queue_name)

# 平均値を発行する交換所の設定
output_exchange_name = 'value1_exchange'
channel.exchange_declare(exchange=output_exchange_name, exchange_type='fanout', durable=True)

print('Waiting for messages. To exit press CTRL+C')

# 直近10個のSensor0の値を保持するリスト
sensor0_values = []

def callback(ch, method, properties, body):
    global sensor0_values
    try:
        sensor_data = json.loads(body.decode())
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"Received sensor data {date}: {sensor_data}")

        # Sensor0の値を取得しリストに追加
        sensor0_values.append(sensor_data[0]['sensor0'])
        if len(sensor0_values) > 10:
            sensor0_values.pop(0)

        # 直近10個のSensor0の平均値を計算
        if len(sensor0_values) == 10:
            average_value = sum(sensor0_values) / len(sensor0_values)
            value1_message = json.dumps({'value1': average_value})

            # 平均値を新しい交換所に発行
            channel.basic_publish(
                exchange=output_exchange_name,
                routing_key='',
                body=value1_message,
                properties=pika.BasicProperties(content_type='application/json')
            )
            print(f"Published value1: {value1_message}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
