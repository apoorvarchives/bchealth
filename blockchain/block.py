import time
import hashlib
import json
from reports.health_report import HealthReport # Import HealthReport to use its from_dict method

class Block:
    def __init__(self, index, transactions, previous_hash, difficulty):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions  # list of health reports (dicts)
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.merkle_root = self.compute_merkle_root()
        self.hash = self.compute_hash()

    def compute_merkle_root(self):
        tx_hashes = [hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() for tx in self.transactions]
        if not tx_hashes:
            return ''
        while len(tx_hashes) > 1:
            temp = []
            for i in range(0, len(tx_hashes), 2):
                left = tx_hashes[i]
                right = tx_hashes[i+1] if i + 1 < len(tx_hashes) else left
                combined = left + right
                temp.append(hashlib.sha256(combined.encode()).hexdigest())
            tx_hashes = temp
        return tx_hashes[0]

    def compute_hash(self):
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'merkle_root': self.merkle_root,
            'hash': self.hash
        }

    def __str__(self):
        transactions_str = ""
        if self.transactions:
            for i, tx_dict in enumerate(self.transactions, 1):
                # Reconstruct HealthReport object to easily access its attributes
                report = HealthReport.from_dict(tx_dict)
                vitals_str = ", ".join(f"{k}: {v}" for k, v in report.vitals.items())
                
                follow_up_date_str = time.ctime(report.follow_up_date) if report.follow_up_date else 'N/A'

                transactions_str += (
                    f"\n    📄 Report #{i} (Doctor: {report.doctor_id}, Patient: {report.patient_id})\n"
                    f"      Timestamp   : {time.ctime(report.timestamp)}\n"
                    f"      Hospital    : {report.hospital_clinic}\n" # New detail
                    f"      Age         : {report.patient_age}\n"     # New detail
                    f"      Gender      : {report.patient_gender}\n"   # New detail
                    f"      Symptoms    : {report.symptoms}\n"
                    f"      Diagnosis   : {report.diagnosis}\n"
                    f"      Vitals      : {vitals_str}\n"
                    f"      Medications : {report.medications}\n"
                    f"      Allergies   : {report.allergies}\n"
                    f"      Follow-up   : {follow_up_date_str}\n"
                    f"      Notes       : {report.notes}\n"
                    f"      Signed by   : {report.doctor_public_key_serialized[:10]}...\n"
                    f"      Signature Valid: {report.verify_signature()}\n" # Display signature validity
                )
        else:
            transactions_str = "\n    (No transactions in this block)"

        return (
            f"\n📦 Block #{self.index}\n"
            f"  Timestamp   : {time.ctime(self.timestamp)}\n"
            f"  Nonce       : {self.nonce}\n"
            f"  Difficulty  : {self.difficulty}\n"
            f"  Merkle Root : {self.merkle_root}\n"
            f"  Prev Hash   : {self.previous_hash}\n"
            f"  Curr Hash   : {self.hash}\n"
            f"  Transactions: {len(self.transactions)}{transactions_str}"
        )

