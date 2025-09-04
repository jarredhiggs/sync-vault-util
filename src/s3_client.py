import boto3

class S3Client():
    def __init__(self, config: dict):
        try:
            self.access_key = config["access_key"]
            self.secret_key = config["secret_key"]
            self.bucket_name = config["bucket_name"]
            self.bucket_region = config["bucket_region"]
            self.local_path = config["local_path"]
            self.vault_name = config["vault_name"]
        except KeyError as e:
            print(f"S3Client __init__ failure: {e} missing from config")
        
        self.client = boto3.client('s3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.bucket_region,
        )
    
    def upload_vault():
        pass
    
    def download_vault():
        pass
    
    def replace_old_local():
        pass