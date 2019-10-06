FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock -r > requirements.txt
RUN pip install -r /tmp/requirements.txt

RUN mkdir /code
WORKDIR /code
COPY . /code/