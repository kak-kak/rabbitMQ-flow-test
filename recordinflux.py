import pika
from influxdb import InfluxDBClient
import json
import time

# RabbitMQの接続設定
rabbitmq_host = 'rabbitmq'
rabbitmq_queue = 'my_queue'

# InfluxDBの接続設定
influxdb_host = 'influxdb'
influxdb_port = 8086
influxdb_user = 'root'
influxdb_password = 'root'
influxdb_dbname = 'mydb'

# InfluxDBクライアントの初期化
client = InfluxDBClient(host=influxdb_host, port=influxdb_port, username=influxdb_user, password=influxdb_password)
client.create_database(influxdb_dbname)
client.switch_database(influxdb_dbname)

# メッセージを受信してInfluxDBに保存するコールバック関数
def callback(ch, method, properties, body):
    data = json.loads(body)
    timestamp = data.get('timestamp', time.time() * 1000)  # タイムスタンプがない場合は現在時刻を使用
    json_body = [
        {
            "measurement": "rabbitmq_data",
            "tags": {
                "source": "rabbitmq"
            },
            "time": int(timestamp),
            "fields": {
                "value": body.decode()
            }
        }
    ]
    client.write_points(json_body)
    print(f"Data written to InfluxDB: {json_body}")

# RabbitMQの接続とキューの設定
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
channel.queue_declare(queue=rabbitmq_queue)

# RabbitMQキューからのメッセージ受信設定
channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
