FROM ubuntu

RUN apt-get update && apt-get install -y python-pip
ADD . /home/camp2docker

WORKDIR /home/camp2docker

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "camp2docker.py"]

CMD ["services"]
