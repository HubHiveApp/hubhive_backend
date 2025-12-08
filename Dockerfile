FROM python:3.10-slim AS base

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY app ./app
COPY run.py ./run.py
COPY setup_database.py ./setup_database.py
COPY alembic.ini ./alembic.ini

EXPOSE 8000
CMD ["python", "run.py"]