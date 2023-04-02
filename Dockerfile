FROM python:3.11.2-slim-buster

COPY . .

RUN pip install -r requirements.txt

CMD ["python","horoscope.py"]