import boto3
import os
from os.path import join, relpath
from shutil import copytree, rmtree

from util import debug

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
        
        debug(f"Initializing s3 client for {self.bucket_name}:{self.vault_name}")
        self.client = boto3.client('s3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.bucket_region,
        )    
        
        
    def _collect_local_files(self) -> list[str]:
        local_files = []
        directory = join(self.local_path, self.vault_name)
        for root, _, files in os.walk(directory):
            for file in files:
                local_path = join(root, file)
                rel_path = relpath(local_path, directory)
                local_files.append(join(self.vault_name, rel_path))
        return local_files
    
    
    def upload_vault(self) -> None:
        local_files = self._collect_local_files()
        s3_target_keys = {x.replace("\\", "/") for x in local_files}

        debug(f"Uploading: {len(local_files)} files.")
        for local_file in local_files:
            full_local_path = join(self.local_path, local_file)
            s3_key = local_file.replace("\\", "/")
            try:
                self.client.upload_file(full_local_path, self.bucket_name, s3_key)
            except Exception as e:
                print(f"Error uploading {full_local_path}: {e}")
                #TODO: Revert back to original state if sync fails
                print(f"!!!!+++++++++++++UPLOAD INCOMPLETE+++++++++++++!!!!")
                exit(1)
                
        debug("Upload complete, searching for extraneous keys in s3.")
        keys_to_delete = set()
        paginator = self.client.get_paginator('list_objects_v2')
        try:
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.vault_name + "/")
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        keys_to_delete.add(obj['Key']) if obj['Key'] not in s3_target_keys else None
        except Exception as e:
            print(f"Error listing S3 objects: {e}")
            #TODO: Revert back to original state if sync fails
            print(f"!!!!+++++++++++++INCOMPLETE REMOVAL OF DELETED FILES FROM S3+++++++++++++!!!!")
            exit(1)
        
        # TODO: delete_payload does not work with more than 1000 items. Add support for multiple delete requests
        keys_to_delete = list(keys_to_delete)
        
        debug(f"Keys to delete: {keys_to_delete}")
        
        if len(keys_to_delete) > 0:
            delete_payload = {
                'Objects': [{'Key': key} for key in keys_to_delete]
            }
            
            debug("Deleting...")
            
            try:
                response = self.client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete=delete_payload
                )
                if 'Errors' in response and response['Errors']:
                    for error in response['Errors']:
                        print(f"Error deleting {error['Key']}: {error['Message']}")
                        raise RuntimeError("Error executing client.delete_objects")
            except Exception as e:
                print(f"An error occurred during S3 deletion: {e}")
                print(f"!!!!+++++++++++++INCOMPLETE REMOVAL OF DELETED FILES FROM S3+++++++++++++!!!!")
                exit(1)
    
    
    def backup_local(self) -> None:
        if self.local_path is None or self.vault_name is None:
            print("Local path or vault name is not set!")
            return
        full_vault_path = join(self.local_path, self.vault_name)
        full_backup_path = f"{full_vault_path}_bak"
        debug(f"Creating backup vault: {full_backup_path}")
        try:
            copytree(full_vault_path, full_backup_path, dirs_exist_ok=True)
        except Exception as e:
            print(f"Failed to create local backup at {full_backup_path}: {e}")
        debug(f"Backup created at {full_backup_path}")
        
    # TODO: Parallelize downloads
    def download_vault(self) -> None:
        self.backup_local()
                    
        s3_keys = set()
        paginator = self.client.get_paginator('list_objects_v2')
        
        debug("Downloading files from s3...")
        
        try:
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=self.vault_name + "/")
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        s3_keys.add(obj['Key'])
        except Exception as e:
            print(f"Error listing S3 objects: {e}")
            print(f"!!!!+++++++++++++DOWNLOAD INCOMPLETE+++++++++++++!!!!")
            exit(1)
            
        debug(f"Found {len(s3_keys)} files to download.")
        
        for s3_key in s3_keys:
            s3_key = s3_key
            
            local_file_path = join(self.local_path, s3_key)
            directory = os.path.dirname(local_file_path)
            
            if directory:
                os.makedirs(directory, exist_ok=True)
                
            try:
                self.client.download_file(self.bucket_name, s3_key, local_file_path)
            except Exception as e:
                print(f"Error downloading {s3_key}: {e}")
                print(f"!!!!+++++++++++++DOWNLOAD INCOMPLETE+++++++++++++!!!!")
        
        debug("Download complete, searching for extraneous local files.")
        
        local_file_list = self._collect_local_files()
        local_to_delete = {x.replace("\\", "/") for x in local_file_list} - s3_keys
        
        debug(f"Local files to delete: {len(local_to_delete)}")
        debug("Deleting...") if len(local_to_delete) > 0 else None
        
        for filename in local_to_delete:
            full_path = join(self.local_path, filename)
            try:
                os.remove(full_path)
            except Exception as e:
                print(f"Error deleting local file {full_path}: {e}")
                print(f"!!!!+++++++++++++INCOMPLETE REMOVAL OF EXTRA LOCAL FILES+++++++++++++!!!!")
                exit(1)
        
        debug("Vault download complete.")
    
    
    def delete_backup(self) -> None:
        if self.local_path is None or self.vault_name is None:
            print("Local path or vault name is not set!")
            return
        full_vault_path = join(self.local_path, self.vault_name)
        full_backup_path = f"{full_vault_path}_bak"
        debug(f"Deleting backup vault at: {full_backup_path}")
        try:
            rmtree(full_backup_path)
        except Exception as e:
            print(f"Failed to delete backup at {full_backup_path}: {e}")
        debug(f"Backup deleted at: {full_backup_path}")