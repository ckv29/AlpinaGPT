FROM python:3.13-alpine

WORKDIR /AlpinaGPT

COPY ./ .

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python","manage.py","runserver","0.0.0.0:8000"]