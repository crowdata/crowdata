CrowData
========

``CrowData`` is a tool to collaborate on the verification or release of data that otherwise would be hard or impossible to get via automatic tools. This is the software we used to create [VozData](http://vozdata.lanacion.com.ar).

In 2014, La Nacion in Argentina launched [VozData](http://vozdata.lanacion.com.ar), a website to crowdsourced senate spendings by asking people to transcribe information from 6500 scanned PDF documents from the senate. This is the code that created that website and it can be used with any document set and any data you may need to take from them.

[VozData: collaborating to free data from PDFs](http://blogs.lanacion.com.ar/projects/data/vozdata/): A really nice article about the process of creating ``VozData`` from La Nacion.

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
    git clone https://github.com/crowdata/crowdata.git crowdata
    cd crowdata
    ```

5. Install dependencies:

    Ubuntu users: before you can move forward, please make sure you have the following packages installed: `python-dev`, `postgresql-9.3`, `postgresql-server-dev-9.3`, `postgresql-contrib`, and `libgeos-dev`

    ```bash
    pip install -r requirements.txt
    ```

6. Create PostgreSQL database

    ```bash
    $ createuser -s -h localhost crow_user
    $ createdb -O crow_user -h localhost crowdata_development
    ```

7. Create extensions for doing [trigram matching](http://www.postgresql.org/docs/9.2/static/pgtrgm.html) and [removing accents](http://www.postgresql.org/docs/9.1/static/unaccent.html) in PostgreSQL

    ```
    $ psql -Ucrow_user crowdata_development
    crowdata_development=# CREATE EXTENSION pg_trgm;
    ```

8. We keep local settings outside GIT. You will need to copy `local_settings.py.example` to `local_settings.py`. You will need to edit the database settings there.

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

9. Install the GEOS library in case you don't have installed already.

10. Initialize the database:

    ```bash
    python manage.py syncdb
    python manage.py migrate --all
    ```

11. Ask a team member for a database backup and load it.

    ```
    pg_restore --dbname=crowdata_development --verbose ~/my_backup.backup --clean
    ```

12. Create superuser

    ```bash
    python manage.py createsuperuser
    ```
    and follow the prompts.

13. Start the development server

    ```bash
    python manage.py runserver_plus
    ```

14. Navigate to `http://localhost:8000/admin/` and log in with your superuser credentials.

## Installing via Docker ##

1. Set your environment variables

There are 6 required environment variables.

* crowdata_NAME : your database name
* crowdata_USER : the main database user (this will also be the django superuser)
* crowdata_HOST : usually localhost
* crowdata_EMAIL : email for django superuser
* crowdata_WITH_DB : the filename of a prepopulated backup for the database (or simply None)
* crowdata_PASSWORD : the password you want

set each of them with:

`export [var name]=[value you want]` (i.e. `export crowdata_USER="beyonce"`)

2. Build your image with

`cat Dockerfile | envsubst | sudo docker build -t lanacion/crowdata -`

3. Once it's built, run the server with

`sudo docker run -i -t -d lanacion/crowdata python /crowdata/manage.py runserver_plus && tail -f /dev/null`

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

[CrowData](http://github.com/crowdata/crowdata)'s copyright is © 2013 Manuel Aristarán <jazzido@jazzido.com>. [CrowData](http://github.com/crowdata/crowdata) was developed with [Open News](http://www.opennews.org) and [La Nacion Argentina](http://www.lanacion.com.ar).

``Crowdata`` is an open source project that was born when [Manuel Aristaran](http://github.com/jazzido) was an Open News fellow at La Nacion in 2013. It was finally released as free software when [Gabriela Rodriguez](http://github.com/gabelula)  continued it for VozData in 2014. Thanks to Cristian Bertelegni and La Nacion for contributing to the code.

Now it relies on contributions from people and organizations. Please, use it, comment on it and make improvements by pull requests in 'GitHub <http://github.com/crowdata/crowdata>'.


Contributions
=============

* Fork the repo
* Clone your fork
* Make a branch of your changes
* Make a pull request through GitHub, and clearly describe your changes
