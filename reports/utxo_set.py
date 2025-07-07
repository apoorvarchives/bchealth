#utxo_set.py
from Signatures import serialize_public_key
from collections import defaultdict
import threading

class UTXOSet:
    def __init__(self):
        self.utxos = defaultdict(float)  # {public_key_str: balance}
        self.lock = threading.Lock()

    def add_utxo(self, public_key, amount):
        key = serialize_public_key(public_key).decode()
        with self.lock:
            self.utxos[key] += amount

    def spend_utxo(self, public_key, amount):
        key = serialize_public_key(public_key).decode()
        with self.lock:
            if self.utxos[key] >= amount:
                self.utxos[key] -= amount
                return True
            return False

    def get_balance(self, public_key):
        key = serialize_public_key(public_key).decode()
        with self.lock:
            return self.utxos.get(key, 0.0)

    def is_valid_transaction(self, tx):
        key = tx.sender_pub
        with self.lock:
            if self.utxos[key] >= tx.amount:
                return True
            return False

    def apply_transaction(self, tx):
        with self.lock:
            if self.utxos[tx.sender_pub] >= tx.amount:
                self.utxos[tx.sender_pub] -= tx.amount
                self.utxos[tx.recipient_pub] += tx.amount
                return True
            return False

    def snapshot(self):
        with self.lock:
            return dict(self.utxos)
