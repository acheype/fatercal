FROM ubuntu:18.10
LABEL author="laurent.schaeffer313@gmail.com"


# Install postgresql-client and python package
RUN apt-get update && apt-get -y install postgresql-client-10 -y tzdata
RUN apt-get update && apt-get install -y python3 python3-pip libpq-dev vim

# Set Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# copy the application files
RUN mkdir /app
COPY app.py /app/
COPY function.py /app/
COPY sql.py /app/
COPY requirements.txt /app/

# install python dependencies
RUN pip3 install -r /app/requirements.txt

# Run the command on container startup
CMD ["python3 app.py","-D","FOREGROUND"]