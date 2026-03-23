import threading
import queue
import uuid

class Message:
    def __init__(self, message: str):
        self.message = message
        self.uuid = uuid.uuid4()
    def get_payload(self):
        return self.message
    def __str__(self):
        return f"Message is: {self.message}"

class Subscriber:
    def __init__(self, name: str):
        self.name = name
        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self._consume)
        self.worker.start()

    def enqueue(self, message: Message):
        self.queue.put(message)

    def _consume(self):
        while True:
            message = self.queue.get()
            if message is None:
                break
            self.on_message(message)

    def on_message(self, message: Message):
        pass

    def shutdown(self):
        self.queue.put(None)
        self.worker.join()

class NewsSubscriber(Subscriber):
    def on_message(self, message: Message):
        print(f"BREAKING NEWS: {message.get_payload()}")

class SlowSubscriber(Subscriber):
    def on_message(self, message: Message):
        print(f"........ NEWS: {message.get_payload()}")

class Topic:
    _lock = threading.Lock()

    def __init__(self, name: str):
        self.name = name
        self.subscribers = set()

    def add_subscriber(self, subscriber: Subscriber):
        self.subscribers.add(subscriber)

    def delete_subscriber(self, subscriber: Subscriber):
        self.subscribers.discard(subscriber)

    def publish(self, message: Message):
        with self._lock:
            subscribers = list(self.subscribers)
        for subscriber in subscribers:
            subscriber.enqueue(message)

class System:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.topics = {}
        self._initialized = True

    def create_topic(self, name: str):
        self.topics[name] = Topic(name)

    def subscribe_topic(self, topic_name: str, subscriber: Subscriber):
        topic = self.topics.get(topic_name)
        if topic is None:
            raise ValueError(f"Not found topic: {topic_name}")
        topic.add_subscriber(subscriber)

    def unsubscribe_topic(self, topic_name: str, subscriber: Subscriber):
        topic = self.topics.get(topic_name)
        if topic is None:
            raise ValueError(f"Not found topic: {topic_name}")
        topic.delete_subscriber(subscriber)

    def publish(self, message: str, topic_name: str):
        topic = self.topics.get(topic_name)
        if topic is None:
            raise ValueError(f"Not found topic: {topic_name}")
        topic.publish(Message(message))

    def shutdown(self):
        for topic in self.topics.values():
            for subscriber in topic.subscribers:
                subscriber.shutdown()




if __name__ == "__main__":
    system = System()
    SPORTS = "SPORTS"
    STOCK = "STOCK"
    system.create_topic(SPORTS)
    system.create_topic(STOCK)

    baseball_news = NewsSubscriber("baseball_news")
    sports_news = SlowSubscriber("sports_news")
    stock_news = NewsSubscriber("stock_market")
    economics_news = SlowSubscriber("economics_news")
    sbi_crawler = SlowSubscriber("sbi")

    system.subscribe_topic(SPORTS, baseball_news)
    system.subscribe_topic(SPORTS, sports_news)
    system.publish("Japan wins at WBC.", SPORTS)
    system.unsubscribe_topic(SPORTS, sports_news)
    system.publish("USA wins at WBC.", SPORTS)
    system.publish("NVIDIA touched highest value yesterday.", STOCK)
    system.subscribe_topic(STOCK, stock_news)
    system.publish("$NVDA touched highest value yesterday.", STOCK)
    system.subscribe_topic(STOCK, economics_news)
    system.subscribe_topic(STOCK, sbi_crawler)
    system.publish("$AAPL touched highest value yesterday.", STOCK)
    print("--- 7 messages ---")
    system.shutdown()
