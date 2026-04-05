import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

class Message:
    def __init__(self, message):
        self.id = uuid.uuid4()
        self.message = message

    def get_str(self):
        return self.message

class Subscriber:
    def __init__(self, name):
        self.name = name

    def on_message(self, message: Message):
        pass

    def get_name(self):
        return self.name


class NewsSubscriber(Subscriber):
    def on_message(self, message: Message):
        print(f"BREAKING NEWS: {message.get_str()}")


class SlowSubscriber(Subscriber):
    def on_message(self, message: Message):
        print(f"... FETCHING NEWS: {message.get_str()}")


class Topic:
    def __init__(self, name: str, delivery_executor: ThreadPoolExecutor):
        self.name = name
        self.delivery_executor = delivery_executor
        self.subscribers = set()

    def add_subscriber(self, subscriber: Subscriber):
        self.subscribers.add(subscriber)

    def remove_subscriber(self, subscriber: Subscriber):
        self.subscribers.discard(subscriber)

    def broadcast(self, message: Message):
        for subscriber in self.subscribers:
            self.delivery_executor.submit(self._deliver_message, subscriber, message)

    def _deliver_message(self, subscriber: Subscriber, message: Message):
        try:
            subscriber.on_message(message)
        except:
            print(f"Error to deliver message to {subscriber.get_name()}")


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
        self.delivery_executor = ThreadPoolExecutor()
        self._initialized = True

    def create_topic(self, name: str):
        if name not in self.topics:
            self.topics[name] = Topic(name, self.delivery_executor)

    def subscribe_topic(self, topic_name, subscriber: Subscriber):
        topic = self.topics.get(topic_name)
        if topic is None:
            raise ValueError(f"Topic not found: {topic}")
        topic.add_subscriber(subscriber)

    def unsubscribe_topic(self, topic_name, subscriber: Subscriber):
        topic = self.topics.get(topic_name)
        if topic is None:
            raise ValueError(f"Topic not found: {topic}")
        topic.remove_subscriber(subscriber)

    def publish(self, message: str, topic_name: str):
        msg = Message(message)
        topic = self.topics.get(topic_name)
        if topic is None:
            raise ValueError(f"Topic not found: {topic}")
        topic.broadcast(msg)

    def shutdown(self):
        self.delivery_executor.shutdown(wait=True)


if __name__ == "__main__":
    system = System()
    SPORTS_TOPIC = "SPORTS"
    STOCK_TOPIC = "STOCK"
    system.create_topic(SPORTS_TOPIC)
    system.create_topic(STOCK_TOPIC)

    baseball_news = NewsSubscriber("baseball_news")
    sports_news = SlowSubscriber("sports_news")
    stock_news = NewsSubscriber("stock_market")
    economics_news = SlowSubscriber("economics_news")
    sbi_crawler = SlowSubscriber("sbi")

    system.subscribe_topic(SPORTS_TOPIC, baseball_news)
    system.subscribe_topic(SPORTS_TOPIC, sports_news)
    system.publish(SPORTS_TOPIC, "Japan won at WBC.")
    system.unsubscribe_topic(SPORTS_TOPIC, sports_news)
    system.publish(SPORTS_TOPIC, "USA won at WBC.")
    system.publish(STOCK_TOPIC, "NVIDIA touched highest value yesterday.")
    system.subscribe_topic(STOCK_TOPIC, stock_news)
    system.publish(STOCK_TOPIC, "$NVDA touched highest value yesterday.")
    system.subscribe_topic(STOCK_TOPIC, economics_news)
    system.subscribe_topic(STOCK_TOPIC, sbi_crawler)
    system.publish(STOCK_TOPIC, "$AAPL touched highest value yesterday.")
