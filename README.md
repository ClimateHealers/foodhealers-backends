# foodhealers-backends

## Getting started

DB Schema - https://www.figma.com/file/RAQ9yIL1fJPGAbpEMomrhI/ClimateHealer-Backends?type=whiteboard&node-id=989-2399&t=pElSGZum3xbircuK-0

### Set up env

python3 -m venv climatehealersenv -- install env and name it

### Activate Env

source climatehealersenv/bin/activate -- in linux
envname\Scripts\activate -- windows

### Setup PostGresql

DB Name - your database name 
username - postgres
PASSWORD - Your password
HOST - localhost

## Run Locally

Activate above env and run the following commands
pip install -r requirements.txt
python manage.py runserver

## Run Celery

### celery

celery -A foodhealers_backend worker -l INFO

# celery -A foodhealers_backend beat --loglevel=info