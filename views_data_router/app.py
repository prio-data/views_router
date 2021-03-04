"""
Very simple router that simply proxies to various data sources and transformers.
Built to make this "conversation" flow smoothly.

Also caches each request, which works well with
"""

import os
import requests
import fastapi
import caching
import settings

URLS = {
    "trf": settings.TRANSFORMER_URL,
    "base": settings.BASE_DATA_RETRIEVER_URL 
}

app = fastapi.FastAPI()
cache = caching.ByteFileCache(settings.CACHE_FOLDER)

@app.get("/{loa}/{dest}/{path:path}")
def route(loa:str,dest:str,path:str):
    """
    Proxies the request to a given _destination_ (host),
    requesting the _path_ with the _loa_ prepended.
    """

    try:
        content = cache.get(loa,dest,path)
    except caching.NotCached:
        try:
            url = URLS[dest]
        except KeyError:
            return fastapi.Response(f"Dest {dest} not registered",
                    status_code=404)

        proxy = requests.get(os.path.join(url,loa,path))

        if not proxy.status_code == 200:
            return fastapi.Response(content=f"Proxied {proxy.content}",
                    status_code=proxy.status_code)
        content = proxy.content
        cache.store(content,loa,dest,path)

    return fastapi.Response(content=content)
