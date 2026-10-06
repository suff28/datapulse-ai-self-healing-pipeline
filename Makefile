.PHONY: demo test up down logs

demo:
	python3 demo_local.py

test:
	pytest -q

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f
