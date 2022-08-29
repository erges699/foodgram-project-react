FROM python:3.7-slim 

WORKDIR /app

COPY ./foodgram-project-react/backend/requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./foodgram-project-react/backend/foodgram .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
