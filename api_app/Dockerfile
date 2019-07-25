FROM ubuntu:18.10
LABEL author="laurent.schaeffer313@gmail.com"


# Install postgresql-client and python package
RUN apt-get update && apt-get -y install postgresql-client-10 -y tzdata
RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev vim
RUN apt-get install -y nginx
# Set Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# copy the application files
RUN mkdir /app

# Give the right of the folder and file inside to the application
RUN chown -R www-data /app

COPY . /app
WORKDIR /app

# install python dependencies
RUN pip3 install -r /app/requirements.txt

COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh

# Run the command on container startup
CMD ["./start.sh","-D","FOREGROUND"]