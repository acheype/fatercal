FROM ubuntu:18.10
LABEL author="laurent.schaeffer313@gmail.com"

# apache-httpd environment variables
ENV APACHE_UID 33
ENV APACHE_GID 33
ENV APACHE_RUN_USER #${APACHE_UID}
ENV APACHE_RUN_GROUP #${APACHE_GID}
ENV APACHE_PORT 80
ENV APACHE_PORTS 443
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Pacific/Noumea

# Environement timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# install the ubuntu packages needed
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:certbot/certbot
#RUN apt-get update && apt-get install -y apache2 mod_ssl apache2-utils libapache2-mod-wsgi-py3 python3 python3-pip libpq-dev postgresql-client-9.6 vim python-certbot-apache && apt-get clean
RUN apt-get update && apt-get install -y apache2 apache2-utils libapache2-mod-wsgi-py3 python3 python3-pip libpq-dev vim python-certbot-apache iputils-ping
RUN apt-get update && apt-get install -y postgresql-client-10
RUN a2enmod ssl
RUN a2enmod headers

# copy the application files
RUN mkdir /app
COPY manage.py requirements.txt /app/
COPY fatercal /app/fatercal
COPY fatercal-site /app/fatercal-site
COPY script_import /app/script_import
COPY index.html /var/www/html/index.html

# install python dependencies
RUN pip3 install -r /app/requirements.txt

# configure the apache server
RUN /bin/bash -c "source /etc/apache2/envvars"
RUN mkdir -p /var/run/apache2; chown $APACHE_UID /var/run/apache2
RUN mkdir -p /var/lock/apache2; chown $APACHE_UID /var/lock/apache2
RUN service apache2 start
RUN service apache2 stop
COPY security.conf /etc/apache2/conf-enabled/security.conf
COPY ssl.conf /etc/apache2/ssl.conf
#COPY 000-fatercal-redirhttps.conf /etc/apache2/sites-available/
COPY 000-default.conf /etc/apache2/sites-available/
COPY 000-fatercal-ssl.conf /etc/apache2/sites-available/
#RUN ln -s /etc/apache2/sites-available/000-default.conf /etc/apache2/sites-enabled/
RUN ln -s /etc/apache2/sites-available/000-fatercal-ssl.conf /etc/apache2/sites-enabled/
RUN rm -f /etc/apache2/site-available/000-default.conf
RUN rm -f /etc/apache2/site-enabled/000-default.conf
#RUN sed -i 's@Listen 80@Listen '"$APACHE_PORT"'@' /etc/apache2/ports.conf
RUN sed -i 's@ErrorLog ${APACHE_LOG_DIR}/error.log@ErrorLog /dev/stderr@' /etc/apache2/apache2.conf
#RUN sed -i 's@Require all granted@Require all denied@' /etc/apache2/apache2.conf

EXPOSE $APACHE_PORT
EXPOSE $APACHE_PORTS

# set the entrypoint script
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["apache2","-D","FOREGROUND"]
