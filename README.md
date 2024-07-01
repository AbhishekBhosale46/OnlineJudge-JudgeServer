# Judge Server

The Judge Server is a REST API built using FastAPI for executing user code asynchronously. This server takes user-submitted code along with required parameters and assigns the execution tasks to workers via RabbitMQ. Upon completion, the workers make a POST request to callback URL provided in the request to return the status of the executed task.

This Judge Server is a wrapper REST api for the [Judger System](https://github.com/AbhishekBhosale46/onlineJudge-Judger/).


## Features

- Asynchronous processing of user-submitted code.
  
- Uses RabbitMQ to assign tasks to workers.

- Horizontal scalability of workers.

- Callback mechanism to notify the status of task execution.


## Horizontal Scalability

The system is designed to scale horizontally by adding more workers. Since tasks are assigned via RabbitMQ, you can easily add more worker instances to handle increased loads. Each worker listens to the same queue and processes tasks concurrently.

To add more workers, simply start additional instances of the worker process. Ensure that each worker is configured to connect to the same RabbitMQ server and listen to the same queue.

## Technologies Used
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![RabbitMQ](https://img.shields.io/badge/Rabbitmq-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

![Judge Server System Diagram](https://github.com/AbhishekBhosale46/OnlineJudge-JudgeServer/assets/58450561/c365ba52-4525-4809-8240-818790b8d91e)


## Installation

Clone the project

```bash
git clone https://github.com/AbhishekBhosale46/OnlineJudge-JudgeServer
```

Install dependencies

```bash
pip install requirements.txt
```

Start the Judge Server

```bash
uvicorn server:app --host 127.0.0.1 --port 9000 --reload
```

Start the submit and run task worker
```bash
python worker/submit_worker.py
python worker/run_worker.py
```
## Usage

### Submitting a Task

To submit a task, make a POST request to the /submit or /run endpoint.

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/submit' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "language": "string",
  "time_limit": 0,
  "memory_limit": 0,
  "src_code": "string",
  "std_in": " ",
  "expected_out": "string",
  "callback_url": "string"
}'

```

### Receiving the Callback

The worker will execute the submitted code and send a POST request to the provided callback_url with the following JSON body:

```bash
{
  "status": "AC | WA | TLE | MLE | RE | CE",
}
```

## API Reference

#### Make submit code request

```https
  POST /submit
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `language` | `string` | Language of the source code |
| `time_limit` | `int` | Time limit in seconds |
| `memory_limit` | `int` | Memory limit in mb |
| `src_code` | `string` | Code to run on the server |
| `std_in` | `string` | Standard input to the program |
| `expected_out` | `string` | Expected output of the program |
| `callback_url` | `string` | Url where POST request will be made by worker |

#### Make run code request

```https
  POST /run
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `language` | `string` | Language of the source code |
| `time_limit` | `int` | Time limit in seconds |
| `memory_limit` | `int` | Memory limit in mb |
| `src_code` | `string` | Code to run on the server |
| `std_in` | `string` | Standard input to the program |
| `callback_url` | `string` | Url where POST request will be made by worker |



## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

- Fork the repository.
- Create a new branch (git checkout -b feature-branch).
- Make your changes.
- Commit your changes (git commit -m 'Add some feature').
- Push to the branch (git push origin feature-branch).
- Open a pull request.

