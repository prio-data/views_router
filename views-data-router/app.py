""" Very simple router that simply proxies to various data sources and transformers.
Built to make this "conversation" flow smoothly.

Also caches each request, which works well with
"""

import os
import logging

import requests
import fastapi

import caching
from caching import cache
import settings
from paths import nav_summary 

try:
    logging.basicConfig(level=getattr(logging,settings.LOG_LEVEL))
except AttributeError:
    pass

logger = logging.getLogger(__name__)

URLS = {
    "trf": settings.TRANSFORMER_URL,
    "base": settings.BASE_DATA_RETRIEVER_URL 
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
        content = cache.get(loa,dest,path)
    except caching.NotCached:
        logging.info("Retrieving content for %s - %s - %s",loa,dest,path)
        try:
            url = URLS[dest]
        except KeyError:
            return fastapi.Response(f"Dest {dest} not registered",
                    status_code=404)

        proxy = requests.get(os.path.join(url,loa,path))

        if proxy.status_code == 200:
            content = proxy.content
            logging.info("Stashing %s - %s - %s",loa,dest,path)
            cache.store(content,loa,dest,path)
        else: 
            return fastapi.Response(content=f"Proxied {proxy.content}",
                    status_code=proxy.status_code)
    else:
        logging.info("Used cached data for %s - %s - %s",loa,dest,path)

    return fastapi.Response(content=content)
