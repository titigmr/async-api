run:
	docker-compose up -d

migrate:
	docker-compose run --rm web alembic upgrade head