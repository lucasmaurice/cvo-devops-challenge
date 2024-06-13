import boto3
from random import randint
import sys

BUCKET_COUNT = 10
BUCKET_NAME_PREFIX = "djls-cvo-"

s3 = boto3.resource('s3')


# Create the buckets and put some objects in them with random sizes.
# If the bucket already exists, skip it and do not add any objects.
def create_data(prefix: str, count: int, file_max_count: int = 100):
    buckets_list = s3.buckets.all()
    existing_bucket_names = [bucket.name for bucket in buckets_list]
    for i in range(count):
        bucket_name = f"{prefix}{i}"
        if bucket_name in existing_bucket_names:
            print(f"Bucket {bucket_name} already exists, skipping")
            continue

        print(f"Creating bucket {bucket_name}")
        bucket = s3.create_bucket(Bucket=bucket_name)

        print(f"Putting objects in bucket {bucket_name}")
        for i in range(randint(10, file_max_count)):
            bucket.put_object(Key=f"file{i}.txt", Body="a" * (1024*1024*randint(1, 10)))


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
    print("Usage: python3 test_data.py [create|delete]")
    sys.exit(1)


if __name__ == "__main__":
    # Get the action from the command line
    if len(sys.argv) < 2:
        print_usage()
    action = sys.argv[1]

    # Perform the specified action
    match action:
        case "create":
            create_data(BUCKET_NAME_PREFIX, BUCKET_COUNT)
        case "delete":
            delete_data(BUCKET_NAME_PREFIX)
        case _:
            print_usage()
