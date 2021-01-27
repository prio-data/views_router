import io
import os
import requests
import fastapi
import pandas as pd
from environs import Env

env = Env()
env.read_env()

BASE_URL = "http://0.0.0.0:8001"
TRF_URL = "http://0.0.0.0:8002"
CACHE="./cache"

URLS = {
    "trf": env("TRF_URL"),
    "base": env("BASE_URL")
}

app = fastapi.FastAPI()


@app.get("/{loa}/{dest}/{path:path}")
def route(loa:str,dest:str,path:str):
    cachepath = os.path.join(env("CACHE"),loa,os.path.join(dest,path))
    if cachepath[-1] == "/":
        cachepath = cachepath[:-1]

    try:
        with open(cachepath,"rb") as f:
            content = f.read()
    except FileNotFoundError:
        try:
            url = URLS[dest]
        except KeyError:
            return fastapi.Response(f"Dest {dest} not registered",
                    status_code=404)

        proxy = requests.get(os.path.join(url,loa,path))

        if not proxy.status_code == 200:
            return fastapi.Response(content=proxy.content,
                    status_code=proxy.status_code)

        content = proxy.content
        cachefolder,_ = os.path.split(cachepath)

        try:
            os.makedirs(cachefolder)
        except FileExistsError:
            pass
        with open(cachepath,"wb") as f:
            f.write(content)

    fake_file = io.BytesIO(content)
    data = pd.read_parquet(fake_file)
    fake_file.seek(0)
    fake_file.truncate()

    return fastapi.Response(content=content)
