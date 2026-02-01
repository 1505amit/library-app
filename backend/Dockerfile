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
COPY alembic.ini entrypoint.sh ./

# Set execute permissions
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
