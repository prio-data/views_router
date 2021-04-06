"""
Required settings:
* Env:
    - KEY_VAULT_URL
* Secrets:
    - BLOB_STORAGE_CONNECTION_STRING
* Config:
    - TRANSFORMER_URL
    - BASE_DATA_RETRIEVER_URL
    - BLOB_CONTAINER_NAME
    - LOG_LEVEL
"""
import environs
from fitin import views_config

env = environs.Env()
env.read_env()
config = views_config(env.str("KEY_VAULT_URL"))
