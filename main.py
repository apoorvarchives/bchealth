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
from wallets.doctor_wallet import DoctorWallet
from history.history_tracker import PatientHistoryTracker

NUM_MINERS = 5
NUM_PATIENTS = 10
DIFFICULTY = 3
logger = setup_logger("Main")

def vote_fn(report):
    return report.verify_signature()

def generate_reports(mempool, patient_wallets, doctor_wallets):
    while True:
        patient_wallet = random.choice(patient_wallets)
        doctor_wallet = random.choice(doctor_wallets)

        report = HealthReport.generate(patient_wallet.patient_id, doctor_wallet)
        mempool.add_report(report.to_dict())

        time.sleep(random.uniform(1, 2))

def query_patient_history(history_tracker):
    while True:
        user_input = input("🔍 Enter patient_id to view history (or 'exit'): ").strip()
        if user_input.lower() == 'exit':
            break
        history_tracker.print_history(user_input)

def run_simulation():
    blockchain = []
    mempool = Mempool()
    node = NodeNetwork(num_miners=NUM_MINERS)
    history_tracker = PatientHistoryTracker()

    patient_wallets = [PatientWallet(f"patient_{i}") for i in range(NUM_PATIENTS)]
    doctor_wallets = [DoctorWallet(f"doctor_{i}") for i in range(3)]

    genesis_block = Block(0, [], "0", DIFFICULTY)
    genesis_block.hash = genesis_block.compute_hash()
    blockchain.append(genesis_block)
    node.blockchain = blockchain
    logger.info("Initialized blockchain with genesis block.")

    tx_thread = threading.Thread(target=generate_reports, args=(mempool, patient_wallets, doctor_wallets))
    tx_thread.daemon = True
    tx_thread.start()
    logger.info("Health report generator started.")

    query_thread = threading.Thread(target=query_patient_history, args=(history_tracker,))
    query_thread.daemon = True
    query_thread.start()

    while True:
        stop_flag = threading.Event()
        miners = []
        ids = list(range(NUM_MINERS))
        random.shuffle(ids)

        # Removed patient assignment logic for miners
        # Miners will now pick up any transactions from the mempool

        for i in ids:
            miner = Miner(
                miner_id=i,
                blockchain=node.blockchain,
                mempool=mempool,
                difficulty=DIFFICULTY,
                stop_flag=stop_flag,
                broadcast_fn=lambda b: node.broadcast_block(b, stop_flag, vote_fn, history_tracker)
                # Removed associated_patient_id parameter
            )
            miners.append(miner)
            miner.start()
            logger.info(f"Started Miner {i}") # Re-added this log as patient assignment log is removed
            time.sleep(random.uniform(0.001, 0.01))

        for miner in miners:
            miner.join()

        time.sleep(1)
        logger.info("Starting next mining round...\n")

if __name__ == "__main__":
    run_simulation()

