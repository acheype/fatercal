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

The compose configuration file for the production environment is in the root directory.

The compose configuration file refer to only two containers: fatercal-db and fatercal-web. They are created from the
version-tagged image downloaded from the Docker Hub (note that the code inside these images could be different that
the one pulled in the `/data/fatercal.git` directory).

Go inside this root directory, then next to the `docker-compose.yml`, create two config files, each for each container, to define your passwords.
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
this directory and init an empty fatercal database (two schemas will be create in the database : the django schema 
for the table managed by django and the public schema for the ones managed by fatercal).

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

**In development**

Developments are made in the *dev* branch.
The version deployed in production are rebased in the *master* branch, and a tag named with the version number is made 
in the Git repository.

For rebase the dev branch into the master branch, do :

    git checkout master
    git rebase dev
    
Then to tag the current version to a tag, you can type (the tag is named 2.3.3 in this example) :

    git tag 2.3.3
    git push --tags

To test and develop the web application, you can launch the development server by taping :
    
    python3 manage.py runserver

Then connect to http://localhost in a web navigator.

**Update the docker image of the web application**

In this example, we want to build the web application image directly on the server in the already existing local 
repository located in `/data/fatercal.git`. It may have to init the repository before.
First get the tagged version of the git repository we want to deploy (we choose 2.3.3 for this example) :

    cd /data/fatercal.git/
    git pull
    git checkout tags/2.3.3
    
Next, make sure you have the tag is updated at the end of the `image` property in the `docker-compose.yml` :

    version: '3'
    services:
        webapp:
            container_name: fatercal-web
            image: acheype/fatercal-web:2.3.3
            build: ./fatercal_apps
            volumes:
            ...
            
Then, you can build the web application docker image by typing :

    docker-compose build

Finally you can tag that the last image available is the version you have just built :

    docker tag acheype/fatercal-web:2.3.3 acheype/fatercal-web:latest acheype/fatercal-web:latest

To save the docker image in https://hub.docker.com/ repository, make sure to have an account in the website. With the
user `acheype` by example, you can save your image by typing :

    docker push acheype/fatercal-web:2.3.3
    docker push acheype/fatercal-web:latest
    
Then if you want to stop reload the new version in prod, you can simply launch :

    docker-compose down
    docker-compose up
    
**Caution with database updates**

The django framework and the migration system allow to update the database model with the django migrations. These
migrations are lauched automatically by the fatercal webapp image at startup (the command 
`python3 /app/manage.py migrate fatercal` is launched in the `docker-entrypoint.sh` of fatercal-web docker image).

Nevertheless, the 'historique' tables, associated triggers and the taxref_export materialized view are not included in
the django migration. If the model update concern these data, you will have to update the database structure manually. 
These changes generally concern the table, function or data types whose scripts are located in the 
`fatercal_apps/sql_script` directory.

    
## Other usefull commands in production

**Create a superuser to access to the admin application**

After the first deployment in production, you need to create a superuser to have access to the admin application : 

    docker exec -it fatercal-web python3 /app/manage.py createsuperuser
    
**Init the database from scratch**

Before to do it, make sure you are not in production with existing data !!

    rm /data/fatercal/postgresql -rf
    
**Import a database from a dump file**

If you need to import some data, for a dump in a clear sql file, launch :

    docker exec -i fatercal-db psql -h localhost -d fatercal -U fatercal < dump_to_import.sql
    
**Launch the postgres client console**

To consult the database tables or update some triggers which are not automatically by the django framework, you can
launch :

    docker exec -it fatercal-db psql -h localhost -d fatercal -U fatercal

**Import a TAXREF revision**

To import with the import script (operation to be done for each taxref revision, generally once a year), first copy the
taxref file in the docker image then execute (the file need to be named `taxref_animalia.csv` and put in 
`/app/script_import`) :

    docker cp file_to_import.csv fatercal-web:/app/script_import
    docker exec -it fatercal-web python3 /app/script_import/updatedata.py

Note that the first time, you need to set the user and password by editing the `script_import/updatedata.py` file.

