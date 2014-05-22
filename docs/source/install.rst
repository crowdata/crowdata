.. _install

How To Install It Locally
=========================


1. Python 2.7.5

2. We recommend the use of [virtualenv](http://virtualenv.org) — Install it.

3. Create a virtual environment and activate it:

    ```bash
    virtualenv ~/.python-envs/crowdata
    . ~/.python-envs/crowdata/bin/activate
    ```

4. Get the source code:

    ```bash
    git clone https://github.com/jazzido/crowdata-wit.git crowdata
    cd crowdata
    ```

5. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

   (If you are using Ubuntu, you may need to install `python-dev` before dependencies.)

6. Create PostgreSQL database

    ```bash
    $ createuser -s -h localhost crow_user
    $ createdb -O crow_user -h localhost crowdata_development
    ```


7. Create extensions for doing [trigram matching](http://www.postgresql.org/docs/9.2/static/pgtrgm.html) and [removing accents](http://www.postgresql.org/docs/9.1/static/unaccent.html) in PostgreSQL

    ```bash
    $ psql -ucrow_user
    crow_user=# \c crowdata_development
    crowdata_development=# CREATE EXTENSION pg_trgm;
    crowdata_development=# CREATE EXTENSION unaccent;
    ```

7. We keep local settings outside GIT. You will need to copy `local_settings.py.example` to `local_settings.py`. You will need to edit the database settings there.

    ```python
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
    ```

5. Initialize the database:

    ```bash
    python manage.py syncdb
    python manage.py migrate --all
    ```

6. Start the development server

    ```bash
    python manage.py runserver_plus
    ```
