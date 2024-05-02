FROM alpine:3.8

RUN mkdir /var/flaskapp

WORKDIR /var/flaskapp

COPY .  .

RUN apk update

RUN apk add python3

RUN pip3 install -r requirements.txt

EXPOSE 8080 

CMD ["python3","app.py"]
