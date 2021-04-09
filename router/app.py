""" 
Router that simply proxies to various data sources and transformers.
Built to make this "conversation" flow smoothly.

Also caches each request, which works well with
"""

import os
import logging

import requests
import fastapi

from . import caching,settings

logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
logger.setLevel(logging.WARNING)

try:
    logging.basicConfig(level=getattr(logging,settings.config("LOG_LEVEL")))
except AttributeError:
    pass

logger = logging.getLogger(__name__)

URLS = {
    "trf": settings.config("TRANSFORMER_URL"),
    "base": settings.config("BASE_DATA_RETRIEVER_URL") 
}

app = fastapi.FastAPI()
cache = caching.BlobStorageCache(
        settings.config("BLOB_STORAGE_CONNECTION_STRING"),
        settings.config("BLOB_STORAGE_ROUTER_CACHE")
    )

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
