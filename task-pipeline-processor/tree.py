import json
from textwrap import dedent

class Task:
    def __init__(self, task):
        self.id = task["id"]
        self.name = task["name"]
        self.status = task["status"]
        self.parentId = task["parentId"]
        self.children = {}

    def get_parameters(self):
        print(f"id: {self.id}, name: {self.name}, status: {self.status}, parentId: {self.parentId}")
        if self.children:
            for child in self.children.values():
                print('  - ', end="")
                child.get_parameters()
            


def process_task(results: str):
    results: list[dict] = json.loads(dedent(results))
    ret = {}
    for result in results:
        ret[result["id"]] = Task(result)
        if result["parentId"] != 0:
            ret[result["parentId"]].children[result["id"]] = ret[result["id"]]
    return sorted(ret.values(), key=lambda x: x.id)


if __name__ == "__main__":
    raw = '''
        [
            {"id": 1, "name": "build", "status": "ok", "parentId": 0},
            {"id": 2, "name": "test", "status": "ok", "parentId": 0},
            {"id": 2, "name": "test", "status": "error", "parentId": 0},
            {"id": 3, "name": "test", "status": "error", "parentId": 1},
            {"id": 3, "name": "test", "status": "warning", "parentId": 1}
        ]
    '''
    ret = process_task(raw)
    for task in ret:
        task.get_parameters()

