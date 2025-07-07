# mempool/mempool.py
import threading

class Mempool:
    def __init__(self):
        self.reports = []
        self.lock = threading.Lock()

    def add_report(self, report):
        with self.lock:
            self.reports.append(report)

    def get_transactions(self, count):
        with self.lock:
            selected = self.reports[:count]
            self.reports = self.reports[count:]
            return selected

    def size(self):
        with self.lock:
            return len(self.reports)
