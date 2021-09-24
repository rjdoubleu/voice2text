# syntax=docker/dockerfile:1

FROM pytorch/pytorch

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY $OPENAI_API_KEY

RUN apt-get -y update
RUN apt-get install -y ffmpeg

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY voice2text /voice2text

WORKDIR /voice2text

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]