import json
import uuid
from typing import Set, Dict, List

import requests

from bychain.modules.blockchain.block import Block
from bychain.modules.blockchain.blockchain import BlockChain


class BlockChainNode(object):
    __blockchain: BlockChain = None
    __peers: Set[str] = None

    @classmethod
    def clear(cls):
        cls.__blockchain = None
        cls.__peers = None

    @classmethod
    def initialize(cls):
        cls.__blockchain = BlockChain()
        cls.__peers = set()

    @classmethod
    def __announce_new_block(cls, block: Block):
        for peer in cls.__peers:
            url = "http://{}/add_block".format(peer)
            requests.post(url=url, data=json.dumps(Block.to_json(block=block), sort_keys=True))

    @classmethod
    def add_new_transaction(cls, transaction: Dict):
        return cls.__blockchain.add_new_transaction(transaction=transaction)

    @classmethod
    def add_peer(cls, peer: str):
        added = False
        if isinstance(peer, str) and peer:
            cls.__peers.add(peer)
            added = True

        return added

    @classmethod
    def add_block(cls, block: Block, proof: str):
        return cls.__blockchain.add_block(block=block, proof=proof)

    @classmethod
    def mine(cls):
        mined_block = cls.__blockchain.mine()
        if mined_block is not None:
            cls.__announce_new_block(block=mined_block)
        return mined_block

    @classmethod
    def consensus(cls):
        result = False

        longest_chain = None
        current_len = len(cls.__blockchain.chain)

        for peer_node in cls.__peers:
            response = requests.get('http://{}/chain'.format(peer_node))
            if response.status_code == 200:
                length = response.json().get('length', 0)
                chain = response.json().get('chain', [])
                if length > current_len and cls.__blockchain.validate_chain(chain=chain):
                    current_len = length
                    longest_chain = chain

        if longest_chain:
            cls.__blockchain.chain = longest_chain
            result = True

        return result

    def __new__(cls, *args, **kwargs):
        if cls.__blockchain is None:
            cls.__blockchain = BlockChain()
            cls.__peers = set()
        return super().__new__(cls, *args, **kwargs)

    def __init__(self):
        self.__uid = str(uuid.uuid4())

    @property
    def uid(self):
        return self.__uid

    @property
    def last_block(self) -> Block:
        last_block = self.__blockchain.last_block
        return last_block

    @property
    def chain(self):
        return self.__blockchain.chain

    @chain.setter
    def chain(self, new_chain: List[Dict]):
        blocks_chain: List[Block] = []
        for block_json in new_chain:
            block_json.pop('hash')
            blocks_chain.append(Block(**block_json))

        self.__blockchain.chain = blocks_chain

    @property
    def unconfirmed_transactions(self):
        return self.__blockchain.unconfirmed_transactions
