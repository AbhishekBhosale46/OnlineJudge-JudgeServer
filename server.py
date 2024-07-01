from fastapi import FastAPI
from pydantic import BaseModel
import pika
import msgpack


# RabbitMQ connection parameters
RABBITMQ_HOST = 'localhost'
RUN_EXCHANGE = 'run_exchange'
SUBMIT_EXCHANGE = 'submit_exchange'
RUN_ROUTING_KEY = 'run_queue_key'
SUBMIT_ROUTING_KEY = 'submit_queue_key'


# RabbitMQ connection parameters
connection_params = pika.ConnectionParameters(RABBITMQ_HOST)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()


# Declare exchanges
channel.exchange_declare(exchange=RUN_EXCHANGE, exchange_type='direct')
channel.exchange_declare(exchange=SUBMIT_EXCHANGE, exchange_type='direct')


# Declare queues
channel.queue_declare(queue='run_queue')
channel.queue_declare(queue='submit_queue')


# Bind queues to exchanges with specific routing keys
channel.queue_bind(exchange=RUN_EXCHANGE, queue='run_queue', routing_key=RUN_ROUTING_KEY)
channel.queue_bind(exchange=SUBMIT_EXCHANGE, queue='submit_queue', routing_key=SUBMIT_ROUTING_KEY)


# Publish messages
def publish_message(exchange, routing_key, body):
    message = msgpack.packb(body)
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
    print(f" [x] Sent message to {exchange} with routing key '{routing_key}'")


# Submit request pydantic model
class SubmitRequest(BaseModel):
    language: str
    time_limit: int
    memory_limit: int
    src_code: str
    std_in: str = " "
    expected_out: str
    callback_url: str


# Run request pydantic model
class RunRequest(BaseModel):
    language: str
    time_limit: int
    memory_limit: int
    src_code: str
    std_in: str = " "
    callback_url: str


app = FastAPI()


# Submit route
@app.post('/submit')
async def submit(submit_request: SubmitRequest):
    publish_message(SUBMIT_EXCHANGE, SUBMIT_ROUTING_KEY, body=submit_request.dict())
    return {"msg": "submit task enqueued, result will be available at the callback server"}


# Run route
@app.post('/run')
async def run(run_request: RunRequest):
    publish_message(RUN_EXCHANGE, RUN_ROUTING_KEY, body=run_request.dict())
    return {"msg": "run task enqueued, result will be available at the callback server"}