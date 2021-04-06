FROM python:3.8

COPY ./requirements.txt /
RUN pip install -r requirements.txt 

COPY ./views_data_router/* /views_data_router/
WORKDIR /views_data_router

CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","--bind","0.0.0.0:80","app:app"]
