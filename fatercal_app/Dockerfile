FROM ubuntu:17.10
LABEL maintainer="laurent.schaeffer313@gmail.com, adrien.cheype@ird.fr"

# apache-httpd environment variables
ENV APACHE_UID 33
ENV APACHE_GID 33
ENV APACHE_RUN_USER #${APACHE_UID}
ENV APACHE_RUN_GROUP #${APACHE_GID}
ENV APACHE_PORT 80
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2

# install the ubuntu packages needed
RUN apt update && apt install -y apache2 apache2-utils libapache2-mod-wsgi-py3 python3 python3-pip libpq-dev postgresql-client-9.6 vim && apt clean

# copy the application files
RUN mkdir /app
COPY manage.py requirements.txt /app/
COPY fatercal /app/fatercal
COPY fatercal-site /app/fatercal-site

# install python dependencies
RUN pip3 install -r /app/requirements.txt

# configure the apache server
COPY 000-default.conf /etc/apache2/sites-available/
RUN mkdir -p /var/lock/apache2; chown $APACHE_UID /var/lock/apache2
RUN sed -i 's@Listen 80@Listen '"$APACHE_PORT"'@' /etc/apache2/ports.conf
RUN sed -i 's@ErrorLog ${APACHE_LOG_DIR}/error.log@ErrorLog /dev/stderr@' /etc/apache2/apache2.conf
#RUN sed -i 's@Require all granted@Require all denied@' /etc/apache2/apache2.conf

EXPOSE $APACHE_PORT

# set the entrypoint script
COPY ./docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["apache2","-D","FOREGROUND"]