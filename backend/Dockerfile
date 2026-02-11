FROM python:3.12-slim

WORKDIR /code

# Install pip-tools
RUN pip install --upgrade pip

# Copy requirements.txt and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./tests ./tests
COPY alembic.ini entrypoint.sh ./

# Set execute permissions
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
