import pika
import time

class PubInSubExchangeHandler:
    def __init__(self, exchange_name_sub, exchange_name_pub, callback, state) -> None:
        self.exchange_name_sub = exchange_name_sub
        self.exchange_name_pub = exchange_name_pub
        self.callback = callback
        self.state = state
        self.try_connect()
        self.resister_sub_exchange()
        self.resister_pub_exchange()
        self.start_sub()

    def try_connect(self):                
        max_retries = 5
        for i in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
                break
            except Exception as e:
                print(f"Connection attempt {i+1}/{max_retries} failed: {e}")
                time.sleep(5)  
        else:
            print("Failed to connect to RabbitMQ after several attempts.")
            exit(1)
            
    def resister_sub_exchange(self):
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=self.exchange_name_sub, exchange_type='fanout', durable=True)
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.queue_name = result.method.queue
        self.channel.queue_bind(exchange=self.exchange_name_sub, queue=self.queue_name)
    
    def resister_pub_exchange(self):
        self.channel.exchange_declare(exchange=self.exchange_name_pub, exchange_type='fanout', durable=True)
        print('Waiting for messages. To exit press CTRL+C')

    def start_sub(self):
        self.sensor0_values = []
        self.val = 0

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback_wrapper, auto_ack=True)
        self.channel.start_consuming()

    def callback_wrapper(self, ch, method, properties, body):
        self.callback(ch, method, properties, body, self)
