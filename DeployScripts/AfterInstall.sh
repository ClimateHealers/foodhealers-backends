#!/bin/bash
. /home/ubuntu/food-env/bin/activate
pip install -r /home/ubuntu/foodhealers-backends/requirements.txt
cd /home/ubuntu/foodhealers-backends/
sudo chown -R ubuntu:ubuntu *
yes | python manage.py makemigrations
python manage.py makemigrations
python manage.py migrate
sudo systemctl restart codedeploy-agent.service
sudo systemctl restart foodhealers-gunicorn.service
sudo systemctl restart rabbitmq-server.service
sudo systemctl restart foodhealers-celery.service
sudo systemctl restart foodhealers-beat.service
echo "All done..."
exit 0
