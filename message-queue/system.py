from collections import defaultdict
import heapq
import threading


class MessageQueue:
    def __init__(self):
        # self.messages = {topic: [message1, message2, ...]}
        self.messages = defaultdict(list)
        # self.offsets = {consumer: {topic: offset}}
        self.offsets = defaultdict(lambda: defaultdict(int))
        # self.subscribers = {topic: {consumer1, consumer2, ...}}
        self.subscribers = defaultdict(set)

    def subscribe(self, topic: str, consumer_id: str) -> bool:
        if consumer_id in self.subscribers[topic]:
            return False
        self.subscribers[topic].add(consumer_id)
        self.offsets[consumer_id][topic] = len(self.messages[topic])
        return True

    def publish(self, topic: str, message: str) -> int:
        self.messages[topic].append(message)
        return len(self.subscribers[topic])

    def poll(self, consumer_id: str, topic: str) -> str:
        if consumer_id not in self.offsets:
            raise ValueError(f"Consumer: {consumer_id} subscribes no topics.")
        if topic not in self.offsets[consumer_id]:
            raise ValueError(f"Not found topic: {topic}")
        offset = self.offsets[consumer_id][topic]
        if offset >= len(self.messages[topic]):
            return ""
        polled_message = self.messages[topic][offset]
        self.offsets[consumer_id][topic] += 1
        return polled_message


if __name__ == "__main__":
    mq = MessageQueue()
    mq.subscribe("orders", "consumer1")
    mq.subscribe("orders", "consumer2")

    message = "message"
    mq.publish("orders", message)
    assert message == mq.poll("consumer1", "orders")
    assert message == mq.poll("consumer2", "orders")
    assert "" == mq.poll("consumer1", "orders")
