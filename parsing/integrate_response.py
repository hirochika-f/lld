from collections import defaultdict
from typing import Any


def extract_sales_and_ticket_counts(
    customers: list[dict[str, Any]],
    tickets: list[dict[str, Any]],
    orders: list[dict[str, Any]]) -> list[dict[str, Any]]:

    customer_id_map = {}
    # {customer_id: name}
    for customer in customers:
        customer_id_map[customer["id"]] = customer["name"]

    customer_open_high_counts = defaultdict(int)
    # {customer_id: open_high_ticket_count}
    for ticket in tickets:
        if ticket["priority"] == "high" and ticket["status"] == "open":
            customer_open_high_counts[ticket["customerId"]] += 1

    customer_total_sales = defaultdict(int)
    # {customer_id: total_amount}
    for order in orders:
        customer_total_sales[order["customerId"]] += order["amount"]

    names_sales_ticket_counts = []
    for customer_id, customer_name in customer_id_map.items():
        name_sales_ticket_count = {
            "name": customer_name,
            "sales": customer_total_sales[customer_id],
            "openHighPriorityTickets": customer_open_high_counts[customer_id]
        }
        names_sales_ticket_counts.append(name_sales_ticket_count)
    return names_sales_ticket_counts


if __name__ == "__main__":
    customers = [
        {"id":1,"name":"Alice"},
        {"id":2,"name":"Bob"}
    ]
    tickets = [
        {"customerId":1,"priority":"high","status":"open"},
        {"customerId":1,"priority":"low","status":"closed"},
        {"customerId":2,"priority":"high","status":"open"},
        {"customerId":2,"priority":"high","status":"open"}
    ]
    orders = [
        {"customerId":1,"amount":100},
        {"customerId":1,"amount":200},
        {"customerId":2,"amount":500}
    ]
    expected = [
        {
            "name":"Alice",
            "sales":300,
            "openHighPriorityTickets":1
        },
        {
            "name":"Bob",
            "sales":500,
            "openHighPriorityTickets":2
        }
    ]
    actual = extract_sales_and_ticket_counts(customers, tickets, orders)
    assert(expected == actual)
