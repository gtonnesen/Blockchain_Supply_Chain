import binascii

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from ..constants import INITIATED, TRACKED
from collections import OrderedDict


class Transaction:

    def __init__(self, block_type, actor_public_key, actor_private_key, actor, node_id=None, supplier=None, item=None,
                 quantity=None, courier=None, status=None):
        self.block_type = block_type
        self.actor = actor
        self.actor_key = actor_public_key
        self.actor_private_key = actor_private_key
        self.node_id = node_id
        self.supplier = supplier
        self.item = item
        self.quantity = quantity
        self.courier = courier
        self.status = status

    def to_dict(self):
        if self.block_type == INITIATED:
            return OrderedDict({
                'actor': self.actor,
                'supplier': self.supplier,
                'item': self.item,
                'quantity': self.quantity
            })
        elif self.block_type == TRACKED:
            return OrderedDict({
                'actor': self.actor,
                'courier': self.courier,
                'status': self.status
            })
        else:
            return False

    def sign_transaction(self):
        """
        Sign transaction with private key
        :return:
        """
        private_key = RSA.import_key(binascii.unhexlify(self.actor_private_key))
        signer = PKCS1_v1_5.new(private_key)
        h = SHA.new(str(self.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')
