from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime

from .models.order import Order
from flask import jsonify
from humanize import naturaltime
from flask import redirect, url_for

from werkzeug.urls import url_parse
from flask_wtf import FlaskForm


from flask import Blueprint
bp = Blueprint('order', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/orders')
def orders():
    orders = None
    if current_user.is_authenticated:
        orders = Order.get_user_orders(current_user.id)
        
        return render_template('orders.html',
                                orders=orders,
                                humanize_time=humanize_time)
    else: 
        return jsonify({}), 404



@bp.route('/orders/add/<int:product_id>', methods=['POST'])
def orders_add(product_id):
    if current_user.is_authenticated:

        Order.register(current_user.id, product_id, datetime.datetime.now())
        
        # this specifies both a flask blueprint (left order, 
        # which is the name of the Python file in which it's defined)
        # and a route defined within that blueprint (right wishlist, 
        # corresponding to @bp.route('/orders').)
        return(redirect(url_for('order.orders')))