import boto3
from random import randint
import sys

BUCKET_COUNT = 20
BUCKET_NAME_PREFIX = "djls-cvo-"
MIN_FILES = 1000
MAX_FILES = 10000

s3 = boto3.resource('s3')


# Create the buckets and put some objects in them with random sizes.
# If the bucket already exists, skip it and do not add any objects.
def create_data(prefix: str, refill: bool = False):
    buckets_list = s3.buckets.all()
    existing_bucket_names = [bucket.name for bucket in buckets_list]
    for i in range(BUCKET_COUNT):
        bucket_name = f"{prefix}{i}"
        if bucket_name in existing_bucket_names and not refill:
            print(f"Bucket {bucket_name} already exists, skipping")
            continue

        print(f"Creating bucket {bucket_name}")
        if i < 10:
            bucket = s3.create_bucket(Bucket=bucket_name)
        elif i < 12:
            bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'})
        elif i < 14:
            bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})
        else:
            bucket = s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})

        object_to_put = randint(MIN_FILES, MAX_FILES)
        print(f"Putting {object_to_put} objects in bucket {bucket_name}")
        for i in range(object_to_put):
            bucket.put_object(Key=f"file{i}.txt", Body="a" * (1024*randint(100, 1000)))


# Empty the buckets and delete them
def delete_data(prefix: str):
    buckets_list = s3.buckets.all()
    for bucket in buckets_list:
        if bucket.name.startswith(prefix):
            print(f"Emptying bucket {bucket.name}")
            bucket.objects.delete()
            print(f"Deleting bucket {bucket.name}")
            bucket.delete()


# Print the usage message and exit
def print_usage():
    print("Usage: python3 test_data.py [create|delete|update]")
    sys.exit(1)


if __name__ == "__main__":
    # Get the action from the command line
    if len(sys.argv) < 2:
        print_usage()
    action = sys.argv[1]

    # Perform the specified action
    match action:
        case "create":
            create_data(BUCKET_NAME_PREFIX)
        case "update":
            create_data(BUCKET_NAME_PREFIX, refill=True)
        case "delete":
            delete_data(BUCKET_NAME_PREFIX)
        case _:
            print_usage()
