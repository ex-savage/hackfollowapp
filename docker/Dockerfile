FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY requirements.txt /code/
COPY setup.py /code/
RUN pip install -r requirements.txt


COPY hackfollow /code/hackfollow
RUN pip install .
#ENTRYPOINT ["hackapp"]
