.PHONY: help setup up down build rebuild logs clean \
	migrate migrate-create migrate-rollback migrate-current migrate-history \
	dev dev-logs test-backend test-coverage \
	status start stop restart remove

# Color definitions
HELP_FORMAT := "  \033[36m%-30s\033[0m %s\n"

## Main Help
help:
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════╗"
	@echo "║         Library App - Project Management Commands         ║"
	@echo "╚═══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Quick Start:"
	@printf $(HELP_FORMAT) "make setup" "Full project setup (recommended for new developers)"
	@printf $(HELP_FORMAT) "make dev" "Start entire app in development mode"
	@printf $(HELP_FORMAT) "make down" "Stop all services"
	@echo ""
	@echo "🐳 Docker Management:"
	@printf $(HELP_FORMAT) "make up" "Start all services (db, backend, frontend)"
	@printf $(HELP_FORMAT) "make build" "Build all Docker images"
	@printf $(HELP_FORMAT) "make rebuild" "Rebuild all images (no cache)"
	@printf $(HELP_FORMAT) "make logs" "View logs from all services"
	@printf $(HELP_FORMAT) "make dev-logs" "Follow real-time logs"
	@printf $(HELP_FORMAT) "make clean" "Stop services and remove volumes"
	@echo ""
	@echo "💾 Database/Migrations:"
	@printf $(HELP_FORMAT) "make migrate" "Run pending migrations"
	@printf $(HELP_FORMAT) "make migrate-create msg=..." "Create new migration (use quotes: msg='add user table')"
	@printf $(HELP_FORMAT) "make migrate-rollback" "Rollback last migration"
	@printf $(HELP_FORMAT) "make migrate-current" "Show current migration"
	@echo ""
	@echo "📦 Dependencies:"
	@printf $(HELP_FORMAT) "make freeze" "Update requirements.txt from Pipfile"
	@echo ""
	@echo "🧪 Testing:"
	@printf $(HELP_FORMAT) "make test-backend" "Run backend tests only"
	@printf $(HELP_FORMAT) "make test-coverage" "Run backend tests with coverage"
	@echo ""

## Quick Start
setup: build
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════╗"
	@echo "║        ✓ Project setup complete!                          ║"
	@echo "║                                                           ║"
	@echo "║  Run 'make dev' to start the application                 ║"
	@echo "║  Backend: http://localhost:8000                          ║"
	@echo "║  Frontend: http://localhost:3000                         ║"
	@echo "╚═══════════════════════════════════════════════════════════╝"
	@echo ""

## Docker Management
up:
	docker-compose up -d
	@echo "✓ All services started"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend: http://localhost:8000"

down:
	docker-compose down
	@echo "✓ All services stopped"

build:
	docker-compose build
	@echo "✓ All images built"

rebuild:
	docker-compose build --no-cache
	@echo "✓ All images rebuilt (no cache)"

logs:
	docker-compose logs -f

dev-logs:
	docker-compose logs -f backend frontend

## Development Mode
dev: up logs
	@echo "⏳ Waiting for services to be ready..."
	@sleep 5
	@docker-compose logs -f backend frontend

## Database & Migrations
migrate:
	docker-compose exec -T backend alembic upgrade head
	@echo "✓ Database migrations applied"

migrate-create:
	@if [ -z "$(msg)" ]; then \
		echo "❌ Error: Please provide message"; \
		echo "Usage: make migrate-create msg='add users table'"; \
		exit 1; \
	fi
	docker-compose exec -T backend alembic revision --autogenerate -m "$(msg)"
	@echo "✓ Migration created at: backend/alembic/versions/"
	@echo "⚡ Run 'make migrate' to apply the migration"

migrate-rollback:
	docker-compose exec -T backend alembic downgrade -1
	@echo "✓ Rolled back to previous migration"

migrate-current:
	docker-compose exec -T backend alembic current

migrate-history:
	docker-compose exec -T backend alembic history

## Testing & Quality
test-backend:
	docker-compose exec -T backend python -m pytest tests/ -v
	@echo "✓ Backend tests completed"

test-coverage:
	docker-compose exec -T backend python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
	@echo "✓ Coverage report: backend/htmlcov/index.html"

## Cleanup
clean:
	docker-compose down -v
	docker-compose rm -f
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	cd frontend && rm -rf node_modules dist 2>/dev/null || true
	@echo "✓ Cleanup completed"

## Aliases
status: logs
start: up
stop: down
restart: down up
remove: clean
.DEFAULT: help
