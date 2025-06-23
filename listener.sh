export DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/tasks
export BROKER_URL=amqp://kalo:kalo@127.0.0.1:5672/
export PYTHONPATH=$(pwd)/

# select * from task where task_id='4d7426c3-b49c-4f59-8142-73dc3f7db2c0';
# {
#     "task_id": "4d7426c3-b49c-4f59-8142-73dc3f7db2c0",
#     "data": {
#         "message_type": "success",
#         "response": { "hello": "world"}
#     }
# }

nodemon --exec python3 listener/main.py 