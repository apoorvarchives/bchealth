import threading
import time
import random
from blockchain.block import Block
from proof_of_work import mine_block
from utils.logger import setup_logger
from reports.health_report import HealthReport # Import HealthReport

class Miner(threading.Thread):
    """
    Represents a miner in the blockchain network.
    Miners now pick up any available health reports from the mempool
    and attempt to mine them through Proof of Work.
    """
    def __init__(self, miner_id, blockchain, mempool, difficulty, stop_flag, broadcast_fn,
                 max_reports_per_block=10): # Removed associated_patient_id
        super().__init__()
        self.miner_id = miner_id
        self.blockchain = blockchain
        self.mempool = mempool
        self.difficulty = difficulty
        self.stop_flag = stop_flag
        self.broadcast_fn = broadcast_fn
        self.max_reports_per_block = max_reports_per_block
        self.logger = setup_logger(f"Miner {self.miner_id}")
        self.daemon = True

    def run(self):
        """
        The main mining loop. Continuously tries to mine new blocks.
        Now picks up any reports from the mempool.
        """
        while True:
            # Check if another miner has already found a block
            if self.stop_flag.is_set():
                self.logger.info("❌ Stopped: Another miner already mined the block.")
                break

            # Get transactions (health reports) from the mempool
            # Miners now simply try to get max_reports_per_block transactions
            potential_reports = self.mempool.get_transactions(self.max_reports_per_block)
            
            # If not enough reports, wait and try again
            if len(potential_reports) < self.max_reports_per_block:
                # Put back the reports if not enough to form a block
                for r in potential_reports:
                    self.mempool.add_report(r)
                time.sleep(0.5)
                continue

            valid_reports = []
            reports_for_next_round = [] # Reports that are valid but exceed max_reports_per_block

            for report_dict in potential_reports: # Iterate over all potential reports
                # Reconstruct HealthReport object to use its verification method
                report = HealthReport.from_dict(report_dict) # This reconstructs with bytes signature internally
                if report.verify_signature():
                    # IMPORTANT FIX: Append the dictionary representation from the *reconstructed*
                    # HealthReport object, which will ensure the signature is Base64 encoded.
                    valid_reports.append(report.to_dict()) 
                else:
                    self.logger.warning(f"🚨 Invalid signature for report from Doctor {report.doctor_id}. Skipping.")
            
            # Put back valid reports that couldn't fit into this block
            # This logic is simplified as we're not filtering by patient anymore
            for r in reports_for_next_round:
                self.mempool.add_report(r)

            # If no valid reports were found from the fetched batch, wait and try again
            if len(valid_reports) == 0:
                time.sleep(0.5)
                continue

            last_block = self.blockchain[-1]

            # Create a new block with the valid reports
            new_block = Block(
                index=last_block.index + 1,
                transactions=valid_reports, # This list now contains dicts with Base64 signatures
                previous_hash=last_block.hash,
                difficulty=self.difficulty
            )

            self.logger.info(f"⛏️ Miner {self.miner_id} mining started...") # Removed patient ID from log
            # Attempt to mine the block using Proof of Work
            mined_block = mine_block(new_block, self.difficulty, self.stop_flag)

            if mined_block:
                self.logger.info(f"✅ Block #{mined_block.index} mined by Miner {self.miner_id}") # Removed patient ID from log
                # Print the full details of the mined block using its __str__ method
                print(mined_block) # This line will print all the requested block and transaction details
                self.logger.info(f"🧾 Health Report Count: {len(mined_block.transactions)}")
                # Broadcast the successfully mined block to the network
                self.broadcast_fn(mined_block)
                break # Stop mining for this round as a block has been found

