import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from ..forms import CreateTransactionForm
from ..services.transaction_object import Transaction
from ..services.transaction_services import fetch_user_transactions, post_transaction, get_details
from ..services.user_services import get_users_in_role
from ..constants import INITIATED, SUPPLIER, RETAILER, COURIER, TRACKED
from ..utils import timestamp_to_string
import json

transaction = Blueprint('transaction', __name__)


@transaction.route('/transaction/list', methods=['GET'])
@login_required
def all_transactions():
    tx = fetch_user_transactions(current_user)
    for tr in tx:
        detail, tracking = get_details(tr['node_id'])
        tr['status'] = detail['current_status']
        tr['timestamp'] = detail['timestamp']
        tr['courier'] = detail['courier']
    can_order = (current_user.user_role == RETAILER)
    return render_template('transaction/list.html', title='Transactions', transactions=tx, can_order=can_order,
                           readable_time=timestamp_to_string)


@transaction.route('/transaction/new', methods=['GET', 'POST'])
@login_required
def create_transaction():
    message = ''
    form = CreateTransactionForm()
    form.supplier.choices = [(users.company, users.company) for users in get_users_in_role(SUPPLIER)]
    if form.validate_on_submit():
        new_tx = Transaction(block_type=INITIATED, actor_public_key=current_user.public_key,
                             actor_private_key=current_user.private_key, actor=current_user.company,
                             supplier=form.supplier.data, item=form.item.data, quantity=form.quantity.data)
        new_tx.signature = new_tx.sign_transaction()
        try:
            result = post_transaction(new_tx)
        except:
            result = False
        if result:
            flash('Order has been successfully created.')
            return redirect(url_for('transaction.all_transactions'))
        else:
            message = 'An error occurred.'
    return render_template('transaction/create.html', title='Create', form=form, message=message)


@transaction.route('/transaction/details/<order>', methods=['GET'])
@login_required
def view_transaction(order):
    details, tracking = get_details(order)
    can_act = (details['current_status'] == 'pending') and (details['origin'] == current_user.company)
    non_traking_options = ['pending', 'declined', 'received']
    can_track = (details['current_status'] not in non_traking_options)
    role = {
        'retailer': can_track and current_user.user_role == RETAILER,
        'supplier': can_track and details['courier'] == '' and current_user.user_role == SUPPLIER,
        'courier': can_track and details['courier'] == current_user.company
    }
    couriers = [c.company for c in get_users_in_role(COURIER) if details['courier'] != c.company]
    return render_template('transaction/details.html', title='Details', details=details, tracking=tracking,
                           readable_time=timestamp_to_string, can_act=can_act, role=role, couriers=couriers)


@transaction.route('/transaction/update_tracking', methods=['POST'])
@login_required
def update_tracking():
    data = request.get_json()

    required = ['order', 'status', 'courier']
    if not all(k in data for k in required):
        return 'Missing Values', 400

    new_tx = Transaction(block_type=TRACKED, actor_public_key=current_user.public_key,
                         actor_private_key=current_user.private_key, actor=current_user.company,
                         node_id=data['order'], status=data['status'], courier=data['courier'])
    new_tx.signature = new_tx.sign_transaction()
    try:
        result = post_transaction(new_tx)
    except:
        result = False
    if result:
        flash('Order has been updated successfully.')
        return jsonify({'message': 'Successful'}), 200
    else:
        return 'An error occurred.', 400
