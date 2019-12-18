from openalea.core.path import path
from openalea.core import settings

# infos about provenance db
REMOTE = False

# SSH
PROVDB_SSH_ADDR = "134.158.247.32"
SSU_USERNAME="ubuntu"
SSH_PKEY="/home/gaetan/.ssh/id_rsa"
# REMOTE_DB_ADDR=('127.0.0.1', 27017)

# Mongo
MONGO_ADDR='127.0.0.1'
MONGO_PORT = 27017

# file infos
PROVENANCE_PATH = path(settings.get_openalea_home_dir()) / 'provenance'
TMP_PATH = path(settings.get_openalea_home_dir()) / "execution_data"
CACHE_PATH = path(settings.get_openalea_home_dir()) / "cached_data"
