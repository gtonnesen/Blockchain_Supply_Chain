from hashlib import sha256
import time
from time import time
import datetime
from ..blockchain import *
import json
import binascii

from Cryptodome.Hash import SHA
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5


MINING_DIFFICULTY = 2


class Block:
    def __init__(self, index, block_type, order_id, tx, timestamp, previous_hash, nonce=0):
        """
        :param index: integer signifying the block's index in the chain
        :param block_type: string - either initiated or tracked. initiated means new first block in a new order.
                                    tracked means a block relating to an order that has already been initiated.
        :param order_id: unique id of the order to which the pertains
        :param tx: dictionary of transaction information - there is only one transaction per block
        :param timestamp: timestamp from when the block was mined
        :param previous_hash: hash of previous block in the chain
        :param nonce: integer value generated in proof of work/mining algorithm, starts at zero by default
        """
        self.index = index
        self.block_type = block_type
        self.order_id = order_id
        self.transaction = tx
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """return a hash value of the block contents"""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def __str__(self):
        """returns block contents in string form"""
        my_hash = self.compute_hash()
        return f'index: {self.index}\nblock type: {self.block_type}\nOrder Id: {self.order_id}\nTransaction: ' \
            f'{self.transaction}\nTimestamp: {datetime.datetime.fromtimestamp(self.timestamp)}\nPrevious Hash: {self.previous_hash}\nHash: {my_hash}' \
            f'\nNonce: {self.nonce}'


class Blockchain:
    def __init__(self):
        """blockchain object"""
        self.chain = []
        self.order_id = str(uuid4()).replace('-', '')  # Generate unique id as a string to be used as order_id
        self.create_genesis_block()  # instantiate genesis block
        self.transaction = dict()
        self.peers = {'http://127.0.0.1:8001', 'http://127.0.0.1:8002'}  # node addresses are hard coded into blockchain

    def create_genesis_block(self):
        """creates first block in chain"""
        gen_block = Block(0, '', self.order_id, '', time(), '00')
        gen_block.hash = gen_block.compute_hash()
        self.chain.append(gen_block)

    @property
    def last_block(self):
        """returns last block in chain"""
        return self.chain[-1]

    def __str__(self):
        """returns blockchain in string form"""
        bc_string = ''
        count = 0
        for block in self.chain:
            bc_string += f'\n\nBlock {count}:\n{block}'
            count += 1
        return bc_string

    @staticmethod
    def verify_transaction_signature(transaction, actor_key, signature):
        """
        Check that the provided signature corresponds to transaction
        signed by the public key (actor's public key)
        """
        actor_key = actor_key
        public_key = RSA.importKey(binascii.unhexlify(actor_key))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        return verifier.verify(h, binascii.unhexlify(signature))

    def submit_transaction(self, transaction, actor, signature):
        """
        add a transaction to the transaction array if it is verified
        """
        transaction_verified = self.verify_transaction_signature(transaction, actor, signature)
        if transaction_verified:
            self.transaction = transaction
            return len(self.chain) + 1
        else:
            return False

    def add_announced_block(self, block):
        """adds a block to the chain that was mined by another node"""
        self.chain.append(block)
        return block

    def add_block(self, block):
        """
        Add a block to the blockchain
        """
        self.chain.append(block)
        self.transaction = dict()
        return block

    @staticmethod
    def proof_of_work(block):
        """
        Proof of work algorithm
        """
        block.nonce = 0
        while Blockchain.valid_proof(block) is False:
            block.nonce += 1
        return block.nonce

    @staticmethod
    def valid_proof(block, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        guess_hash = block.compute_hash()
        return guess_hash[:difficulty] == '0' * difficulty

    def mine(self, block_type, node_id):
        """computes hash redundantly until the hash begins with 2 zeros- incrementing the nonce each time to ensure a
        different hash value is generated upon each iteration"""
        # We run the proof of work algorithm to get the next proof...
        previous_hash = self.last_block.compute_hash()
        proposed_block = Block(len(self.chain), block_type, node_id, self.transaction, time(),
                               previous_hash)
        proposed_block.nonce = self.proof_of_work(proposed_block)
        # Forge the new Block by adding it to the chain
        block = self.add_block(proposed_block)
        return block

    @classmethod
    def check_chain_validity(cls, chain):
        """matches the hashes to the previous hashes to ensure the blockchain is valid"""
        result = True
        previous_hash = '0'
        for block in chain:
            block_hash = block.hash
            if not Blockchain.is_valid_proof(block, block.hash) or previous_hash != block.previous_hash:
                result = False
                break
            block.hash, previous_hash = block_hash, block_hash
        return result

