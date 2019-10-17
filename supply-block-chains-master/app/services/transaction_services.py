
from ..constants import NODE_ADDRESS, INITIATED, RETAILER, SUPPLIER, COURIER, TRACKED

import requests  # EXPLAIN!!!!!!!!!!!!!!!!!!!!!!!
import json

all_transactions = []
user_trasnsactions = []


def fetch_transactions():
    """
    Fetch the blockchain data and store it locally
    """

    get_chain_address = "{}/chain".format(NODE_ADDRESS)
    response = requests.get(get_chain_address)  # EXPLAIN!!!!!!!!!!!!!!!!!!
    content = []
    # 200 signifies dictionary successfully received from get_chain_address containing {length: int,
    # chain: list of blocks, peers: list of peer addresses}
    if response.status_code == 200:
        chain = json.loads(response.content)
        for block in chain["chain"]:  # chain['chain'] is a list of blocks
            if block["block_type"] != '':
                tx = block["transaction"]
                tx["timestamp"] = block["timestamp"]
                tx["node_id"] = block["order_id"]
                tx["block_type"] = block["block_type"]
                content.append(tx)

    global all_transactions
    all_transactions = sorted(content, key=lambda k: k['timestamp'], reverse=True)


def fetch_user_transactions(user):
    """
    get all transactions in the blockchain with the users public key
    :return:
    """
    fetch_transactions()
    d_key = ''
    if len(all_transactions) > 0:
        if user.user_role == RETAILER:
            d_key = 'actor'
        elif user.user_role == SUPPLIER:
            d_key = 'supplier'
        elif user.user_role == COURIER:
            d_key = 'courier'
        else:
            return []
    else:
        return []

    if any(d_key in transaction for transaction in all_transactions):
        user_tx = [tx['node_id'] for tx in all_transactions if tx.get(d_key) is not None and tx[d_key] == user.company]
        transaction_ids = set(user_tx)

        return [tx for tx in all_transactions if tx['block_type'] == INITIATED and tx['node_id'] in transaction_ids]
    else:
        return []


def post_transaction(transaction):
    """
    Add an initiated transaction to the blockchain
    :return:
    """
    tx = transaction.__dict__

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(NODE_ADDRESS)

    response = requests.post(new_tx_address, json=tx, headers={'Content-type': 'application/json'})

    if response.status_code == 200:
        return response.content
    else:
        return False


def get_transaction_details(order_number, block_type):
    """
    Get the full details of a transaction
    :param order_number: <str> the node_id of the transaction
    :return:
    """
    return [tx for tx in all_transactions if tx['block_type'] == block_type and tx['node_id'] == order_number]


def get_details(order_number):
    fetch_transactions()
    initiated = get_transaction_details(order_number, INITIATED)
    tracking = get_transaction_details(order_number, TRACKED)
    detail = {}
    tracking_details = []

    if any(initiated):
        detail['order_number'] = initiated[0]['node_id']
        detail['origin'] = initiated[0]['supplier']
        detail['destination'] = initiated[0]['actor']
        detail['item'] = initiated[0]['item']
        detail['quantity'] = initiated[0]['quantity']

        tracking_details.append({
            'actor': initiated[0]['actor'],
            'status': 'pending',
            'timestamp': initiated[0]['timestamp'],
            'courier': ''
        })

        if any(tracking):
            for tracked in tracking:
                tx = {'actor': tracked['actor'],
                      'status': tracked['status'],
                      'timestamp': tracked['timestamp'],
                      'courier': tracked['courier']
                      }
                tracking_details.append(tx)

        sorted_tx = sorted(tracking_details, key=lambda k: k['timestamp'], reverse=True)

        detail['current_status'] = sorted_tx[0]['status']
        detail['timestamp'] = sorted_tx[0]['timestamp']
        detail['courier'] = sorted_tx[0]['courier']

        return detail, sorted_tx


def get_user_insights(user):
    user_txs = fetch_user_transactions(user)

    number = len(user_txs)

    # pending = [tx for tx in all_transactions if user_txs['block_type'] == TRACKED]

    if user.user_role == RETAILER:
        initiated_txs = ''
        accepted_txs = ''
        shipped_txs = ''
    elif user.user_role == SUPPLIER:
        incoming_txs = ''
        shipped_txs = ''
    elif user.user_role == COURIER:
        incoming_txs = ''
        recieved_txs = ''
    else:
        return []

    return number

