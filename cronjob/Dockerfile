FROM ubuntu:18.10
LABEL author="laurent.schaeffer313@gmail.com"

# Set Env Variable
ENV TZ=Pacific/Noumea
ENV DEBIAN_FRONTEND=noninteractive

# Install cron and postgresql-client
RUN apt-get update && apt-get -y install cron -y postgresql-client-10 -y tzdata

# Set Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy cron-psql file to the cron.d directory
COPY cron-psql /etc/cron.d/cron-psql

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cron-psql

# Apply cron job
RUN crontab /etc/cron.d/cron-psql

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && env >> /etc/environment && tail -f /var/log/cron.log
