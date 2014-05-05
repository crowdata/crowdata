vozdata
=======

**Importante**: esta es la versión de [CrowData](http://github.com/jazzido/crowdata) que se usará para implementar el producto VozData de La Nación

## Crear entorno de desarrollo ##

1. Se recomienda el uso de [virtualenv](http://virtualenv.org) — Instalarlo.

2. Crear un entorno virtual y activarlo:

    ```bash
    virtualenv ~/.python-envs/crowdata
    . ~/.python-envs/crowdata/bin/activate
    ```

3. Obtener el código fuente:

    ```bash
    git clone https://github.com/lanacioncom/vozdata.git crowdata
    cd crowdata
    ```

4. Instalar las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

   (Si está en Ubuntu, es probable que también deba instalar `python-dev` antes de instalar las depdencias.)

4. Crear una base de datos PostgreSQL

4. Renombrar `local_settings.py.example` a `local_settings.py` y editarlo para ajustar los parámetros de conexión a DB según corresponda.

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'crowdata_development',                      # Or path to database file if using sqlite3.
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
    ```

5. Inicializar la DB:

    ```bash
    python manage.py syncdb
    python manage.py migrate --all
    ```

6. Iniciar el servidor de desarrollo

    ```bash
    python manage.py runserver_plus
    ```

## Al crear un document set ##

Si vas a utilizar document cloud para cargar y visualizar los documentos PDFs, tenes que tener en el head html:

``` <script src="http://s3.documentcloud.org/viewer/loader.js"></script> ```

y en el template function:

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

El copyright de [CrowData](http://github.com/jazzido/crowdata) es © 2013 Manuel Aristarán <jazzido@jazzido.com>.

El diseño de VozData y las modificaciones de CrowData desarrolladas para VozData son © 2013 La Nación.

[CrowData](http://github.com/jazzido/crowdata) fue creado gracias al apoyo de [Open News](http://www.opennews.org).
