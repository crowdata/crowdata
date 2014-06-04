.. _install

Installation
============

1. Python 2.7.5

2. We recommend the use of `virtualenv <http://virtualenv.org>` — Install it.

3. Create a virtual environment and activate it::

      $ virtualenv ~/.python-envs/crowdata
      $ . ~/.python-envs/crowdata/bin/activate

4. Get the source code::

    $ git clone https://github.com/crowdata/crowdata.git crowdata
    $ cd crowdata

5. Install dependencies::

    $ pip install -r requirements.txt

(If you are using Ubuntu, you may need to install `python-dev` before dependencies.)

6. Create PostgreSQL database::

    $ createuser -s -h localhost crow_user
    $ createdb -O crow_user -h localhost crowdata_development

7. Create extensions for doing `trigram matching <http://www.postgresql.org/docs/9.2/static/pgtrgm.html>` and `removing accents <http://www.postgresql.org/docs/9.1/static/unaccent.html>` in PostgreSQL::

    $ psql -ucrow_user
    crow_user=# \c crowdata_development
    crowdata_development=# CREATE EXTENSION pg_trgm;
    crowdata_development=# CREATE EXTENSION unaccent;

   *Note: In Debian/Ubuntu you need to install postgresql-contrib-9.1 and geospatial libraries.*

8. We keep local settings out of GIT. You will need to copy `local_settings.py.example` to `local_settings.py`. You will need to edit the database settings there.::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'crowdata_development',                      # Or path to database file if using sqlite3.
            'USER': 'crow_user',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }

9. Initialize the database::

    $ python manage.py syncdb
    $ python manage.py migrate --all

10. Start the development server::

    $ python manage.py runserver_plus
