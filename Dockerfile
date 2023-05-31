FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app/
WORKDIR /app/

# Copy the code to /app/
COPY . /app/

# Install the requirements using pip
RUN apt-get update && apt-get install -y git && pip install -r requirements.txt
# Create the directory /home/ubuntu
RUN mkdir -p /home/ubuntu
syntax=docker/dockerfile:experimental
# ARG FIREBASE_JSON  #for passing args parameter in command
# RUN echo "$FIREBASE_JSON" > /home/ubuntu/food-healers-b6ab8-firebase-adminsdk-dqe5w-9169a69607.json
# RUN echo "FIREBASE_JSON value: $FIREBASE_JSON"
RUN --mount=type=secret,id=FIREBASE_JSON_SECRET \
    echo "$ENVFILE" > /home/ubuntu/.local.env && \
    echo "$FIREBASE_JSON" > /home/ubuntu/food-healers-b6ab8-firebase-adminsdk-dqe5w-9169a69607.json && \
    echo "FIREBASE_JSON value: $FIREBASE_JSON"

RUN echo "$ENVFILE" > /home/ubuntu/.local.env

#check
# Set environment variables for remote database connection
ENV DB_ENGINE=django.db.backends.postgresql
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=foodhealersstagging
ENV DB_USER=postgres
ENV DB_PASSWORD=root

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
