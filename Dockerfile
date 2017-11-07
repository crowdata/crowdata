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
RUN DEBIAN_FRONTEND=noninteractive locale-gen en_US.UTF-8 && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales && \
    update-locale LANG=en_US.UTF-8 && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq wget && \
    wget --no-check-certificate --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" >> /etc/apt/sources.list && \
    apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install -yq postgresql-9.3 postgresql-server-dev-9.3 postgresql-contrib && \
    mkdir -p /data && \
    echo "host    all    all    0.0.0.0/0     trust" >> /etc/postgresql/9.3/main/pg_hba.conf && \
    echo "listen_addresses = '*'\nlogging_collector = on\nlog_directory = '/data/logs'" >> /etc/postgresql/9.3/main/postgresql.conf && \
    echo "log_filename = 'postgresql.log'\nlog_file_mode=0644\nlog_truncate_on_rotation = on\nlog_rotation_age = 7d" >> /etc/postgresql/9.3/main/postgresql.conf && \
    sed -i "s@^data_directory.+@data_directory = '/data/postgresql'@" /etc/postgresql/9.3/main/postgresql.conf

# Let other volumes read config
VOLUME ["/data"]

# Crowdata-specific install starts here...
# Install requirements
RUN apt-get install -yq python-dev python-pip libgeos-dev

# Add the crowdata application to the image
ADD . /crowdata
WORKDIR /crowdata

# Install python deps
RUN pip install -r requirements.txt

# Import all the variables
ENV crowdata_HOST $crowdata_HOST
ENV crowdata_USER $crowdata_USER
ENV crowdata_PASSWORD $crowdata_PASSWORD
ENV crowdata_NAME $crowdata_NAME
ENV crowdata_EMAIL $crowdata_EMAIL
ENV crowdata_WITH_DB $crowdata_WITH_DB

# Clone and populate local_settings.py
RUN python docker_setup.py -init && \
    createuser -s -h $crowdata_HOST $crowdata_USER && \
    createdb -O $crowdata_USER -h $crowdata_HOST $crowdata_NAME && \
    psql -U $crowdata_USER $crowdata_NAME -c "CREATE EXTENSION pg_trgm;" && \
    python manage.py syncdb && \
    python manage.py migrate --all && \
    python docker_setup.py -db_pop 

# OK LET'S ROLL
EXPOSE [5432, 8000]
