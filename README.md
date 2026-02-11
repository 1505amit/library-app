# Library Management App

A Neighborhood library management system built with **FastAPI** (Backend) and **React/Vite** (Frontend), containerized with Docker for easy development and deployment.

## Features

- 📚 Book catalog management
- 👥 Member management
- 📋 Borrow/return tracking
- 🔌 RESTful API with automatic openapi documentation
- 🎨 Modern React UI using MUI
- 🐳 Docker containerized setup

## Prerequisites

Ensure you have installed:

- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Make** - Usually pre-installed on Linux/Mac, [Windows users](https://gnuwin32.sourceforge.net/packages/make.htm)
- **Git** - For cloning the repository

## Quick Start

```bash
make setup    # Build Docker images
make dev      # Start the entire application
```

The app will be running at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Documentation

- **[Setup & Development Guide](./SETUP.md)** - Complete setup instructions, commands reference, troubleshooting
- **[Makefile Commands](#available-commands)** - Quick command reference

## Available Commands

### Core Commands

```bash
make setup           # Build images and prepare project
make dev             # Start all services with live logs
make down            # Stop all services
make clean           # Remove containers and volumes
```

### Database Migrations

```bash
make migrate                          # Apply pending migrations
make migrate-create msg='description' # Create new migration
make migrate-rollback                 # Undo last migration
```

### Testing

```bash
make test-backend    # Run backend tests
make test-coverage   # Run with coverage report
```

For a complete list of commands, run:

```bash
make help
```

## Project Structure

```
.
├── backend/              # FastAPI application
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations
│   └── tests/           # Test suite
├── frontend/             # React/Vite application
│   ├── src/             # React components
├── docker-compose.yaml  # Docker services configuration
└── Makefile            # Project commands
```

## Technology Stack

### Backend

- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Alembic** - Schema migrations
- **pytest** - Testing

### Frontend

- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Navigation
- **Axios** - HTTP client
- **Material-UI** - Component library

## Development Workflow

1. Clone the repository
2. Run `make setup` - one-time setup
3. Run `make dev` - start developing
4. Check `make help` for available commands
5. For detailed workflows, see [SETUP.md](./SETUP.md)
