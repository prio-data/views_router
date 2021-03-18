
import os
from environs import Env
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.appconfiguration import AzureAppConfigurationClient

env = Env()
env.read_env()

PROD = env.bool("PRODUCTION","true")

def get_dev_kv(k):
    return requests.get(os.path.join(env.str("REST_ENV_URL",""),k)).content.decode()

if PROD:
    secret_client = SecretClient(env.str("KEY_VAULT_URL"),credential=DefaultAzureCredential())
    app_config_client = AzureAppConfigurationClient.from_connection_string(
            get_secret("app-settings-connection-string")
            )
    get_secret = lambda k: secret_client.get_secret(k).value
    get_config = lambda k: app_config_client.get_configuration_setting(k).value
else:
    get_secret = get_dev_kv 
    get_config = get_dev_kv

BLOB_STORAGE_CON_STR = get_secret("blob-storage-connection-string")

TRANSFORMER_URL = get_config("data-transformer-url")
BASE_DATA_RETRIEVER_URL = get_config("base-data-retriever-url")
BLOB_CONTAINER_NAME = get_config("router-cache-container-name")

# TODO these should be queried from somewhere, maybe a service responsible
# for keeping track of various DB metadata things?
DB_MIN_YEAR = 1989
DB_MAX_YEAR = 2020

LOG_LEVEL = get_config("log-level")

