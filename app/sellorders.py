from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user
import datetime
from .models.sellorder import SellOrder
from.models.fruit import Fruit
from humanize import naturaltime
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from flask import Blueprint



bp = Blueprint('sellorders', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/sellorders')
def sellorders():
    if current_user.is_authenticated:
        sellorders = Fruit.get_by_sid(current_user.id)

        return render_template('orders.html',
                                sellorders=sellorders,
                                humanize_time=humanize_time)
    else: 
        return jsonify({"error": "User not authenticated"}), 404

@bp.route('/sellorders/add/<int:product_id>', methods=['POST'])
def sellorders_add(product_id):
    if current_user.is_authenticated:
        SellOrder.register(current_user.id, product_id, datetime.datetime.now())
        return redirect(url_for('sellorders.sellorders'))

@bp.route('/sellorders/fulfill/<int:order_id>', methods=['POST'])
def fulfill_order(order_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 403

    # Fetch the order
    order = SellOrder.get(order_id)

    # Check if the current user is the seller
    if not order or order.sellerid != current_user.id:
        flash("You are not authorized to fulfill this order.", "error")
        return redirect(url_for('sellorders.sellorders'))

    # Fulfill the order
    success = SellOrder.fulfill_order(order_id)
    if success:
        flash(f"Order ID {order_id} has been fulfilled.", "success")
    else:
        flash(f"Failed to fulfill Order ID {order_id}.", "error")

    return redirect(url_for('sellorders.sellorders'))
