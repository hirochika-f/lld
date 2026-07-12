from collections import defaultdict
from typing import Any

def count_user_open_tickets(
    customers: list[dict[str, Any]],
    tickets: list[dict[str, Any]]) -> dict[str, int]:
    customer_id_map = {}
    # {customer_id: name}
    for customer in customers:
        customer_id_map[customer["id"]] = customer["name"]

    ticket_counts = defaultdict(int)
    # {customer_id: open_ticket_count}
    for ticket in tickets:
        customer_id = ticket["customerId"]
        if ticket["status"] == "open":
            ticket_counts[customer_id] += 1

    ret = {}
    for customer_id, count in ticket_counts.items():
        if customer_id not in customer_id_map:
            print(f"Not found customer id in customers table: {customer_id}")
            continue
        ret[customer_id_map[customer_id]] = count
    return ret

if __name__ == "__main__":
    customers = [
        {"id":1,"name":"Alice"},
        {"id":2,"name":"Bob"},
        {"id":3,"name":"Charlie"}
    ]
    tickets = [
        {"customerId":2,"status":"open"},
        {"customerId":8,"status":"open"},
        {"customerId":2,"status":"open"},
        {"customerId":3,"status":"closed"}
    ]
    ret = count_user_open_tickets(customers, tickets)
    # output = {"name": ticket_count}
    print(ret)
