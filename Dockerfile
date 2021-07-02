FROM prioreg.azurecr.io/uvicorn-deployment 

COPY ./requirements.txt /
RUN pip install -r requirements.txt 

COPY ./router/* /router/
ENV APP="router.app:app"
