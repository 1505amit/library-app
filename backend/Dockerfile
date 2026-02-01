FROM python:3.12-slim

WORKDIR /code

# Install pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock first for caching
COPY Pipfile* ./

# Install dependencies system-wide (including dev dependencies for testing)
RUN pipenv install --system --deploy --dev

# Copy app source
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./tests ./tests
COPY alembic.ini entrypoint.sh ./

# Set execute permissions
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
