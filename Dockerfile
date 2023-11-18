#builder stage
FROM python:3.11.6-slim-bullseye as builder

RUN apt-get update \
    && apt-get -y install libpq-dev gcc 

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin/:$PATH"

COPY requirements.txt .

RUN pip3 install -r requirements.txt

#operational stage
FROM python:3.11.6-slim-bullseye

RUN apt-get update \
    && apt-get -y install libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin/:$PATH"

WORKDIR /reviveme-be 

COPY . /reviveme-be/

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]