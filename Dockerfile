FROM python:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app/
WORKDIR /app/

# Copy the code to /app/
COPY . /app/

# Install the requirements using pip
RUN apt-get update && apt-get install -y git && pip install -r requirements.txt

# Set environment variables for remote database connection
# ENV DB_HOST=<remote_db_host>
# ENV DB_PORT=<remote_db_port>
# ENV DB_NAME=<remote_db_name>
# ENV DB_USER=<remote_db_user>
# ENV DB_PASSWORD=<remote_db_password>

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
