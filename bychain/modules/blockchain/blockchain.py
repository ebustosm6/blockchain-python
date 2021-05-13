import copy
from datetime import datetime
from typing import Dict, List

from bychain.modules.blockchain.block import Block


class BlockChain(object):
    DIFFICULTY = 2
    STARTING_HASH = '0'
    REQUIRED_TRANSACTION_FIELDS = {'id', 'value', 'timestamp'}
    OPTIONAL_TRANSACTION_FIELDS = set()

    @classmethod
    def __is_valid_proof(cls, block: Block, block_hash: str):
        return block_hash.startswith('0' * cls.DIFFICULTY) and block_hash == block.hash

    @classmethod
    def proof_of_work(cls, block: Block):
        computed_hash = block.hash
        while not computed_hash.startswith('0' * cls.DIFFICULTY):
            block.nonce += 1
            computed_hash = block.hash

        return computed_hash

    @classmethod
    def __validate_new_transaction(cls, transaction: Dict):
        is_valid = False

        for field in cls.REQUIRED_TRANSACTION_FIELDS:
            if not transaction.get(field):
                break
        else:
            for field in transaction:
                if not (field in cls.REQUIRED_TRANSACTION_FIELDS or field in cls.OPTIONAL_TRANSACTION_FIELDS):
                    break
            else:
                is_valid = True

        return is_valid

    @classmethod
    def validate_chain(cls, chain: List[Dict]):
        result = False
        previous_hash = cls.STARTING_HASH

        if isinstance(chain, list) and chain:
            for block_json in chain:
                block_hash = block_json.pop('hash')
                block = Block(**block_json)
                if not (cls.__is_valid_proof(block=block, block_hash=block_hash) and
                        previous_hash == block.previous_hash):
                    break
                previous_hash = block.hash

            else:
                result = True

        return result

    def __init__(self):
        self.__unconfirmed_transactions = []
        self.__chain = []
        self.__create_genesis_block()

    def __create_genesis_block(self):
        genesis_block = Block(index=0, transactions=[], previous_hash=self.STARTING_HASH)
        self.proof_of_work(block=genesis_block)
        self.__chain.append(genesis_block)

    def add_block(self, block: Block, proof: str):
        added = False

        if self.last_block.hash == block.previous_hash:
            if self.__is_valid_proof(block=block, block_hash=proof):
                self.__chain.append(block)
                added = True

        return added

    def add_new_transaction(self, transaction: Dict):
        added = False
        if isinstance(transaction, dict):
            transaction['timestamp'] = datetime.utcnow().timestamp()
            if self.__validate_new_transaction(transaction=transaction):
                self.__unconfirmed_transactions.append(transaction)
                added = True

        return added

    def mine(self):
        mined_block = None
        if self.__unconfirmed_transactions:
            last_block = self.last_block
            new_block = Block(index=last_block.index + 1,
                              transactions=self.__unconfirmed_transactions,
                              previous_hash=last_block.hash)

            proof = self.proof_of_work(block=new_block)
            added = self.add_block(block=new_block, proof=proof)
            if added:
                self.__unconfirmed_transactions = []
                mined_block = new_block

        return mined_block

    @property
    def last_block(self) -> Block:
        last = None
        if len(self.__chain) > 0:
            last = copy.deepcopy(self.__chain[-1])
        return last

    @property
    def chain(self):
        return [Block.to_json(block) for block in self.__chain]

    @chain.setter
    def chain(self, chain: List[Dict]):
        new_chain = [Block(**block_json) for block_json in chain]
        self.__chain = new_chain

    @property
    def unconfirmed_transactions(self):
        return copy.deepcopy(self.__unconfirmed_transactions)
