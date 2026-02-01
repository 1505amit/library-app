FROM python:3.12-slim

WORKDIR /code

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock first for caching
COPY Pipfile* ./

# Install dependencies system-wide
RUN pipenv install --system

# Copy app source
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini ./

CMD ["sh", "-c", "pipenv run alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
