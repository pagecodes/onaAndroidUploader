import sys
import os
import argparse
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def upload_to_s3(file_path, bucket_name, object_name=None):
    """
    Uploads a file to an S3 bucket using credentials found in environment variables.
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_path)

    # Check if file exists before attempting upload
    if not os.path.isfile(file_path):
        print(f"Error: File not found at '{file_path}'")
        return False

    # Instantiate S3 client
    # Boto3 will automatically look for AWS_ACCESS_KEY_ID and
    # AWS_SECRET_ACCESS_KEY in os.environ
    s3_client = boto3.client('s3')

    try:
        print(f"Starting upload of '{file_path}' to bucket '{bucket_name}'...")

        # Extra args can be used to set metadata, ContentType, or ACLs if needed.
        # For APKs, it's often good to set ContentType explicitly if you know it,
        # though S3 usually auto-detects.
        extra_args = {
            'ContentType': 'application/vnd.android.package-archive'
        }

        s3_client.upload_file(
            file_path,
            bucket_name,
            object_name,
            ExtraArgs=extra_args
        )

        print(f"Success! '{object_name}' uploaded to '{bucket_name}'.")
        return True

    except FileNotFoundError:
        print("Error: The file was not found.")
        return False
    except NoCredentialsError:
        print("Error: AWS credentials not found.")
        print("Please ensure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables are set.")
        return False
    except ClientError as e:
        # Catch specific AWS errors (like 403 Forbidden if IAM permissions are wrong)
        print(f"AWS Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Upload a file (APK) to an AWS S3 bucket using env vars for auth.")
    parser.add_argument("bucket", help="Name of the S3 bucket")
    parser.add_argument("filepath", help="Path to the file to upload")
    parser.add_argument("--key", help="Optional: specific key (path) to save the file as in S3", default=None)

    args = parser.parse_args()

    # Optional: Explicitly validate env vars are present if you strictly want to enforce this method.
    # Boto3 does this internally, but this provides faster user feedback.
    if not os.environ.get('AWS_ACCESS_KEY_ID') or not os.environ.get('AWS_SECRET_ACCESS_KEY'):
         print("Warning: AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not explicitly set in environment.")
         print("Attempting to proceed using other credential methods (config files, IAM roles)...")

    success = upload_to_s3(args.filepath, args.bucket, args.key)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
```{.python .filepath}
