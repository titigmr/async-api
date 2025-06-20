export DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/tasks
export BROKER_URL=amqp://kalo:kalo@127.0.0.1:5672/
export PYTHONPATH=$(pwd)/

nodemon --exec python3 listener/main.py 