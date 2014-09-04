FROM harlo:postgres
MAINTAINER Harlo <harlo.holmes@gmail.com>

RUN apt-get update -qq

# Install requirements
RUN apt-get install -yq python-dev python-pip libgeos-dev

# Install python deps
RUN pip install -r requirements.txt
RUN docker_setup.py

# Setup database
RUN python manage.py syncdb
RUN python manage.py migrate --all

# Populate database (TODO: from env_vars, because user might not have these...)
ADD free_crow.backup
RUN pg_restore --dbname=$(ENV_VAR) --verbose $(ENV_VAR) --clean

# Create superuser TBD!!!

RUN python manage.py runserver_plus
EXPOSE 8000