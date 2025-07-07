import logging
import sys

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(handler)
    logger.propagate = False
    return logger