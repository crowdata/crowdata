CrowData
========

This is the software we used to create [VozData](http://vozdata.lanacion.com).

## Install Locally ##


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

## When creating a document set ##

If you are going to use document cloud to load and view the PDF documents, then you will have to set the 'head html' in the admin, when creating the document set:

``` <script src="http://s3.documentcloud.org/viewer/loader.js"></script> ```

and the template function:

```
// Javascript function to insert the document into the DOM.
// Receives the URL of the document as its only parameter.
// Must be called insertDocument
// JQuery is available yeah
// resulting element should be inserted into div#document-viewer-container

function insertDocument(document_url) {
  var url = document_url.match(/(.+)\.html$/)[1];
  DV.load(url + '.js', {
    container : 'div#document-viewer-container', width:650,height:835,sidebar:false});
}
```

## When importing documents to a 'document set' via CSV upload ##

There is an option 'Add Documents to this document set' in the admin for the document set. You can upload a CSV with columns document_title and document_url. This will create documents in the document set with that name and link to that url. 

[CrowData](http://github.com/jazzido/crowdata)'s copyright is © 2013 Manuel Aristarán <jazzido@jazzido.com>. [CrowData](http://github.com/jazzido/crowdata) was developed with [Open News](http://www.opennews.org) and [La Nacion Argentina](http://www.lanacion.com.ar).
