class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None
        self.prev = None

class LRUCache:
    def __init__(self, capacity):
        self.d = {}
        self.capacity = capacity
        self.left = Node(None, None)
        self.right = Node(None, None)
        self.right.prev = self.left
        self.left.next = self.right

    def _add_to_tail(self, node):
        prev = self.right.prev
        prev.next = node
        node.next = self.right
        self.right.prev = node
        node.prev = prev

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.next = None
        node.prev = None

    def put(self, key, value):
        if self.capacity == 0:
            return
        if key in self.d:
            node = self.d[key]
            node.value = value
            self._remove(node)
        else:
            node = Node(key, value)
            self.d[key] = node
        self._add_to_tail(node)
        if len(self.d) > self.capacity:
            lru = self.left.next
            self._remove(lru)
            del self.d[lru.key]

    def get(self, key):
        if key in self.d:
            node = self.d[key]
            self._remove(node)
            self._add_to_tail(node)
            return node.value
        else:
            return -1
        

if __name__ == "__main__":
    commands = ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
    args = [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]

    results = []
    obj = None

    for cmd, arg in zip(commands, args):
        if cmd == "LRUCache":
            obj = LRUCache(*arg)
            results.append(None)
        elif cmd == "put":
            obj.put(*arg)
            results.append(None)
        elif cmd == "get":
            res = obj.get(*arg)
            results.append(res)

    print(results)
