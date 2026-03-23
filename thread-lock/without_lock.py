import threading
import time

counter = 0
NUM_THREADS = 10
INCREMENTS_PER_THREAD = 100_000

def increment():
    global counter
    for _ in range(INCREMENTS_PER_THREAD):
        temp = counter
        time.sleep(0.000001)
        temp += 1
        counter = temp

threads = []

for _ in range(NUM_THREADS):
    t = threading.Thread(target=increment)
    threads.append(t)
    t.start()

for t in threads:
    pass
expected = NUM_THREADS * INCREMENTS_PER_THREAD
print("Expected:", expected)
print("Actual:", counter)
