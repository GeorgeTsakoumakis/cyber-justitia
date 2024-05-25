FROM python:3.12.3-slim-bullseye

RUN apt-get update && apt-get install -y \
    gnupg \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://sdk.cloud.google.com | bash

ENV PATH=$PATH:/root/google-cloud-sdk/bin

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]