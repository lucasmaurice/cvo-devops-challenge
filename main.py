import typer
from typing_extensions import Annotated
from typing import Optional

from tabulate import tabulate

from s3_lister import get_bucket, list_buckets, available_grouping


UNITS = ["auto", "B", "KiB", "MiB", "GiB", "TiB"]
selected_unit = "auto"


# Callback to set the unit to use for the data display
def set_unit(value):
    if value not in UNITS:
        raise ValueError(f"Invalid unit selected '{value}'. Must be one of {UNITS}")

    global selected_unit
    selected_unit = value


def beautify_size(size):
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if (selected_unit == unit) or (size < 1024.0 and selected_unit == "auto"):
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"


def beautify_cost(cost):
    return f"${cost:.2f}"


def print_bucket_table(bucket_information):
    # Beautify the data
    for bucket in bucket_information:
        bucket["total_size"] = beautify_size(bucket["total_size"])
        bucket["cost"] = beautify_cost(bucket['cost'])

    table = tabulate(bucket_information, headers="keys")
    print("-"*len(table.split("\n")[1]))
    print(table)
    print("-"*len(table.split("\n")[1]))


def main(
    bucket: Annotated[str, typer.Option(help="The bucket name to filter. Should be the entire bucket name.")] = "",
    group_by: Annotated[str, typer.Option(help="The grouping you want to use for display the buckets.", callback=available_grouping)] = "",
    data_unit: Annotated[str, typer.Option(help="The unit to use for the data. {UNITS}", callback=set_unit)] = "auto",
):
    if bucket:
        if bucket_information := get_bucket(bucket):
            print_bucket_table([bucket_information])
        return

    buckets_data = list_buckets(group_by)

    if group_by:
        print(f"Grouping by {group_by}")

    for group, data in buckets_data.items():
        if group_by:
            print(f"Data for {group_by} {group}:")
        print_bucket_table(data["buckets"])
        print(f"Summary:\tBuckets: {data['buckets_count']}, Files: {data['files_count']}, Size: {beautify_size(data['total_size'])}, Cost: {beautify_cost(data['total_cost'])}")
        print("\n")


if __name__ == "__main__":
    typer.run(main)
