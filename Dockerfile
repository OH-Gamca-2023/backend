FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY backend ./backend

WORKDIR /app/backend
CMD ["gunicorn", "backend.wsgi", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--log-file", "-", "--workers", "4"]
