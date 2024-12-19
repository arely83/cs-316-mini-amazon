from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user
import datetime

from .models.purchase import Purchase
from humanize import naturaltime
from flask import Blueprint

bp = Blueprint('purchase', __name__)


import logging
from flask import Flask

app = Flask(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)
app.logger.setLevel(logging.ERROR)


# Utility function for humanizing time
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/allpurchases', methods=['GET'])
def get_all_purchases_by_id():
    """
    Fetch and display all purchases for the authenticated user, with sorting options.
    """
    if not current_user.is_authenticated:
        flash("Please log in to view your purchase history.", "error")
        return redirect(url_for('users.login'))

    try:
        # Get sorting parameters from the query string
        sort_by = request.args.get('sort_by', 'time_purchased')  # Default sort column
        order = request.args.get('order', 'desc')  # Default sort order

        # Validate query parameters
        valid_sort_columns = ['time_purchased', 'price', 'name']
        valid_orders = ['asc', 'desc']

        if sort_by not in valid_sort_columns or order not in valid_orders:
            sort_by = 'time_purchased'
            order = 'desc'

        # Fetch sorted purchases for the current user
        purchases = Purchase.get_user_purchases(current_user.id, sort_by=sort_by, order=order) or []

        # Render the purchases page
        return render_template('purchases.html',
                               purchases=purchases,
                               humanize_time=humanize_time,
                               sort_by=sort_by,
                               order=order)
    except Exception as e:
        # Log the error
        app.logger.error(f"Error fetching purchases: {e}", exc_info=True)
        flash("An error occurred while fetching your purchases. Please try again.", "error")
        return redirect(url_for('error_page'))  # Replace with a custom error page
