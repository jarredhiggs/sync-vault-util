from os.path import dirname, join

from dotenv import load_dotenv

from app_config import AppConfig
from s3_client import S3Client

s3_client: S3Client = None
config: AppConfig = None

def get_appconfig() -> AppConfig:
    return AppConfig.from_file(join(dirname(__file__), "config.yaml"))

def startup() -> None:
    load_dotenv()
    
    global config
    global s3_client
    
    if not config:
        config = get_appconfig()
    if not s3_client:
        s3_client = S3Client(config.get("access_key", "secret_key", "bucket_name", "bucket_region", "local_path", "vault_name"))

def execute(command):
    global config
    global s3_client
    
    commands = {
        "upload": s3_client.upload_vault,
        "download": s3_client.download_vault,
        "sync": s3_client.download_vault
    }
    
    if command not in commands:
        print(f"\"{command}\" is not a valid command. Available commands are {list(commands.keys())}")
        return
    
    commands[command]()

if __name__ == "__main__":
    startup()
    while True:
        command = input(">> ").strip().lower()
        
        if not command:
            continue 
        
        execute(command)