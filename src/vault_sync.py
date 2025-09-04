from os.path import dirname, join

from dotenv import load_dotenv

from app_config import AppConfig
from s3_client import S3Client

def get_appconfig() -> AppConfig:
    return AppConfig.from_file(join(dirname(__file__), "config.yaml"))
    

if __name__ == "__main__":
    load_dotenv()
    config = get_appconfig()
    
    client = S3Client(config.get("access_key", "secret_key", "bucket_name", "bucket_region", "local_path", "vault_name"))