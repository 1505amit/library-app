.PHONY: docker-test docker-test-coverage

# Docker test commands
docker-test:
	docker-compose exec -T backend python -m pytest tests/ -v

docker-test-coverage:
	docker-compose exec -T backend python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
