This utility automatically synchronizes Obsidian vault with your S3 bucket.

Use it for easy backups and for portability between devices.

# Configuration
These system environment variables are required. Set them before execution, or create a file named `.env` with the following variables:

```
AWS_ACCESS_KEY="my_access_key"
AWS_SECRET_KEY="my_secret_key"

S3_BUCKET_NAME="my-bucket-name"
S3_REGION="my-bucket-region"

LOCAL_VAULT_PATH="C:\path\to\vault" # The directory containing the vault, NOT the vault's root directory

VAULT_NAME="My Vault" # The vault's root directory

# With the above configuration, vault_sync will synchronize the contents
#  of "C:\path\to\vault\My Vault" with the s3 resources at
#  s3://my-bucket-name/My Vault/*
```

## Install Requirements
`pip install -r requirements.txt`

# Usage
Execute `vault_sync.py` with one of the following arguments:

  - **sync**: The main operation. Uploads local vault to s3.
  - **download**: Downloads the vault from the S3 bucket, overwriting the local vault. Perform a local backup first to be safe.
  - **backup**: Creates a local backup in the same parent directory as the vault.
  - **interactive / -i**: Launch an interactive loop for entering commands. Good for testing.