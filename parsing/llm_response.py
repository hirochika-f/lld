from typing import Any
import json

def extract(response: dict[str, Any]) -> list[dict[str, Any]]:
    ret = []
    if not response["choices"]:
        return ret
    choices = response["choices"]
    for choice in choices:
        tool_calls = choice["message"].get("tool_calls", [])
        for tool_call in tool_calls:
            call = {}
            function = tool_call["function"]
            customer_id_str = function["arguments"]
            try:
                customer_id_dict = json.loads(customer_id_str)
            except JSONDecodeError:
                raise ValueError("Invalid format in customer_id")
            if not isinstance(customer_id_dict, dict):
                raise ValueError("Invalid arguments")
            customer_id = customer_id_dict.get("customerId")
            if customer_id is None:
                raise ValueError("Not found customer id key")
            if type(customer_id) is not int:
                raise ValueError("Invalid customer id type")
            call = {
                "tool": function["name"],
                "customerId": customer_id
            }
            ret.append(call)
    return ret


if __name__ == "__main__":
    response = {
        "choices":[
            {
                "message":{
                    "tool_calls":[
                        {
                            "function":{
                                "name":"search_customer",
                                "arguments":"{\"customerId\":123}"
                            }
                        }
                    ]
                }
            }
        ]
    }
    result = extract(response)
    print(result)

