import pika
import time
import msgpack
import requests
from Judger import judger

# RabbitMQ connection parameters
connection_params = pika.ConnectionParameters('localhost')
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare the queue (necessary in consumer to ensure it exists)
channel.queue_declare(queue='submit_queue')

# Define the callback function
def submit_callback(ch, method, properties, body):
    print(f" [x] Received task in submit_worker")
    data = msgpack.unpackb(body)
    judge_result = judger.run_judger(
        judger_vol_path=r"PATH_TO_CONTAINER_VOL",
        language=data["language"],
        time_limit=data["time_limit"],
        memory_limit=data["memory_limit"],
        src_code=data["src_code"],
        std_in=data["std_in"],
        expected_out=data["expected_out"]
    ) 
    callback_url = data["callback_url"]
    print(f" [#] Status : {judge_result}") 
    print(f" [#] Sending PUT request on {callback_url} \n")
    requests.post(url=callback_url, json={"status": judge_result}, headers={'Content-Type': 'application/json'})

# Start consuming messages
channel.basic_consume(queue='submit_queue', on_message_callback=submit_callback, auto_ack=True)

print(' [*] Submit worker waiting for messages...')
channel.start_consuming()