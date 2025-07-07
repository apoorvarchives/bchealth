import threading
import time
import random
from miner_app import Miner
from blockchain.block import Block
from mempool.mempool import Mempool
from network.node import NodeNetwork
from reports.health_report import HealthReport
from utils.logger import setup_logger
from wallets.patient_wallet import PatientWallet
from wallets.doctor_wallet import DoctorWallet # Import DoctorWallet
from history.history_tracker import PatientHistoryTracker

NUM_MINERS = 5
DIFFICULTY = 3

logger = setup_logger("Main")

# This vote_fn now performs actual verification of the report's signature.
# In a real network, this would be a more complex function run by each node
# to validate the entire block and its transactions.
def vote_fn(report):
    """
    Simulates a node's vote on a health report (transaction).
    For this simulation, a report is considered "valid" if its signature is valid.
    """
    return report.verify_signature()

def generate_reports(mempool, patient_wallets, doctor_wallets):
    """
    Continuously generates random health reports, signs them with a random doctor's wallet,
    and adds them to the mempool.
    """
    while True:
        patient_wallet = random.choice(patient_wallets)
        doctor_wallet = random.choice(doctor_wallets)

        # Generate a health report and sign it using the doctor's wallet
        report = HealthReport.generate(patient_wallet.patient_id, doctor_wallet)
        mempool.add_report(report.to_dict()) # Add the signed report (as dict) to mempool

        time.sleep(random.uniform(1, 2))

def query_patient_history(history_tracker):
    """
    Allows a user to query and view a patient's health history from the tracker.
    """
    while True:
        user_input = input("🔍 Enter patient_id to view history (or 'exit'): ").strip()
        if user_input.lower() == 'exit':
            break
        history_tracker.print_history(user_input)

def run_simulation():
    """
    Initializes and runs the blockchain simulation.
    """
    blockchain = []
    mempool = Mempool()
    node = NodeNetwork(num_miners=NUM_MINERS)
    history_tracker = PatientHistoryTracker()

    # Initialize patient and doctor wallets
    patient_wallets = [PatientWallet(f"patient_{i}") for i in range(5)]
    doctor_wallets = [DoctorWallet(f"doctor_{i}") for i in range(3)] # New: Doctor Wallets

    # Create the genesis block
    genesis_block = Block(0, [], "0", DIFFICULTY)
    genesis_block.hash = genesis_block.compute_hash()
    blockchain.append(genesis_block)
    node.blockchain = blockchain # Node network needs access to the blockchain
    logger.info("Initialized blockchain with genesis block.")

    # Start the health report generation thread
    tx_thread = threading.Thread(target=generate_reports, args=(mempool, patient_wallets, doctor_wallets))
    tx_thread.daemon = True
    tx_thread.start()
    logger.info("Health report generator started.")

    # Start the patient history query thread
    query_thread = threading.Thread(target=query_patient_history, args=(history_tracker,))
    query_thread.daemon = True
    query_thread.start()

    # Main simulation loop for mining
    while True:
        stop_flag = threading.Event() # Event to signal miners to stop after a block is found
        miners = []
        ids = list(range(NUM_MINERS))
        random.shuffle(ids) # Randomize miner order for fairness

        # Start all miners for the current round
        for i in ids:
            miner = Miner(
                miner_id=i,
                blockchain=node.blockchain, # Pass the shared blockchain reference
                mempool=mempool,           # Pass the shared mempool reference
                difficulty=DIFFICULTY,
                stop_flag=stop_flag,       # Pass the shared stop flag
                broadcast_fn=lambda b: node.broadcast_block(b, stop_flag, vote_fn, history_tracker)
            )
            miners.append(miner)
            miner.start()
            logger.info(f"Started Miner {i}")
            time.sleep(random.uniform(0.001, 0.01)) # Stagger miner start times slightly

        # Wait for all miners to complete their current mining attempt
        for miner in miners:
            miner.join()

        time.sleep(1) # Short pause before starting the next mining round
        logger.info("Starting next mining round...\n")

if __name__ == "__main__":
    run_simulation()

