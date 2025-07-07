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

        # In a real network, this would involve sending the block to other nodes.
        # Here, vote_fn simulates other nodes' validation.
        # Each 'vote' should represent a node's decision on the block's validity.
        # For this simulation, we'll have 'vote_fn' check each transaction's signature.
        
        # Collect votes from simulated nodes (here, just based on transaction validity)
        # A more complex system would involve actual network communication and votes from distinct nodes.
        valid_votes_count = 0
        for tx_dict in block.transactions:
            report = HealthReport.from_dict(tx_dict)
            if vote_fn(report): # vote_fn now verifies the report
                valid_votes_count += 1
            else:
                self.logger.warning(f"[Network] 🚨 Invalid report detected in block {block.hash[:10]}... from Doctor {report.doctor_id}. Vote against.")

        # Simple majority consensus: if more than half of the transactions are valid, the block is accepted.
        # In a real blockchain, this would be about nodes voting on the *entire block's* validity,
        # including PoW, previous hash, and all transactions.
        # Here, we're simplifying the 'voting' to transaction validity.
        if valid_votes_count >= len(block.transactions) / 2: # At least half of the reports must be valid
            self.blockchain.append(block)
            self.logger.info(f"[Network] ✅ Block {block.hash[:10]}... added to blockchain by majority (valid reports: {valid_votes_count}/{len(block.transactions)})")
            # Add all reports from the accepted block to the patient history tracker
            for report in block.transactions:
                history_tracker.add_report(report)
        else:
            self.logger.warning(f"[Network] ❌ Block {block.hash[:10]}... rejected due to insufficient valid reports ({valid_votes_count}/{len(block.transactions)}).")
        
        # Signal all miners to stop current mining round as a block has been processed
        stop_flag.set()

