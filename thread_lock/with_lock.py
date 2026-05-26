import threading

counter = 0
NUM_THREADS = 10
INCREMENTS_PER_THREAD = 100_000

lock = threading.Lock()

def increment():
    global counter
    for _ in range(INCREMENTS_PER_THREAD):
        with lock:
            counter += 1

threads = []

for _ in range(NUM_THREADS):
    t = threading.Thread(target=increment)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

expected = NUM_THREADS * INCREMENTS_PER_THREAD
print("Expected:", expected)
print("Actual:", counter)
