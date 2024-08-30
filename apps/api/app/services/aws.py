import boto3
import os
import requests
from uuid import uuid4
from botocore.exceptions import NoCredentialsError, ClientError

aws_access_key = os.getenv("AWS_ACCESS_KEY", "")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")

def upload_to_aws(url: str):
    bucket_name = "stories-summarizes"
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )

    try:
        s3_file_name = f"{uuid4().hex}.tmp"

        response = requests.get(url)
        response.raise_for_status()  

        with open(s3_file_name, 'wb') as file:
            file.write(response.content)

        s3.upload_file(s3_file_name, bucket_name, s3_file_name)
        print(f"File from URL {url} uploaded to {bucket_name} as {s3_file_name}.")

        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"
        return s3_url

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except FileNotFoundError:
        print(f"Temporary file {s3_file_name} was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
    except ClientError as e:
        print(f"Client error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    finally:
        if os.path.exists(s3_file_name):
            os.remove(s3_file_name)
