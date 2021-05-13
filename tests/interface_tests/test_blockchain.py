import json
from unittest import mock

from interface_tests.base_interface_test import BaseInterfaceTest
from modules.blockchain.block import Block
from modules.blockchain.blockchain import BlockChain
from modules.blockchain.node import BlockChainNode


class TestBlockChainInterface(BaseInterfaceTest):

    def test_new_transaction_ok(self):
        expected_status_code = 201
        expected_data = b'Added transaction successfully'

        response = self.client.post('/transaction', content_type='application/json',
                                    data=json.dumps({'id': 1, 'value': 1}))

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data, expected_data)

    def test_new_transaction_invalid_ko(self):
        expected_status_code = 400
        expected_data = b'Invalid transaction data'

        response = self.client.post('/transaction')

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data, expected_data)

    def test_get_chain_empty_ok(self):
        expected_status_code = 200
        expected_content_type = 'application/json'
        expected_body = {
            'chain': [
                {
                    'hash': mock.ANY,
                    'index': 0,
                    'nonce': mock.ANY,
                    'previous_hash': '0',
                    'timestamp': mock.ANY,
                    'transactions': []
                }
            ],
            'length': 1
        }

        response = self.client.get('/chain')

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.content_type, expected_content_type)
        self.assertEqual(response.json, expected_body)

    def test_mine_unconfirmed_transactions_empty_ok(self):
        expected_status_code = 204

        response = self.client.get('/mine')

        self.assertEqual(response.status_code, expected_status_code)

    def test_mine_unconfirmed_transactions_ok(self):
        expected_status_code = 200
        expected_content_type = 'application/json'
        expected_body = {
            "block_index": 1
        }

        self.client.post('/transaction', content_type='application/json',
                         data=json.dumps({'id': 1, 'value': 1}))
        response = self.client.get('/mine')

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.content_type, expected_content_type)
        self.assertEqual(response.json, expected_body)

    def test_get_pending_transactions_empty_ok(self):
        expected_status_code = 204

        response = self.client.get('/pending')

        self.assertEqual(response.status_code, expected_status_code)

    def test_get_pending_transactions_ok(self):
        expected_status_code = 200
        expected_content_type = 'application/json'
        expected_body = [
            {'id': 1, 'timestamp': mock.ANY, 'value': 1}
        ]

        self.client.post('/transaction', content_type='application/json',
                         data=json.dumps({'id': 1, 'value': 1}))
        response = self.client.get('/pending')

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.content_type, expected_content_type)
        self.assertEqual(response.json, expected_body)

    def test_add_nodes_invalid_ko(self):
        expected_status_code = 400
        expected_data = b'Invalid nodes data'

        response = self.client.post('/nodes')

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data, expected_data)

    def test_add_nodes_ok(self):
        expected_status_code = 200
        expected_data = b'Added nodes successfully'

        response = self.client.post('/nodes', content_type='application/json',
                                    data=json.dumps(['node1', 'node2']))

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data, expected_data)

    def test_add_block_ok(self):
        expected_status_code = 201
        expected_data = b'Added block successfully'

        node = BlockChainNode()
        node.add_new_transaction(transaction={'id': 'transaction_1', 'value': 1})
        node.add_new_transaction(transaction={'id': 'transaction_2', 'value': 2})
        node.mine()
        block_json = Block.to_json(block= node.last_block)
        response = self.client.post('/add_block', content_type='application/json',
                                    data=json.dumps(block_json))

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(response.data, expected_data)
