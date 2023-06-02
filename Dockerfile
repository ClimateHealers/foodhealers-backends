FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app/
WORKDIR /app/

# Copy the code to /app/
COPY . /app/

# Install the requirements using pip
RUN apt-get update && apt-get install -y git && pip install -r requirements.txt

COPY food-healers-b6ab8-firebase-adminsdk-dqe5w-9169a69607.json $HOME

RUN cat food-healers-b6ab8-firebase-adminsdk-dqe5w-9169a69607.json
COPY local.env $HOME
RUN cat local.env
RUN ls -l $HOME
RUN pwd

# Set environment variables for remote database connection
ENV DB_ENGINE=django.db.backends.postgresql
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=foodhealersstagging
ENV DB_USER=postgres
ENV DB_PASSWORD=root
ENV FIREBASE_ADMIN_SDK=food-healers-b6ab8-firebase-adminsdk-dqe5w-9169a69607.json

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
