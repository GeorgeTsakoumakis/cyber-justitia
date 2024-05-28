#!/bin/bash

# Project variables
PROJECT_ID="civil-hash-421214"
SA_NAME="cyber-justitia-docker"
KEY_FILE_PATH="/app/key.json"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Confirms file path and loads credentials from env to json file
echo "Key file path: $KEY_FILE_PATH"
JSON_STRING="$JSON_AUTH_DETAILS"

mkdir -p "$(dirname "$KEY_FILE_PATH")"

echo "$JSON_STRING" > "$KEY_FILE_PATH"

# Ensure the active account has necessary permissions
gcloud auth activate-service-account --key-file=$KEY_FILE_PATH

# Sets service account
gcloud config set account cyber-justitia-docker@civil-hash-421214.iam.gserviceaccount.com

# Checks the active account
gcloud auth list

# Sets credential file path for gcloud to find
export GOOGLE_APPLICATION_CREDENTIALS=$KEY_FILE_PATH

# Perform database migrations and collect static files
python manage.py makemigrations
python manage.py migrate --fake
python manage.py collectstatic --noinput

exec "$@"