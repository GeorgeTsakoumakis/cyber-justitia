#!/bin/sh

set -e

mkdir -p /app/credentials

gcloud auth activate-service-account --key-file=/run/secrets/gcloud-key

gcloud secrets versions access latest --secret="ai-cloud-key" --project="$PROJECT_ID" > /app/credentials/credentials.json

export GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/credentials.json

exec "$@"
