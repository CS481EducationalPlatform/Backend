# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /backend_app

# Install system dependencies including PostgreSQL client
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory and set permissions (to allow logging)
RUN mkdir -p /backend_app/logs && chmod -R 777 /backend_app/logs

# Copy the entire Django project into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8001
ENV DEBUG=False

# Generate a default SECRET_KEY if not provided
RUN python -c 'import secrets; print("SECRET_KEY=" + secrets.token_hex(32))' > /backend_app/.env

# Make the entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port Django runs on (Render will override this with $PORT)
EXPOSE 8001

# Use the entrypoint script
ENTRYPOINT ["/entrypoint.sh"]

# Start the application
CMD gunicorn backend_project.wsgi:application --bind 0.0.0.0:${PORT} --workers 4 --log-level debug
