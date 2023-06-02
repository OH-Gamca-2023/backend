FROM python:3.11.3-slim-bullseye
WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV PATH=/home/appuser/.local/bin:$PATH

RUN apt update \
    && apt -y upgrade \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p ./backend \
    && chown -R appuser:appuser ./backend \
    && chmod -R 755 ./backend

USER appuser

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --dev --deploy

COPY backend ./backend

WORKDIR /app/backend

RUN python manage.py collectstatic --noinput

VOLUME /app/backend/staticfiles
VOLUME /app/backend/uploads

CMD python manage.py migrate && gunicorn backend.wsgi --bind 0.0.0.0:8000 --access-logfile - --error-logfile - --workers 4