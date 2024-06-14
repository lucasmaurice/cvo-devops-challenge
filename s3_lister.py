from datetime import datetime

import boto3
from dateutil.tz import tzutc
from mypy_boto3_s3 import S3Client


COST_PER_GB = 0.023
COST_PER_BYTE = COST_PER_GB / 1024 / 1024 / 1024

AVAILABLE_GROUPS = ["", "region"]


def available_grouping(value: str):
    if value not in AVAILABLE_GROUPS:
        raise ValueError(f"Invalid grouping selected `{value}`. Must be one of {AVAILABLE_GROUPS}")
    return value


def get_bucket(name):
    print(f"Getting bucket with name {name}")

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(name)
    client = boto3.client("s3")

    last_modified = datetime.min
    last_modified = last_modified.replace(tzinfo=tzutc())
    bucket_object_count = 0
    bucket_size = 0
    bucket_location = ""

    paginator = client.get_paginator('list_objects_v2')
    for objects in paginator.paginate(Bucket=name):
        if not (contents := objects.get("Contents")):
            continue

        bucket_location = objects["ResponseMetadata"]["HTTPHeaders"]["x-amz-bucket-region"]

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
        region=bucket_location,
        cost=round(COST_PER_BYTE * bucket_size, 2),
    )


def list_buckets(group_by: str = ""):
    client = boto3.client("s3")

    all_buckets_info = {}

    for bucket in client.list_buckets()["Buckets"]:
        bucket_info = get_bucket(bucket["Name"])

        # Ignore empty buckets
        if not bucket_info:
            continue

        # Use the group_by tag to group the buckets - or use "all" if no grouping is selected
        current_group = "all"
        if group_by:
            current_group = bucket_info[group_by]

        # If the grouping tag is not in the dictionary, add it
        if current_group not in all_buckets_info:
            all_buckets_info[current_group] = {
                "total_cost": 0,
                "total_size": 0,
                "files_count": 0,
                "buckets_count": 0,
                "buckets": [],
            }

        # Update the summary
        all_buckets_info[current_group]["total_cost"] += bucket_info["cost"]
        all_buckets_info[current_group]["total_size"] += bucket_info["total_size_bytes"]
        all_buckets_info[current_group]["files_count"] += bucket_info["nb_files"]
        all_buckets_info[current_group]["buckets_count"] += 1

        # Insert the bucket information
        all_buckets_info[current_group]["buckets"].append(bucket_info)

    return all_buckets_info
