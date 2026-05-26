import hashlib
import bisect

class ConsistentHash:
    def __init__(self, hash_space=2**256):
        self.hash_space = hash_space
        self._keys = []
        self.nodes = []

    def hash_fn(self, key):
        hsh = hashlib.sha256()
        hsh.update(key.encode("utf-8"))
        return int(hsh.hexdigest(), 16) % self.hash_space

    def add_node(self, node):
        if len(self._keys) >= self.hash_space:
            raise Exception("Hash space is full.")

        key = self.hash_fn(node.host)
        index = bisect.bisect_left(self._keys, key)
        if index < len(self._keys) and self._keys[index] == key:
            raise Exception("Hash collision.")

        # implement data transfer between the past node and the new node here

        self._keys.insert(index, key)
        self.nodes.insert(index, node)
        return key

    def remove_node(self, node):
        if len(self._keys) == 0:
            raise Exception("Hash space is empty.")

        key = self.hash_fn(node.host)
        index = bisect.bisect_left(self._keys, key)
        if index == len(self._keys) or self._keys[index] != key:
            raise Exception("Node is not existing.")

        # implement data transfer between the deleted node and the next node here

        self._keys.pop(index)
        self.nodes.pop(index)
        return key

    def assign(self, item):
        if len(self._keys) == 0:
            raise Exception("No nodes in hash space.")

        key = self.hash_fn(item)
        index = bisect.bisect_right(self._keys, key) % len(self._keys)
        return self.nodes[index]
