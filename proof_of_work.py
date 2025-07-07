import hashlib
import json

def compute_hash(block):
    block_string = (
        f"{block.index}"
        f"{block.timestamp}"
        f"{json.dumps(block.transactions, sort_keys=True)}"
        f"{block.previous_hash}"
        f"{block.nonce}"
    )
    return hashlib.sha256(block_string.encode()).hexdigest()

def mine_block(block, difficulty, stop_flag):
    prefix = '0' * difficulty
    while not stop_flag.is_set():
        block.hash = compute_hash(block)
        if block.hash.startswith(prefix):
            return block
        block.nonce += 1
    return None
