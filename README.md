# PrismVio

PrismVio

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    $ mypy prismvio

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
celery -A config.celery_app worker -B -l info
```

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

```shell
docker compose -f local.yml build
docker compose -f local.yml up
```

### Make file

Oneshot
```shell
make build
make oneshot
```

Logs:
```shell
make logs.django
make logs.celeryworker
```

### Pre-commit
brew install pre-commit
pre-commit run --all-files

### How to start new app
Step 1
```shell
cd prismvio
python ../manage.py startapp event
```

Step 2:
Go to new app, edit AppConfig name:
```
name = "prismvio.event"
```

Step 3:
Go to config/settings/base.py
Add new app into LOCAL_APPS setting
```
LOCAL_APPS = [
    ...
    "prismvio.event",
]
```

Add urls for API:
```
prismvio/api/urls.py
```


## Search - Elasticsearch
### ENV
Check ELASTICSEARCH_DSL in the django settings.


### Management Commands
Delete all indices in Elasticsearch or only the indices associate with a model (--models):
```
python manage.py search_index --delete [-f] [--models [app[.model] app[.model] ...]]
```

Create the indices and their mapping in Elasticsearch:
```
python manage.py search_index --create [--models [app[.model] app[.model] ...]]
```

Populate the Elasticsearch mappings with the Django models data (index need to be existing):
```
python manage.py search_index --populate [--models [app[.model] app[.model] ...]] [--parallel] [--refresh]
```

Recreate and repopulate the indices:
```
python manage.py search_index --rebuild [-f] [--models [app[.model] app[.model] ...]] [--parallel] [--refresh]
```

Recreate and repopulate the indices using aliases:
```
python manage.py search_index --rebuild --use-alias [--models [app[.model] app[.model] ...]] [--parallel] [--refresh]
```

Recreate and repopulate the indices using aliases, but not deleting the indices that previously pointed to the aliases:
```
python manage.py search_index --rebuild --use-alias --use-alias-keep-index [--models [app[.model] app[.model] ...]] [--parallel] [--refresh]
```

### Run seed data
```
export ELASTICSEARCH_DSL_AUTOSYNC=False
python manage.py seed_dummy_data
python manage.py search_index --rebuild --parallel
```

### Register Elasticsearch DSL document
Go to `search/documents/__init__.py`
Update your documents:
```
__all__ = [
    "MerchantDocument"
]
```
python3.11 -m venv env
source env/bin/activate
python3.11 -m pip install pip --upgrade

brew install postgresql
export PGDATA='/usr/local/var/postgres' #check your package dir
brew services list
brew services stop postgresql@14