"""
Cache implementations
"""
from typing import List
import os
from abc import ABC,abstractmethod
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError
from settings import config

class NotCached(Exception):
    pass

class Cache(ABC):
    @abstractmethod
    def store(self,content:bytes,*identifiers:List[str]):
        pass
    @abstractmethod
    def get(self,*identifiers:List[str]):
        pass

class ByteFileCache(Cache):
    def __init__(self,base_path):
        self.base_path = base_path

    def store(self,content,*identifiers):
        path = self._resolve(*identifiers) 
        with open(path,"wb") as f:
            f.write(content)

    def get(self,*identifiers):
        path = self._resolve(*identifiers) 
        try:
            with open(path,"rb") as f:
                return f.read()
        except FileNotFoundError as fnf:
            raise NotCached from fnf 

    def _resolve(self,*identifiers)->str:
        path_elements = identifiers
        path = os.path.join(self.base_path,*path_elements)
        folder,_ = os.path.split(path)
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass
        if path[-1] == "/":
            path = path[:-1]
        return path 

    def __str__(self):
        return f"FileCache @ {self.base_path}"

class BlobStorageCache(Cache):
    def __init__(self,*_,**__):
        self.client = BlobServiceClient.from_connection_string(
                    config("BLOB_STORAGE_CONNECTION_STRING"),
                )
        self.container_client = self.client.get_container_client(
                    config("BLOB_STORAGE_ROUTER_CACHE"),
                )
    def store(self,content,*identifiers):
        path = os.path.join(*identifiers)
        blob_client = self.container_client.get_blob_client(path)
        blob_client.upload_blob(content)

    def get(self,*identifiers):
        path = os.path.join(*identifiers)
        try:
            blob = (self.container_client
                    .get_blob_client(path)
                    .download_blob()
                )
        except ResourceNotFoundError as rnf:
            raise NotCached from rnf

        return blob.content_as_bytes()

class DictCache(Cache):
    """
    Just caches in a dict
    Useful for testing
    """
    def __init__(self,*_,**__):
        self.storage = {}

    def store(self,content,*identifiers):
        self.storage[self._resolve(*identifiers)] = content

    def get(self,*identifiers):
        try:
            return self.storage[self._resolve(*identifiers)]
        except KeyError as ke:
            raise NotCached from ke

    @staticmethod
    def _resolve(*identifiers)->str:
        return ".".join(identifiers)

    def __str__(self):
        return f"Dictcache {self.storage}"

cache = BlobStorageCache()