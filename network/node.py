# network/node.py
import threading
from collections import defaultdict
from reports.health_report import HealthReport # Import HealthReport
from utils.logger import setup_logger # Import setup_logger

class NodeNetwork:
    """
    Simulates the blockchain network, handling block broadcasting and
    consensus for adding new blocks to the blockchain.
    """
    def __init__(self, num_miners):
        self.miners = [f"miner_{i}" for i in range(num_miners)]
        self.blockchain = []
        self.logger = setup_logger("NodeNetwork") # Add a logger for the network

    def broadcast_block(self, block, stop_flag, vote_fn, history_tracker):
        """
        Broadcasts a newly mined block to the network.
        Other nodes (simulated by vote_fn) validate the block.
        If accepted by majority, the block is added to the blockchain.
        """
        self.logger.info(f"[Network] Broadcasting block {block.hash[:10]}...")

        valid_votes_count = 0
        for tx_dict in block.transactions:
            report = HealthReport.from_dict(tx_dict)
            if vote_fn(report): # vote_fn now verifies the report
                valid_votes_count += 1
            else:
                self.logger.warning(f"[Network] 🚨 Invalid report detected in block {block.hash[:10]}... from Doctor {report.doctor_id}. Vote against.")

        if valid_votes_count >= len(block.transactions) / 2: # At least half of the reports must be valid
            self.blockchain.append(block)
            self.logger.info(f"[Network] ✅ Block {block.hash[:10]}... added to blockchain by majority (valid reports: {valid_votes_count}/{len(block.transactions)})")
            # Add all reports from the accepted block to the patient history tracker,
            # passing the block's hash.
            for report_dict in block.transactions: # Iterate over the dictionaries stored in the block
                history_tracker.add_report(report_dict, block.hash) # Pass the block.hash
        else:
            self.logger.warning(f"[Network] ❌ Block {block.hash[:10]}... rejected due to insufficient valid reports ({valid_votes_count}/{len(block.transactions)}).")
        
        # Signal all miners to stop current mining round as a block has been processed
        stop_flag.set()

