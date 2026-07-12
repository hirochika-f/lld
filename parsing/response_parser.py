from collections import defaultdict
from typing import Any
import json


def extract_completed_prices(response: dict[str, Any]) -> dict[str, int]:
    d = defaultdict(int)
    users = response.get("users", [])
    for user in users:
        user_id = user["id"]
        orders = user.get("orders", [])
        for order in orders:
            if order["status"] != "completed":
                continue
            if not isinstance(order["price"], int):
                print("Invalid price format")
                continue
            d[user_id] += order["price"]
    return dict(d)


if __name__ == "__main__":
    with open("input.json", "r") as f:
        response = json.load(f)
        ret = extract_completed_prices(response)
        print(ret)
