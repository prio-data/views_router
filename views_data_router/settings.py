

from environs import Env

env = Env()
env.read_env()

TRANSFORMER_URL = env.str("TRANSFORMER_URL")
BASE_DATA_RETRIEVER_URL = env.str("BASE_DATA_RETRIEVER_URL")
CACHE_FOLDER = env.str("CACHE_FOLDER")
