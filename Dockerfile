# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install flask kafka-python pyspark pymongo

# Expose ports for Flask and potential other services
EXPOSE 5000 8080

# Define environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=/app/dashboard/app.py

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$SERVICE" = "main" ]; then\n\
    python /app/main.py\n\
elif [ "$SERVICE" = "dashboard" ]; then\n\
    flask run --host=0.0.0.0 --port=5000\n\
else\n\
    echo "Please specify SERVICE as either main or dashboard"\n\
    exit 1\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]