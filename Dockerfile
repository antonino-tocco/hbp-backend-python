FROM tiangolo/uwsgi-nginx-flask:python3.8

# set the working directory in the container
WORKDIR /usr/app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -e https://github.com/HumanBrainProject/openid_http_client.git#egg=openid_http_client&subdirectory=openid_http_client
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./ .

ADD import-task.sh /root/import-task.sh

# Give execution rights on the cron scripts
RUN chmod 0644 /root/import-task.sh

#Install Cron
RUN apt-get update
RUN apt-get -y install cron

# Add the cron job
RUN crontab -l | { cat; echo "0 0 * * * bash /root/import-task.sh"; } | crontab -

# Run the command on container startup
CMD cron

# command to run on container start
RUN chmod +x wait_to_start.sh
CMD ["./wait_to_start.sh"]