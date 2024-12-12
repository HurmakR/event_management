# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
