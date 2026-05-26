import threading

class LogWriter:
    def __init__(self):
        self._lock = threading.Lock()
        self.logs = []

    def write(self, message) -> None:
        with self._lock:
            self.logs.append(message)

    def get_logs(self) -> list[str]:
        with self._lock:
            return self.logs.copy()


if __name__ == "__main__":
    logwriter = LogWriter()
    NUM_THREADS = 10
    threads = []
    for i in range(NUM_THREADS):
        msg = f"msg{i}"
        t = threading.Thread(target=logwriter.write, args=(msg,))
        threads.append(t)
        t.start()
    # wait until all threads finished
    for t in threads:
        t.join()
    print(logwriter.get_logs())

