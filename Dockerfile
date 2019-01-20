FROM ubuntu:16.04

MAINTAINER Rogério Silva "rogerio@inventsis.com.br"

RUN apt-get update -y && \  
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

RUN clone http://github.com/engrogerio/pylaws

COPY . /

ENTRYPOINT [ "python3" ]

# CMD ["java", "-jar", "./tika_server/tika-server-1.20.jar --port 9999"]

CMD [ "./manage.py runserver" ]  