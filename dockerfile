FROM python

WORKDIR /app

COPY src src
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "/app/src/main.py"]
