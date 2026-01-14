up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f api

test:
	# Add your pytest command here
	docker compose exec api pytest
	