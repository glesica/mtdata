FROM python:3.9.7-slim-bullseye

VOLUME /data

RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY mtdata mtdata/
COPY pyproject.toml ./
COPY README.md ./

RUN FLIT_ROOT_INSTALL=1 python -m flit install

RUN mkdir /work
WORKDIR /work

CMD ["python", "-m", "mtdata"]
