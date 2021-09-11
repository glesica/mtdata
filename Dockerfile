FROM python:3.9-slim-bullseye
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
VOLUME /data
CMD ["python", "-m", "mtdata", "--out", "/data"]
