FROM python:3.11.3

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    python3-dev \
    gcc \
    python3-psycopg2 \
    tzdata \
    gettext \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt  /app/
RUN pip install -r requirements.txt 

ADD . /app/
EXPOSE 3978

ENTRYPOINT ["python" , "app.py"]
