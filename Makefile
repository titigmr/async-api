run:
	docker-compose up -d

tests:
	python -m unittest 

migrate:
	docker-compose run --rm web alembic upgrade head