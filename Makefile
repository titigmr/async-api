run:
	docker compose up -d

# Reminder for one file: pytest -v  tests/api/repositories/test_task_repository.py
test:
	pytest

coverage:
	coverage run
	coverage html

migrate:
	docker compose run --rm web alembic upgrade head