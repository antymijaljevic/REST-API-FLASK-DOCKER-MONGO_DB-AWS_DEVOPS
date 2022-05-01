# https://runnable.com/docker/python/docker-compose-with-flask-apps

# pulling from dockerhub
FROM python:3

# random directory in container
WORKDIR /user/src/app

# copy req to container pwd
COPY requirements.txt .

# run following in container
RUN pip install --no-cache-dir -r requirements.txt

# copy pwd to container pwd
COPY . .

# run command
CMD ["python", "app.py"]

# export FLASK_APP=app.py