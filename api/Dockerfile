FROM python:3.9
WORKDIR /app

ADD requirements.txt  ./
RUN  pip3 install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED True

CMD ["python3","app.py"]