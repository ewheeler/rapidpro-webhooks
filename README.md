# Dev Environment

### Create your virtual environment
    pipenv install
    psql -c 'CREATE DATABASE rapidpro-webhooks;' -U postgres
    python manage.py runserver

Next, get your databases setup. This project uses CouchDB and Postgres.

### CouchDB

Simply install CouchDB for your development environment. The necessary catalog will be created as needed automatically.

### PostgreSQL

We need some Postgres love too. To initialize, issue the following command:

`% python manage.py db upgrade`

### Start the server

To start the server, you need to first set a couple environment variables.

`export RPWEBHOOKS_SETTINGS=settings/dev.py`
`export FLASK_APP=app.py`
`flask run`


