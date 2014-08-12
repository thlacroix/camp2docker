FROM ubuntu

RUN apt-get update && apt-get install -y python-pip

ADD requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

ADD camp2docker /home/camp2docker

WORKDIR /home/camp2docker

ENTRYPOINT ["python", "camp2docker.py"]

CMD ["services"]
