# fatercal
FATERCAL (New Caledonia's Terrestrial fauna)



## Installation in the production environment

*Requirement* : an installed Git client, Docker Community Edition
([cf. installation](https://docs.docker.com/engine/installation/)) and
docker-compose ([cf. installation](https://docs.docker.com/compose/install/)).


**Installing the application source code**

    mkdir /data/
    git clone https://github.com/acheype/fatercal.git fatercal.git


**Configure the application**

In the production environment, the compose configuration file is in the `docker/prod` directory.

The compose configuration file refer to only two containers: fatercal-db and fatercal-web. They are created from the
version-tagged image downloaded from the Docker Hub (note that the code inside these images could be different that
the one pulled in the `/data/fatercal.git` directory).

Go inside this directory:

    cd docker/prod/

then next to the `docker-compose-prod.yml`, create two config files, each for each container, to define your passwords.
The first one `fatercal-db.env` must have this content :

    POSTGRES_PASSWORD=thePasswordOfTheFatercalUserInTheDb

And the `fatercal-web.env` must have this one (think about escape the '$' character by double it):

    DJANGO_SECRET_KEY=yourLoooooongSecretKey
    POSTGRES_PASSWORD=thePasswordOfTheFatercalUserUsedConnectingTheWebAppToTheDB


**Adding an administrateur**

To let an access to the web interface, you must add one or several superusers. The followed command line ask the
needed information to add a superuser.

    docker exec -it fatercal-web python3 /app/manage.py createsuperuser


**Starting the server**

When the configuration is set, you can launch the application with the docker-compose command :

    docker-compose up

The connection form is then accessible in the port 80 of your host.

You can verify the status of the containers with `docker ps` and stop properly the application with `docker-compose down`.

The database data will be stored in the directory `/data/postgres`. If this location refer to an existing postgres data
directory, the application expects that a fatercal database already exists. However, the containers will create
this directory and init an empty fatercal database.

If needed, it's possible to modify the postgres data directory location by changing in the docker-compose.yml the part
before ':' in that section :

    volumes:
        - /data/postgresql:/var/lib/postgresql/data


**Autostart using Systemd**

For linux system which rely on systemd, the followed configuration will automatically execute a Fatercal service at
system startup.

First create the service file and add the followed content with `vi /etc/systemd/system/fatercal.service` :

    [Unit]
    Description=fatercal
    Requires=docker.service
    After=docker.service

    [Service]
    User=root
    ExecStartPre=-/usr/local/bin/docker-compose -f /data/fatercal.git/docker/prod/docker-compose-prod.yml down
    ExecStart=/usr/local/bin/docker-compose -f /data/fatercal.git/docker/prod/docker-compose-prod.yml up
    ExecStop=/usr/local/bin/docker-compose -f /data/fatercal.git/docker/prod/docker-compose-prod.yml stop

    [Install]
    WantedBy=multi-user.target

(adapt the path for the `docker-compose.yml` according to your situation)

Then enable the start at startup :

    systemctl enable fatercal

## From development to production

To have the database set quicky, it's possible to use the same docker image than in production. For this, you can go to the directory `docker/test` and launch separately the service :

    docker-compose up postgres
    
### TODO Write out this section

launch the db in development

    docker-compose up postgres

build the web application docker image

    cd docker/test
    docker-compose build

for the initialization, make sur the directory /data/fatercal/postgresql is empty

    rm /data/fatercal/postgresql -rf

launch the postgres service (as it's the first startup, it will create the database and the database user)

    docker-compose up postgres

launch the webapp service. As it's the fist startup, it will create all the tables (the django schema where there is
the table managed by django and the public schema with the one managed by the fatercal webapp)

    docker-compose up webapp

test the application in development

    python3 manage.py runserver

create a superuser to test the web application

    docker exec -it fatercal-web python3 /app/manage.py createsuperuser

Then connect to localhost:8000 in a web navigator

If you need to import some data, for a dump in a clear sql file, launch :

    docker exec -i fatercal-db psql -h localhost -d fatercal -U fatercal < dump_to_import.sql

After trying in development environement, you can update the docker image in production.

First, tag the docker image to the version number you want (here, 1.0)

    docker tag acheype/fatercal-web:latest acheype/fatercal-web:1.0

Then, upload the image in the dockerhub repository :

    docker push acheype/fatercal-web:latest
    docker push acheype/fatercal-web:1.0

Finally, change the version number of the web application for the production docker image in the
``docker/prod/docker-compose.yml`` file (after 'fatercal-web:' at the fifth line as below)

    version: '3'
    services:
        www:
            container_name: fatercal-web
            image: acheype/fatercal-web:1.0
            ports:
                - "80:80"
    ...

Then when you will start again the webapp service in the production environment, the new image will be downloaded
before to start :

    cd docker/prod
    docker-compose up
