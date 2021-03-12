
from environs import Env
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.appconfiguration import AzureAppConfigurationClient

env = Env()
env.read_env()

CACHE_FOLDER = env.str("CACHE_FOLDER","cache")

secret_client = SecretClient(env.str("KEY_VAULT_URL"),credential=DefaultAzureCredential())

BLOB_STORAGE_CON_STR = secret_client.get_secret("blob-storage-connection-string").value

app_config_client = AzureAppConfigurationClient.from_connection_string(
        secret_client.get_secret("app-settings-connection-string").value
        )

get_remote_config = lambda k: app_config_client.get_configuration_setting(k).value

TRANSFORMER_URL = get_remote_config("data-transformer-url")
BASE_DATA_RETRIEVER_URL = get_remote_config("base-data-retriever-url")
BLOB_CONTAINER_NAME = get_remote_config("router-cache-container-name")


# TODO these should be queried from somewhere, maybe a service responsible
# for keeping track of various DB metadata things?
DB_MIN_YEAR = 1989
DB_MAX_YEAR = 2020
