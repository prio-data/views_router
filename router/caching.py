"""
Cache implementations
"""
from io import BytesIO
from typing import List
import os
import requests
from abc import ABC,abstractmethod
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

class NotCached(Exception):
    pass

class RESTCache:
    def __init__(self, url):
        self._url = url

    def url(self, path):
        return self._url + "/" + path

    def store(self,content,key):
        rsp = requests.post(self.url(key), files = {"file": BytesIO(content)})
        rsp.raise_for_status()

    def get(self,key):
        rsp = requests.get(self.url(key))

        try:
            assert rsp.status_code != 404
        except AssertionError:
            raise NotCached

        return rsp.content

class BlobStorageCache:
    def __init__(self,connection_string,container):
        self.client = BlobServiceClient.from_connection_string(
                    connection_string,
                )
        self.container_client = self.client.get_container_client(
                    container,
                )
    def store(self,content,key):
        blob_client = self.container_client.get_blob_client(key)
        blob_client.upload_blob(content)

    def get(self,key):
        try:
            blob = (self.container_client
                    .get_blob_client(key)
                    .download_blob()
                )
        except ResourceNotFoundError as rnf:
            raise NotCached from rnf

        return blob.content_as_bytes()
