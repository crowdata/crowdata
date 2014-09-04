# ## Crowdata on Docker
#
# Postgres support cribbed from
# https://github.com/crccheck/docker-postgis

FROM ubuntu:14.04
MAINTAINER Harlo <harlo.holmes@gmail.com>

# Install postgres (a la Chris's instructions)
RUN apt-get update -qq

# Change locale to UTF-8 from standard locale ("C")
RUN DEBIAN_FRONTEND=noninteractive apt-get -yq install language-pack-en
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN DEBIAN_FRONTEND=noninteractive locale-gen en_US.UTF-8
RUN DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
RUN update-locale LANG=en_US.UTF-8

RUN DEBIAN_FRONTEND=noninteractive apt-get install -yq wget

# Add Postgres PPA
# --no-check-certificate workaround for:
#     "ERROR: cannot verify www.postgresql.org's certificate"
RUN wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list

RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -yq postgresql-9.3 postgresql-server-dev-9.3 postgresql-contrib

RUN mkdir -p /data
# Update host-based authentification to let remote machines connect
# TODO change to 'md5'?
RUN echo "host    all    all    0.0.0.0/0     trust" >> /etc/postgresql/9.3/main/pg_hba.conf
# Make sure postgresql is listening, send logs to /data/logs
RUN echo "listen_addresses = '*'\nlogging_collector = on\nlog_directory = '/data/logs'" >> /etc/postgresql/9.3/main/postgresql.conf
# Make logs easier for developers to work with
RUN echo "log_filename = 'postgresql.log'\nlog_file_mode=0644\nlog_truncate_on_rotation = on\nlog_rotation_age = 7d" >> /etc/postgresql/9.3/main/postgresql.conf

# Change data directory
RUN sed -i "s@^data_directory.+@data_directory = '/data/postgresql'@" /etc/postgresql/9.3/main/postgresql.conf

# Let other volumes read config
VOLUME ["/data"]

# Crowdata-specific install starts here...
# Install requirements
RUN apt-get install -yq python-dev python-pip libgeos-dev

# Install python deps
RUN pip install -r requirements.txt

# Add the crowdata application to the image
ADD . /crowdata
WORKDIR /crowdata

# Import all the variables
ENV crowdata_HOST $crowdata_HOST
ENV crowdata_USER $crowdata_USER
ENV crowdata_PASSWORD $crowdata_PASSWORD
ENV crowdata_NAME $crowdata_NAME
ENV crowdata_EMAIL $crowdata_EMAIL
ENV crowdata_WITH_DB $crowdata_WITH_DB

# Clone and populate local_settings.py
RUN python docker_setup.py -init

# Setup database 
# TODO: since there is no prior postgres user, we have to:
# init the primary user and grant permissions (Gaba, how to do this again?)
# then...
RUN createuser -s -h $crowdata_HOST $crowdata_USER
RUN createdb -O $crowdata_USER -h $crowdata_HOST $crowdata_NAME
RUN psql -U $crowdata_USER $crowdata_NAME -c "CREATE EXTENSION pg_trgm;"

RUN python manage.py syncdb
RUN python manage.py migrate --all

# Populate database from imported file (if available) and create django superuser
RUN python docker_setup.py -db_pop

# OK LET'S ROLL
EXPOSE [5432, 8000]