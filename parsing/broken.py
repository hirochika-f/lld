from collections import defaultdict
from collections.abc import Iterable
from typing import Any, Iterator
import csv


def extract(reader: Iterable[dict[str, str]]) -> dict[str, int]:
    sales = defaultdict(int)
    for row in reader:
        if row["status"] != "completed":
            print("invalid status")
            continue
        customer = row["customer"].strip()
        if not customer:
            print("invalid customer")
            continue
        try:
            price = int(row["price"])
        except ValueError:
            print(f"Invalid price format: {row['price']}")
            continue
        sales[customer] += price
    return dict(sales)


if __name__ == "__main__":
    with open("broken.csv", newline="") as f:
        reader = csv.DictReader(f)
        sales = extract(reader)
        print("ret: ", sales)
