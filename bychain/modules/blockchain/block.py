import copy
import json
from hashlib import sha256
from datetime import datetime
from typing import List, Dict


class Block(object):

    @staticmethod
    def to_json(block: 'Block'):
        result = None
        if block is not None:
            result = block.__json()
            result['hash'] = block.hash

        return result

    def __init__(self, index: int, transactions: List[Dict], previous_hash: str, timestamp: float = None,
                 nonce: int = 0):
        self.__index = index
        self.__transactions = copy.deepcopy(transactions)
        self.__timestamp = timestamp or datetime.utcnow().timestamp()
        self.__previous_hash = previous_hash
        self.nonce = nonce

    def __json(self):
        return dict(index=self.__index, transactions=self.__transactions, timestamp=self.__timestamp,
                    previous_hash=self.__previous_hash, nonce=self.nonce)

    @property
    def hash(self):
        block_string = json.dumps(self.__json(), sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    @property
    def index(self):
        return self.__index

    @property
    def transactions(self):
        return self.__transactions

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def previous_hash(self):
        return self.__previous_hash
