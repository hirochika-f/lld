import json
from textwrap import dedent

class Task:
    def __init__(self, task):
        self.id = task["id"]
        self.name = task["name"]
        self.status = task["status"]
        self.parent_id = task["parentId"]
        self.children = []

    def get_parameters(self, visited=None, gen=0):
        if visited is None:
            visited = set()
        if self.id in visited:
            return

        indent = ' ' * (gen * 2)
        print(f"{indent}id: {self.id}, name: {self.name}, status: {self.status}, parentId: {self.parent_id}")
        new_visited = visited | {self.id}
        for child in self.children:
            child.get_parameters(new_visited, gen + 1)


def process_task(results: str):
    tasks: list[dict] = json.loads(dedent(results))
    dedup = {}
    for t in tasks:
        dedup[t["id"]] = t

    d = {}
    for t in dedup.values():
        d[t["id"]] = Task(t)


    roots = []
    for t in d.values():
        if t.parent_id == 0:
            roots.append(t)
        else:
            parent = d.get(t.parent_id)
            if parent:
                parent.children.append(t)
            else:
                roots.append(t)
    return roots


if __name__ == "__main__":
    raw = '''
        [
            {"id": 1, "name": "build", "status": "ok", "parentId": 0},
            {"id": 2, "name": "test", "status": "ok", "parentId": 3},
            {"id": 2, "name": "test", "status": "error", "parentId": 3},
            {"id": 3, "name": "test", "status": "error", "parentId": 1},
            {"id": 3, "name": "test", "status": "warning", "parentId": 1}
        ]
    '''
    ret = process_task(raw)
    for task in ret:
        task.get_parameters()

