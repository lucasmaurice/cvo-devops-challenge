from datetime import datetime

import boto3
from dateutil.tz import tzutc
from mypy_boto3_s3 import S3Client


COST_PER_GB = 0.023
COST_PER_BYTE = COST_PER_GB / 1024 / 1024 / 1024


def get_bucket(name):
    print(f"Getting bucket with name {name}")

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(name)

    client = boto3.client("s3")

    last_modified = datetime.min
    last_modified = last_modified.replace(tzinfo=tzutc())
    bucket_object_count = 0
    bucket_size = 0

    paginator = client.get_paginator('list_objects_v2')
    for objects in paginator.paginate(Bucket=bucket.name):
        if not (contents := objects.get("Contents")):
            continue
        for bucket_object in contents:
            if (new_last_modified := bucket_object["LastModified"]) > last_modified:
                last_modified = new_last_modified
            bucket_object_count += 1
            bucket_size += bucket_object["Size"]

    if bucket_object_count == 0:
        return None

    return dict(
        name=name,
        creation_date=bucket.creation_date,
        nb_files=bucket_object_count,
        total_size_bytes=bucket_size,
        last_modified=last_modified,
        cost=round(COST_PER_BYTE * bucket_size, 2),
    )


def list_buckets():
    client: S3Client = boto3.client("s3")

    all_buckets_info = []
    for bucket in client.list_buckets()["Buckets"]:
        print(f'Getting bucket info for {bucket["Name"]}')
        if bucket_info := get_bucket(bucket["Name"]):
            all_buckets_info.append(bucket_info)

    return all_buckets_info
