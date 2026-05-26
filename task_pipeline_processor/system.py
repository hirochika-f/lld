import json
from textwrap import dedent

def process_task(results: str):
    results: list[dict] = json.loads(dedent(results))
    ret = {}
    for result in results:
        ret[result["id"]] = result
    return sorted(ret.values(), key=lambda x: x["id"])


if __name__ == "__main__":
    raw = '''
        [
            {"id": 1, "name": "build", "status": "ok", "parentId": 0},
            {"id": 2, "name": "test", "status": "ok", "parentId": 0},
            {"id": 2, "name": "test", "status": "error", "parentId": 0}
        ]
    '''
    print(process_task(raw))

