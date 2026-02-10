# Complete Setup & Development Guide

This guide provides detailed instructions, complete command reference, and workflows for developing the Library App. For a quick start, see [README.md](./README.md).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Available Commands](#available-commands)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)
- [Tips for Developers](#tips-for-developers)

## Prerequisites

Before you begin, ensure you have installed:

- Docker & Docker Compose
- Make (usually pre-installed on Linux/Mac, [install for Windows](https://gnuwin32.sourceforge.net/packages/make.htm))
- Git

## Initial Setup

### First-Time Setup (Recommended)

```bash
make setup    # Build Docker images
make dev      # Start all services
```

The app will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Understanding the Setup Process

If you prefer to understand each step:

```bash
# 1. Build Docker images
make build

# 2. Start all services (db, backend, frontend)
make up

# 3. View logs to confirm everything is running
make logs

# 4. Run database migrations (migrations run automatically on app startup)
make migrate
```

## Available Commands

### Working with the Application

```bash
# Start the entire application
make dev

# View real-time logs from all services
make logs

# Stop all services
make down

# Restart all services
make restart
```

### Database Migrations

```bash
# Apply all pending migrations
make migrate

# Create a new migration
make migrate-create msg='add users table'

# Check current migration status
make migrate-current

# View all migrations history
make migrate-history

# Rollback to previous migration
make migrate-rollback
```

### Testing

```bash
# Run backend tests
make test-backend

# Run backend tests with coverage report
make test-coverage
```

### Docker Management

```bash
# View all available commands
make help

# Build Docker images
make build

# Rebuild images (no cache)
make rebuild

# Stop all services
make down

# Stop and remove volumes (clean slate)
make clean

# View application logs
make logs

# Follow real-time logs
make dev-logs
```

## Common Workflows

### Starting Development

```bash
# First time only
make setup

# Every time you start working
make dev
```

### Creating a Database Schema Change

```bash
# 1. Make your changes to the SQLAlchemy models in app/models/

# 2. Create a migration
make migrate-create msg='specific description here'

# 3. Review the generated migration file in backend/alembic/versions/

# 4. Apply the migration
make migrate

# 5. Restart the app to see changes
make restart
```

### Running Tests Before Committing

```bash
# Run backend tests
make test-backend

# Or test with coverage
make test-coverage
```

### Database connection errors

```bash
# Completely reset the database
make clean
make setup
make dev

# This removes volumes, rebuilds everything, and starts fresh
```

## File Structure

```
Makefile                  # Root Makefile (run all commands from here)
docker-compose.yaml       # Docker services configuration
backend/                  # Backend server (FastAPI)
frontend/                 # Frontend application (React/Vite)
```

## Getting Help

```bash
# View all available commands
make help
```

All commands run from the root directory. Documentation is built into the Makefile help system.

---
