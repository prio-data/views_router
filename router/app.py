""" 
Router that simply proxies to various data sources and transformers.
Built to make this "conversation" flow smoothly.

Also caches each request, which works well with
"""

import os
import logging

import requests
from fastapi import FastAPI,Response

from . import caching,settings,paths

try:
    logging.basicConfig(level=getattr(logging,settings.config("LOG_LEVEL")))
except AttributeError:
    pass

logger = logging.getLogger(__name__)

app = FastAPI()

cache = caching.RESTCache(
            settings.config("DATA_CACHE_URL") + "/files"
        )

remotes = paths.Remotes(
            trf=os.path.join(settings.config("TRANSFORMER_URL"),"apply"),
            base=os.path.join(settings.config("BASE_DATA_RETRIEVER_URL"),"fetch")
        )

@app.get("/{raw_path:path}")
def route(raw_path:str):
    """
    Requests the provided path from a remote, either from cache or over HTTP.
    """
    try:
        path = paths.Path.parse(raw_path)
    except ValueError as ve:
        return Response(f"Path {raw_path} could not resolve: {str(ve)}", status_code=404)

    url = path.url(remotes)
    cache_name = path.path

    try:
        content = cache.get(cache_name)

    except caching.NotCached:
        response = requests.get(url)

        if response.status_code == 200:
            logger.info("Stashing %s",url)
            content = response.content
            cache.store(content,cache_name)

        else: 
            return Response(
                    content=f"HTTP error from {url}: {response.content}",
                    status_code = response.status_code
                    )

    return Response(content=content)
