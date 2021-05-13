import unittest
from datetime import datetime

from bychain.modules.blockchain.block import Block


class TestBlock(unittest.TestCase):

    def test_initialization(self):
        expected_index = 1
        expected_transactions = []
        expected_previous_hash = '01234'
        expected_nonce = 0
        expected_timestamp = datetime.utcnow().timestamp()

        block = Block(index=expected_index, transactions=expected_transactions, previous_hash=expected_previous_hash)

        self.assertEqual(block.index, expected_index)
        self.assertEqual(block.transactions, expected_transactions)
        self.assertIsNot(block.transactions, expected_transactions)
        self.assertEqual(block.previous_hash, expected_previous_hash)
        self.assertTrue(block.timestamp - expected_timestamp < .1)
        self.assertEqual(block.nonce, expected_nonce)

    def test_to_json(self):
        expected_index = 1
        expected_hash = '1cc635207b0ba327387d15e11e9d65a9e8439a850384063ebb1e2e07d37a9aa6'
        expected_transactions = []
        expected_previous_hash = '01234'
        expected_timestamp = datetime.utcnow().timestamp()
        expected_nonce = 0

        block_dict = Block.to_json(
            Block(index=expected_index, transactions=expected_transactions, previous_hash=expected_previous_hash,
                  timestamp=123456))

        self.assertEqual(block_dict['index'], expected_index)
        self.assertEqual(block_dict['transactions'], expected_transactions)
        self.assertIsNot(block_dict['transactions'], expected_transactions)
        self.assertEqual(block_dict['previous_hash'], expected_previous_hash)
        self.assertTrue(block_dict['timestamp'] - expected_timestamp < .1)
        self.assertEqual(block_dict['nonce'], expected_nonce)
        self.assertEqual(block_dict['hash'], expected_hash)

    def test_hash(self):
        expected_hash = '1cc635207b0ba327387d15e11e9d65a9e8439a850384063ebb1e2e07d37a9aa6'

        block = Block(index=1, transactions=[], previous_hash='01234', timestamp=123456)

        self.assertEqual(block.hash, expected_hash)
