import json

from flask.app import Flask, Response
from flask.globals import request

from bychain.modules.blockchain.node import BlockChainNode
from bychain.modules.blockchain.block import Block

app = Flask(__name__)
node = BlockChainNode()


@app.route('/transaction', methods=['POST'])
def new_transaction():
    response = Response(status=400, response='Invalid transaction data')
    tx_data = request.get_json()

    added = node.add_new_transaction(tx_data)
    if added:
        response = Response(status=201, response='Added transaction successfully')

    return response


@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = node.chain
    body = {
        "length": len(chain_data),
        "chain": chain_data
    }
    return Response(status=200, response=json.dumps(body), content_type='application/json')


@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    response = Response(status=204)
    mined_block = node.mine()
    if isinstance(mined_block, Block):
        body = {
            "block_index": mined_block.index
        }
        response = Response(status=200, response=json.dumps(body), content_type='application/json')
    return response


@app.route('/pending', methods=['GET'])
def get_pending_transactions():
    response = Response(status=204)
    unconfirmed_transactions = node.unconfirmed_transactions
    if unconfirmed_transactions:
        response = Response(status=200, response=json.dumps(unconfirmed_transactions), content_type='application/json')
    return response


@app.route('/nodes', methods=['POST'])
def register_new_peers():
    response = Response(status=400, response='Invalid nodes data')
    peers = request.get_json()
    if peers:
        for peer in peers:
            node.add_peer(peer=peer)
            response = Response(status=200, response='Added nodes successfully')

    return response


@app.route('/add_block', methods=['POST'])
def validate_and_add_block():
    response = Response(status=400, response='Invalid nodes data')

    block_json = request.get_json()
    proof = block_json.pop('hash')
    block = Block(**block_json)
    added = node.add_block(block=block, proof=proof)

    if added:
        response = Response(status=201, response='Added block successfully')

    return response
