# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /backend_app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . .

# Set environment variables to ensure Python behaves correctly
ENV PYTHONUNBUFFERED=1

# Expose the port Django runs on
EXPOSE 8001

# Run database migrations and start the Django server
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--log-level=debug", "--access-logfile=-", "--error-logfile=-", "backend_project.wsgi:application"]

#Create logs directory and set permissions (to allow logging)
RUN mkdir -p /backend_app/logs && chmod -R 777 /backend_app/logs

#Delay for PostgreSQl
RUN echo "#!/bin/sh\n\
set -e\n\
echo \"Applying database migrations...\"\n\
python manage.py migrate --noinput\n\
echo \"Starting Gunicorn...\"\n\
exec \"\$@\"" > /entrypoint.sh

#COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]