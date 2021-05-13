import copy
import json
import unittest
from unittest import mock
from datetime import datetime

from bychain.modules.blockchain.node import BlockChainNode
from bychain.modules.blockchain.block import Block
from bychain.modules.blockchain.blockchain import BlockChain


class ResponseMock(object):

    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body

    def json(self):
        return self.body


class TestBlockChainNode(unittest.TestCase):

    def setUp(self):
        super().setUp()
        BlockChainNode.clear()
        self.maxDiff = None

    def tearDown(self) -> None:
        super().tearDown()
        BlockChainNode.clear()

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

        node = BlockChainNode()
        last_block = node.last_block

        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)
        self.assertEqual(last_block.previous_hash, expected_previous_hash)
        self.assertTrue(last_block.timestamp - expected_timestamp < .1)
        self.assertTrue(last_block.nonce > 0)
        self.assertEqual(node.chain, expected_chain)
        self.assertEqual(node.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_add_new_transaction_ok(self):
        expected_unconfirmed_transactions = [
            {'id': 'transaction_1', 'value': 1, 'timestamp': mock.ANY},
            {'id': 'transaction_2', 'value': 2, 'timestamp': mock.ANY}
        ]

        node = BlockChainNode()
        added_1 = node.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        added_2 = node.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})

        self.assertEqual(added_1, True)
        self.assertEqual(added_2, True)
        self.assertEqual(node.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_add_block_ok(self):
        expected_index = 1
        expected_transactions = []
        expected_timestamp = 123456
        expected_unconfirmed_transactions = []

        node = BlockChainNode()
        chain = BlockChain()
        first_block = node.last_block
        block = Block(index=1, transactions=[], previous_hash=node.last_block.hash, timestamp=123456)
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
                'previous_hash': node.last_block.hash,
                'timestamp': 123456,
                'transactions': []
            }
        ]
        added = node.add_block(block=block, proof=block.hash)
        last_block = node.last_block

        self.assertEqual(added, True)
        self.assertEqual(last_block.index, expected_index)
        self.assertEqual(last_block.transactions, expected_transactions)
        self.assertIsNot(last_block.transactions, expected_transactions)
        self.assertEqual(last_block.hash, generated_hash)
        self.assertEqual(last_block.timestamp, expected_timestamp)
        self.assertEqual(node.chain, expected_chain)
        self.assertEqual(node.unconfirmed_transactions, expected_unconfirmed_transactions)

    def test_mine(self):
        expected_index = 1
        expected_transactions = [
            {'id': 'transaction_1', 'value': 1, 'timestamp': mock.ANY},
            {'id': 'transaction_2', 'value': 2, 'timestamp': mock.ANY}
        ]

        node = BlockChainNode()
        added_1 = node.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        added_2 = node.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})
        node.mine()

        self.assertEqual(added_1, True)
        self.assertEqual(added_2, True)
        self.assertEqual(node.last_block.index, expected_index)
        self.assertEqual(node.last_block.transactions, expected_transactions)

    @unittest.mock.patch('requests.post')
    def test_mine_announced(self, mock_post):
        expected_index = 1
        expected_transactions = [
            {'id': 'transaction_1', 'value': 1, 'timestamp': mock.ANY},
            {'id': 'transaction_2', 'value': 2, 'timestamp': mock.ANY}
        ]

        node = BlockChainNode()
        node.add_peer(peer='node2')
        node.add_peer(peer='node3')
        node.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        node.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})
        node.mine()
        last_block = node.last_block
        expected_post_calls = [
            unittest.mock.call(
                url='http://node3/add_block',
                data=json.dumps(Block.to_json(block=last_block), sort_keys=True)),
            unittest.mock.call(
                url='http://node2/add_block',
                data=json.dumps(Block.to_json(block=last_block), sort_keys=True))
        ]

        self.assertEqual(node.last_block.index, expected_index)
        self.assertEqual(node.last_block.transactions, expected_transactions)
        self.assertCountEqual(mock_post.call_args_list, expected_post_calls)

    def test_add_peer_ok(self):
        node = BlockChainNode()

        added = node.add_peer(peer='node2')

        self.assertEqual(added, True)
        self.assertEqual(node._BlockChainNode__peers, {'node2'})

    def test_add_peer_none_ko(self):
        node = BlockChainNode()

        added = node.add_peer(peer=None)

        self.assertEqual(added, False)

    def test_add_peer_invalid_ko(self):
        node = BlockChainNode()

        added = node.add_peer(peer='')

        self.assertEqual(added, False)

    @unittest.mock.patch('requests.get')
    def test_consensus_ok(self, mock_get):
        remote_node = BlockChainNode()
        remote_node.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        remote_node.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})
        remote_node.mine()
        remote_node.add_new_transaction(transaction={'id': 'transaction_3', 'value': 3})
        remote_node.mine()
        remote_chain_data = remote_node.chain
        expected_chain = remote_node.chain
        mock_get.side_effect = [
            ResponseMock(status_code=200, body={'length': len(remote_chain_data), 'chain': remote_chain_data})
        ]
        remote_node.clear()
        node = BlockChainNode()
        node.add_peer(peer='node2')

        result = node.consensus()

        self.assertEqual(result, True)
        self.assertEqual(node.chain, expected_chain)

    @unittest.mock.patch('requests.get')
    def test_consensus_ko(self, mock_get):
        mock_get.side_effect = [
            ResponseMock(status_code=200, body={'length': 0, 'chain': []})
        ]
        node = BlockChainNode()
        node.add_peer(peer='node2')

        result = node.consensus()

        self.assertEqual(result, False)
