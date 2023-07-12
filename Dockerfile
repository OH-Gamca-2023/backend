FROM python:3.11.3-slim-bullseye
WORKDIR /app
RUN useradd --create-home appuser \
    && chmod 777 /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

VOLUME /app/staticfiles
VOLUME /app/media

RUN pip install --upgrade pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY --chown=appuser:appuser . /app/

USER root
RUN chown appuser:appuser -R /app/
USER appuser

CMD ["/app/entrypoint.sh"]
