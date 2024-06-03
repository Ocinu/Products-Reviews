# Names of the containers and network
DOCKER_COMPOSE=docker-compose
SERVICE_WEB=web
SERVICE_DB=db

# Load environment variables
include .env
export $(shell sed 's/=.*//' .env)

# Docker commands
build:
	@$(DOCKER_COMPOSE) build --no-cache

up:
	@$(DOCKER_COMPOSE) up -d

stop:
	@$(DOCKER_COMPOSE) stop

down:
	@$(DOCKER_COMPOSE) down --volumes --remove-orphans

restart: stop up

# Command to wait for the database to be ready
wait_for_db:
	@echo "Waiting for the database to be ready..."
	@$(DOCKER_COMPOSE) exec $(SERVICE_DB) sh -c 'echo POSTGRES_USER=$(POSTGRES_USER); echo POSTGRES_DB=$(POSTGRES_DB); while ! pg_isready -U $(POSTGRES_USER); do sleep 1; done'

# Commands to work with the database
create_db: wait_for_db
	@echo "Creating database: $(POSTGRES_DB) with user: $(POSTGRES_USER)"
	@$(DOCKER_COMPOSE) exec $(SERVICE_DB) sh -c 'psql -U $(POSTGRES_USER) -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '\''$(POSTGRES_DB)'\''" | grep -q 1 || psql -U $(POSTGRES_USER) -d postgres -c "CREATE DATABASE $(POSTGRES_DB);"'

seed_db:
	@echo "Seeding database..."
	@$(DOCKER_COMPOSE) up -d $(SERVICE_WEB)
	@timeout /t 10 /nobreak
	@$(DOCKER_COMPOSE) exec $(SERVICE_WEB) python core/init_db.py

# Run Flask application
start:
	@$(DOCKER_COMPOSE) up

# Full setup cycle
setup: down build up create_db seed_db start

# Test project
test:
	@$(DOCKER_COMPOSE) exec $(SERVICE_WEB) pytest tests/
