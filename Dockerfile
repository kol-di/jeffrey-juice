FROM python:3.10.15-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py config.yaml ./
COPY src ./src
COPY data ./data

CMD ["python3", "main.py"]