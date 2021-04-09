"""
Cache implementations
"""
from typing import List
import os
from abc import ABC,abstractmethod
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

class NotCached(Exception):
    pass

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
