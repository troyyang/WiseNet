#!/bin/sh

# check if we are on a Debian or Ubuntu system
echo "Loading .env file..."
# Check if .env file exists and load environment variables
if [ -f ./.env ]; then
    if [ -r ./.env ]; then
        . ./.env  # Use '.' instead of 'source'
    else
        echo "You do not have permission to read the .env file. Please check the file permissions."
        exit 1
    fi
else
    echo ".env file not found. Please create it and try again."
    exit 1
fi

# Validate required environment variables
if [ -z "$APP_LOG_LEVEL" ]; then
    echo "APP_LOG_LEVEL environment variable is not set. Please set it in the .env file."
    exit 1
fi

if [ -z "$APP_WORKERS" ]; then
    echo "APP_WORKERS environment variable is not set. Please set it in the .env file."
    exit 1
fi
echo "APP_LOG_LEVEL: $APP_LOG_LEVEL"
echo "APP_WORKERS: $APP_WORKERS"
echo "Running the application..."
uvicorn main:app --host 0.0.0.0 --port 8088 --log-level ${APP_LOG_LEVEL:-info} --workers ${APP_WORKERS:-4}