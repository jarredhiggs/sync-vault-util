from os.path import dirname, join
import sys

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

def execute(command: str) -> None:
    global config
    global s3_client
    
    commands = {
        "sync": s3_client.upload_vault,
        "download_remote": s3_client.download_vault,
        "backup": s3_client.backup_local,
        "interactive (-i)": interactive_loop,
        "quit": exit
    }
    
    aliases = {
        "upload": "sync",
        "use_remote": "download_remote",
        "download": "download_remote",
        "backup_local": "backup",
        "interactive": "interactive (-i)",
        "-i": "interactive (-i)",
        "exit": "quit"
    }
    
    command = aliases[command] if command in aliases else command
    
    if command not in commands:
        print(f"\"{command}\" is not a valid command. Available commands are {list(commands.keys())}")
        return
    
    commands[command]()

def interactive_loop() -> None:
    while True:
        command = input(">> ").strip().lower()
        
        if not command:
            continue 
        
        execute(command)
    

if __name__ == "__main__":
    startup()
    
    if len(sys.argv) > 1:
        execute(sys.argv[1])
        sys.exit(0)
    
    print("No arguments provided! Available options are `sync`, `download`, `backup`, `interactive / -i`, `help`")