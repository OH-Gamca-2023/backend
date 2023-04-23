# Start with a Python 3.10 image as a base
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv
RUN pip install pipenv

# Install the dependencies from Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile

# Copy the application code into the container
COPY ./backend /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Collect static files
RUN python manage.py collectstatic --noinput

# Add gunicorn to the PATH
ENV PATH="/usr/local/bin:$PATH"

# Expose port 8000
EXPOSE 8000

# Start the Django development server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi", "--access-logfile", "-", "--error-logfile", "-", \
    "--workers", "4", "--timeout", "120"]
