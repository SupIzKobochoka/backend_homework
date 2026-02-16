import time
import logging

def get_timestamp():
    return time.time()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)