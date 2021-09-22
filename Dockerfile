# syntax=docker/dockerfile:1

FROM pytorch/pytorch

WORKDIR /voice2text

RUN apt-get -y update
RUN apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY voice2text .

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]