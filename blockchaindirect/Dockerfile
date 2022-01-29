#FROM python:3.8-slim-buster
FROM python:3.8

#RUN apk update && apk add gcc

WORKDIR /app


COPY eth-fork-chains-arbitrage/requirements.txt requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY eth-fork-chains-arbitrage/*.py .

RUN mkdir /libraries

COPY libraries/ /libraries/

CMD [ "python", "-u", "front_run.py", "polygon"]