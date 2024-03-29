# FROM python:3.10.13-alpine3.19
# FROM python:3.12.2-alpine3.19
FROM python:3.10.13
WORKDIR /usr/src/app

RUN apt update && apt install -y \
    build-essential \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

RUN  pip install --upgrade pip

COPY requirements.txt ./
RUN pip install -r requirements.txt

EXPOSE 8000

COPY . .

CMD [ "uvicorn", "src.api.main:tenet", "--host", "0.0.0.0" ]