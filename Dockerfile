# Import python image from Docker Hub
FROM python:3.12.3-slim-bullseye

# Update software on VM
RUN apt-get update && apt-get install -y \
    gnupg \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install and set path for Google Cloud SDK
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-sdk

ENV PATH="$PATH:/usr/lib/google-cloud-sdk/bin"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Application will be stored in /app directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app contents to project root
COPY . .

# Run entry point for gcloud authentication
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Debugging - Check if entrypoint.sh is copied and has executable permissions
RUN ls -la /app

# Free port 8000
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

# Run WSGI for production
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "justitia.wsgi:application"]