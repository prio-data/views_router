FROM python:3.8

COPY ./requirements.txt /
RUN pip install -r requirements.txt 

COPY ./router/* /router/

CMD ["gunicorn","-k","uvicorn.workers.UvicornWorker","--bind","0.0.0.0:80","router.app:app"]
