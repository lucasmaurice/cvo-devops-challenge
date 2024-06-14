import typer
from typing_extensions import Annotated
from typing import Optional

from tabulate import tabulate

from s3_lister import get_bucket, list_buckets, available_grouping


def print_as_table(bucket_information):
    print(tabulate(bucket_information, headers="keys"))


def main(
    bucket: Annotated[str, typer.Option(help="The bucket name to filter. Should be the entire bucket name.")] = "",
    group_by: Annotated[Optional[str], typer.Option(help="this option does this and that", callback=available_grouping)] = "",
):
    if bucket:
        if bucket_information := get_bucket(bucket):
            print_as_table([bucket_information])
        return

    buckets_data = list_buckets(group_by)

    if group_by:
        print(f"Grouping by {group_by}")

    for group, data in buckets_data.items():
        if group_by:
            print(f"Data for {group_by} {group}:\n-----------")
        print_as_table(data["buckets"])
        print("-----------")
        print(f"Summary:\tBuckets: {data['buckets_count']}, Files: {data['files_count']}, Cost: {data['total_cost']}, Data: {data['total_size']} bytes")
        print("\n")


if __name__ == "__main__":
    typer.run(main)
