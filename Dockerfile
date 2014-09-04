FROM harlo:postgres
MAINTAINER Harlo <harlo.holmes@gmail.com>

RUN apt-get update -qq

# Install requirements
RUN apt-get install -yq python-dev python-pip libgeos-dev

# Install python deps
RUN pip install -r requirements.txt

# Clone and populate local_settings.py
RUN python docker_setup.py -init

# Setup database
RUN createuser -s -h $crowdata_HOST $crowdata_USER
RUN createdb -O $crowdata_USER -h $crowdata_HOST $crowdata_NAME
RUN psql -U $crowdata_USER $crowdata_NAME -c "CREATE EXTENSION pg_trgm;"

RUN python manage.py syncdb
RUN python manage.py migrate --all

# Populate database from imported file (if available) and create superuser
RUN python docker_setup.py -db_pop

# OK LET'S ROLL
RUN python manage.py runserver_plus
EXPOSE 8000