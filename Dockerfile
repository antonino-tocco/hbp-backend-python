FROM tiangolo/uwsgi-nginx-flask:python3.8

# set the working directory in the container
WORKDIR /usr/app

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install https://github.com/HumanBrainProject/openid_http_client.git#egg=openid_http_client&subdirectory=openid_http_client
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./ .

# command to run on container start
RUN chmod +x wait_to_start.sh
CMD ["./wait_to_start.sh"]