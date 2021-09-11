FROM python:3.9.7-slim-bullseye

VOLUME /data

RUN mkdir /code
WORKDIR /code

RUN useradd --create-home mtdata
USER mtdata

COPY mtdata mtdata/
COPY requirements.txt ./
COPY pyproject.toml ./
COPY README.md ./

RUN pip install --user -r requirements.txt
RUN python -m flit install --user

WORKDIR /home/mtdata

CMD ["python", "-m", "mtdata"]
