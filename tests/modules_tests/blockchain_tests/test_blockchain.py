import unittest
from unittest import mock
from datetime import datetime

from bychain.modules.blockchain.block import Block
from bychain.modules.blockchain.blockchain import BlockChain


class TestBlockChain(unittest.TestCase):

    def test_initialization(self):
        expected_index = 0
        expected_transactions = []
        expected_previous_hash = '0'
        expected_chain = [
            {
                'hash': mock.ANY,
                'index': 0,
                'nonce': mock.ANY,
                'previous_hash': '0',
                'timestamp': mock.ANY,
                'transactions': []
            }
        ]
        expected_unconfirmed_transactions = []
        expected_timestamp = datetime.utcnow().timestamp()

        chain = BlockChain()
        last_block = chain.last_block

        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)
        self.assertEqual(last_block.previous_hash, expected_previous_hash)
        self.assertTrue(last_block.timestamp - expected_timestamp < .1)
        self.assertTrue(last_block.nonce > 0)
        self.assertEqual(chain.chain, expected_chain)
        self.assertEqual(chain.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_proof_of_work(self):
        expected_hash = '00c7200e876c6f2f93297d37f3253e559adf609a16fffd3c198a0792055f052d'
        expected_nonce = 148
        expected_unconfirmed_transactions = []
        block = Block(index=1, transactions=[], previous_hash='0', timestamp=123456)

        chain = BlockChain()
        generated_hash = chain.proof_of_work(block=block)

        self.assertEqual(block.hash, expected_hash)
        self.assertEqual(block.nonce, expected_nonce)
        self.assertEqual(generated_hash, expected_hash)
        self.assertEqual(chain.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_add_block_ok(self):
        expected_index = 1
        expected_transactions = []
        expected_timestamp = 123456
        expected_unconfirmed_transactions = []

        chain = BlockChain()
        first_block = chain.last_block
        block = Block(index=1, transactions=[], previous_hash=chain.last_block.hash, timestamp=123456)
        generated_hash = chain.proof_of_work(block=block)
        expected_chain = [
            {
                'hash': first_block.hash,
                'index': 0,
                'nonce': first_block.nonce,
                'previous_hash': '0',
                'timestamp': first_block.timestamp,
                'transactions': []
            },
            {
                'hash': mock.ANY,
                'index': 1,
                'nonce': block.nonce,
                'previous_hash': chain.last_block.hash,
                'timestamp': 123456,
                'transactions': []
            }
        ]
        added = chain.add_block(block=block, proof=block.hash)
        last_block = chain.last_block

        self.assertEqual(added, True)
        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)
        self.assertEqual(last_block.hash, generated_hash)
        self.assertEqual(last_block.timestamp, expected_timestamp)
        self.assertEqual(chain.chain, expected_chain)
        self.assertEqual(chain.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_add_block_with_transactions_ok(self):
        expected_index = 1
        expected_transactions = [{'id': 'transaction_1', 'value': 1}]
        expected_timestamp = 123456
        expected_unconfirmed_transactions = []

        chain = BlockChain()
        first_block = chain.last_block
        block = Block(index=1, transactions=[{'id': 'transaction_1', 'value': 1}], previous_hash=chain.last_block.hash,
                      timestamp=123456)
        generated_hash = chain.proof_of_work(block=block)
        expected_chain = [
            {
                'hash': first_block.hash,
                'index': 0,
                'nonce': first_block.nonce,
                'previous_hash': '0',
                'timestamp': first_block.timestamp,
                'transactions': []
            },
            {
                'hash': mock.ANY,
                'index': 1,
                'nonce': block.nonce,
                'previous_hash': chain.last_block.hash,
                'timestamp': 123456,
                'transactions': [{'id': 'transaction_1', 'value': 1}]
            }
        ]
        added = chain.add_block(block=block, proof=block.hash)
        last_block = chain.last_block

        self.assertEqual(added, True)
        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)
        self.assertEqual(last_block.hash, generated_hash)
        self.assertEqual(last_block.timestamp, expected_timestamp)
        self.assertEqual(chain.chain, expected_chain)
        self.assertEqual(chain.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_add_block_invalid_previous_hash_ko(self):
        expected_index = 0
        expected_transactions = []
        expected_chain = [
            {
                'hash': mock.ANY,
                'index': 0,
                'nonce': mock.ANY,
                'previous_hash': '0',
                'timestamp': mock.ANY,
                'transactions': []
            }
            ]
        expected_unconfirmed_transactions = []

        chain = BlockChain()
        block = Block(index=1, transactions=[], previous_hash='invalid', timestamp=123456)
        generated_hash = chain.proof_of_work(block=block)
        added = chain.add_block(block=block, proof=block.hash)
        last_block = chain.last_block

        self.assertEqual(added, False)
        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)
        self.assertNotEqual(last_block.hash, generated_hash)
        self.assertEqual(chain.chain, expected_chain)
        self.assertEqual(chain.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_add_block_invalid_proof_ko(self):
        expected_index = 0
        expected_transactions = []

        chain = BlockChain()
        block = Block(index=1, transactions=[], previous_hash=chain.last_block.hash, timestamp=123456)
        added = chain.add_block(block=block, proof=block.hash)
        last_block = chain.last_block

        self.assertEqual(added, False)
        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)

    def test_add_new_transaction_ok(self):
        expected_unconfirmed_transactions = [
            {'id': 'transaction_1', 'value': 1, 'timestamp': mock.ANY},
            {'id': 'transaction_2', 'value': 2, 'timestamp': mock.ANY}
        ]

        chain = BlockChain()
        added_1 = chain.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        added_2 = chain.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})

        self.assertEqual(added_1, True)
        self.assertEqual(added_2, True)
        self.assertEqual(chain.unconfirmed_transactions, expected_unconfirmed_transactions)
        self.assertIsNot(chain._BlockChain__unconfirmed_transactions, chain.unconfirmed_transactions)

    def test_add_new_transaction_missing_required_fields_ko(self):
        chain = BlockChain()
        added_1 = chain.add_new_transaction(transaction={'value': 1})
        added_2 = chain.add_new_transaction(transaction={'id': 'transaction_2'})

        self.assertEqual(added_1, False)
        self.assertEqual(added_2, False)
        self.assertEqual(chain.unconfirmed_transactions, [])

    def test_add_new_transaction_non_allowed_fields_ko(self):
        expected_transactions = [
            {'id': 'transaction_1', 'value': 1, 'timestamp': mock.ANY}]

        chain = BlockChain()
        added_1 = chain.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        added_2 = chain.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2, 'invalid': 0})

        self.assertEqual(added_1, True)
        self.assertEqual(added_2, False)
        self.assertEqual(chain._BlockChain__unconfirmed_transactions, expected_transactions)

    def test_mine(self):
        expected_index = 1
        expected_transactions = [
            {'id': 'transaction_1', 'value': 1, 'timestamp': mock.ANY},
            {'id': 'transaction_2', 'value': 2, 'timestamp': mock.ANY}
        ]

        chain = BlockChain()
        added_1 = chain.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        added_2 = chain.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})
        chain.mine()

        self.assertEqual(added_1, True)
        self.assertEqual(added_2, True)
        self.assertEqual(chain.last_block.index, expected_index)
        self.assertEqual(chain.last_block.transactions, expected_transactions)

    def test_validate_chain_ok(self):
        chain = BlockChain()
        block = Block(index=1, transactions=[], previous_hash=chain.last_block.hash, timestamp=123456)
        chain.add_block(block=block, proof=block.hash)
        is_valid = chain.validate_chain(chain=chain.chain)

        self.assertEqual(is_valid, True)

    def test_validate_chain_invalid_empty_ko(self):
        chain = BlockChain()
        is_valid = chain.validate_chain(chain=[])

        self.assertEqual(is_valid, False)

    def test_validate_chain_invalid_type_ko(self):
        chain = BlockChain()
        is_valid = chain.validate_chain(chain=None)

        self.assertEqual(is_valid, False)

    def test_validate_chain_invalid_previous_hash_ko(self):
        chain = BlockChain()
        block = Block(index=1, transactions=[], previous_hash=chain.last_block.hash, timestamp=123456)
        chain.proof_of_work(block=block)
        chain.add_block(block=block, proof=block.hash)
        chain_json = chain.chain
        chain_json[1]['previous_hash'] = 'invalid'
        is_valid = chain.validate_chain(chain=chain_json)

        self.assertEqual(is_valid, False)

    def test_validate_chain_invalid_proof_hash_ko(self):
        chain = BlockChain()
        block = Block(index=1, transactions=[], previous_hash=chain.last_block.hash, timestamp=123456)
        chain.proof_of_work(block=block)
        chain.add_block(block=block, proof=block.hash)
        chain_json = chain.chain
        chain_json[1]['hash'] = 'invalid'
        is_valid = chain.validate_chain(chain=chain_json)

        self.assertEqual(is_valid, False)

