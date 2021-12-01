FROM prioreg.azurecr.io/prio-data/uvicorn_deployment:2.1.0

COPY ./requirements.txt /
RUN pip install -r requirements.txt 

COPY ./router/* /router/
ENV GUNICORN_APP="router.app:app"
