FROM prioreg.azurecr.io/prio-data/uvicorn_deployment:1.2.0

COPY ./requirements.txt /
RUN pip install -r requirements.txt 

COPY ./router/* /router/
ENV APP="router.app:app"
