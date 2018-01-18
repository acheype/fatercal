# fatercal
FATERCAL (New Caledonia's Terrestrial fauna)



## Installation in the production environment

*Requirement* : an installed Git client, Docker Community Edition
([cf. installation](https://docs.docker.com/engine/installation/)) and
docker-compose ([cf. installation](https://docs.docker.com/compose/install/)).


**Installing the application source code**

    mkdir /data/
    git clone https://github.com/acheype/fatercal.git fatercal.git


**Adding a directory to store the database**

    mkdir /data/postgresql


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

    docker exec fatercal-web python3 /app/manage.py createsuperuser


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



