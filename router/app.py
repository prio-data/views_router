""" 
Router that simply proxies to various data sources and transformers.
Built to make this "conversation" flow smoothly.

Also caches each request, which works well with
"""

import os
import logging

import requests
import fastapi

import caching
from caching import cache
from settings import config

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

try:
    logging.basicConfig(level=getattr(logging,config("LOG_LEVEL")))
except AttributeError:
    pass

logger = logging.getLogger(__name__)

URLS = {
    "trf": config("TRANSFORMER_URL"),
    "base": config("BASE_DATA_RETRIEVER_URL") 
}

app = fastapi.FastAPI()

@app.get("/nav/{path:path}")
def nav_path(path:str):
    """
    Returns a JSON response with: 
        The path shifted in TIME :param n: places.
        The bounds of the path (start-end)
    """
    
    try:
        navObject = nav_summary(path) 
    except ValueError as ve:
        return fastapi.Response(str(ve),status_code=400)
    else:
        return navObject

@app.get("/{loa}/{dest}/{path:path}")
def route(loa:str,dest:str,path:str):
    """
    Proxies the request to a given _destination_ (host),
    requesting the _path_ with the _loa_ prepended.
    """
    try:
        base_url = URLS[dest]
    except KeyError:
        return fastapi.Response(f"Dest {dest} not registered",
                status_code=404)
    url = os.path.join(base_url,loa,path)

    try:
        content = cache.get(loa,dest,path)
    except caching.NotCached:
        logger.info("Fetching %s",url)

        proxy = requests.get(url)

        if proxy.status_code == 200:
            logger.info("Stashing %s",url)
            content = proxy.content
            cache.store(content,loa,dest,path)
        else: 
            return fastapi.Response(content=f"Proxied {proxy.content}",
                    status_code=proxy.status_code)
    else:
        logger.info("Used cache for %s",url)

    return fastapi.Response(content=content)
