import binascii

import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA

from app import db
from app.models import User


def register_user(form):
    user = User(username=form.username.data, email=form.email.data, company=form.company.data,
                user_role=form.user_role.data)
    user.set_password(form.password.data)
    user.private_key, user.public_key = generate_user_keys()
    db.session.add(user)
    db.session.commit()


def generate_user_keys():
    random_gen = Crypto.Random.new().read
    private_key = RSA.generate(1024, random_gen)
    public_key = private_key.publickey()
    return binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'), \
           binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')


def get_users_in_role(role):
    return User.query.filter_by(user_role=role).all()
