# Backend

[WIP] Dockerized Python Django backend for Babushka Lessons.

Current status: Imported Django backend demo project, now to incorporate into Docker backend demo project. 

# Setup Commands
```
#Take down containers and empty volumes
docker-compose down --volumes
#Prop up containers
docker-compose up --build

#Python packages (can be done in /venv/Scripts/activate environment)
pip install django python-dotenv psycopg psycopg2 celery django-cors-headers djangorestframework
pip install --upgrade google-api-python-client

#Migrate tables and create an administrator
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

# Ports Used
8000 : web : Django Backend
5173 : Currently Allowed FrontEnd CORS
6379 : Redis?
5432 : db : Postgres DB


# Need to Add
After pulling the repo user needs to set up backend\.env file which needs
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432
DEBUG=True

## License

This project is completely closed source. All rights reserved.