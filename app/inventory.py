
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from .models.inventory import Inventory
from .models.product import Product
from flask import jsonify
from humanize import naturaltime
from flask import redirect, url_for
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm

from flask import Blueprint
bp = Blueprint('inventory', __name__)
def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)
@bp.route('/inventory')
def inventory():
    inventory = None
    if current_user.is_authenticated:
        saleitems = Inventory.get_all_by_sellerid(current_user.id)
        
        return render_template('inventory.html',
                                saleitems=saleitems,
                                humanize_time=humanize_time)
    else: 
        return jsonify({}), 404


@bp.route('/inventory/add/<int:product_id>', methods=['POST'])
def inventory_add(product_id):
    if current_user.is_authenticated:
        # Extract quantity from the form data
        quantity = int(request.form.get('quantity', 1))  # Default to 1 if not provided
        prod = Product.get_by_pid(product_id)
        sellerid = current_user.id
        product_name = prod.name

        # Register the product in inventory
        Inventory.register(sellerid, product_id, product_name, quantity, datetime.datetime.now())

        # Redirect to the inventory page
        return redirect(url_for('inventory.inventory'))

@bp.route('/inventory/update_quantity/<int:product_id>', methods=['POST'])
def update_quantity(product_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 403
    # print("test", quantity)
    # new_quantity = request.form.get('new_quantity')
    # new_quantity = quantity
    # if new_quantity is None or int(new_quantity) < 0:
    #     return jsonify({"error": "Invalid input"}), 400
    # Retrieve data from request (e.g., item ID and new quantity)
    # product_id = request.form.get('product_id')  # Product ID from form
    quantity = request.form.get('quantity')  # New quantity from form
    prod = Product.get_by_pid(product_id)
    seller_id = current_user.id
    product_name = Product.get_by_pid(product_id).name
    print("product id: ", product_id, "  new qty:", quantity, "  productname:", product_name, "  sellerid", seller_id)
    print(Inventory.exists(product_id, current_user.id))
    new_quantity = quantity
    # if pid already present for seller, then run update query
    if (Inventory.exists(product_id, current_user.id)):

        # Update inventory
        result = Inventory.update(sellerid=seller_id, pid=product_id, product_name=product_name, quantity=new_quantity, time_added=datetime.datetime.now())
        if result:
            return redirect(url_for('inventory.inventory', product_id=product_id, quantity=quantity))
        else:
            return jsonify({"error": "item exists - Failed to update inventory"}), 500
    # otherwise run an insertion query & default it to quantity=1
    else: 
        # Update inventory
        result = Inventory.update(sellerid=seller_id, pid=product_id, product_name=product_name, quantity=new_quantity, time_added=datetime.datetime.now())
        print(result)
        if result:
            return redirect(url_for('inventory.inventory', product_id=product_id, quantity=quantity))
        else:
            return jsonify({"error": "item doesnt exist - Failed to update inventory"}), 500


# @bp.route('/inventory/update_quantity/<int:product_id>', methods=['POST'])
# def update_quantity(product_id):
#     if not current_user.is_authenticated:
#         return jsonify({"error": "User not authenticated"}), 403

#     # Get the new quantity from the form
#     try:
#         new_quantity = int(request.form.get('quantity'))
#         if new_quantity < 0:
#             raise ValueError("Quantity must be a positive integer.")
#     except (TypeError, ValueError):
#         return jsonify({"error": "Invalid quantity input"}), 400

#     # Fetch product and seller details
#     prod = Product.get_by_pid(product_id)
#     if not prod:
#         return jsonify({"error": "Product not found"}), 404

#     seller_id = current_user.id
#     product_name = prod.name

#     # Check if the item exists in the inventory
#     if Inventory.exists(seller_id, product_id):
#         # If the new quantity is less than the current quantity, decrement the inventory
#         try:
#             result = Inventory.decrement(seller_id, product_id, new_quantity)
#             if result:
#                 flash(f"Decremented quantity for product {product_name}.")
#                 return redirect(url_for('inventory.inventory'))
#             else:
#                 return jsonify({"error": "Failed to decrement inventory"}), 500
#         except ValueError as e:
#             flash(str(e))
#             return redirect(url_for('inventory.inventory'))
#     else:
#         # If the item doesn't exist, create a new inventory entry
#         result = Inventory.register(
#             sellerid=seller_id,
#             pid=product_id,
#             product_name=product_name,
#             quantity=new_quantity,
#             time_added=datetime.datetime.now()
#         )
#         if result:
#             flash(f"Added new inventory entry for product {product_name}.")
#             return redirect(url_for('inventory.inventory'))
#         else:
#             return jsonify({"error": "Failed to add inventory entry"}), 500


@bp.route('/inventory/decrement/<int:product_id>', methods=['POST'])
def decrement_inventory(product_id):
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 403

    # Extract quantity to decrement
    try:
        decrement_quantity = int(request.form.get('quantity'))
        if decrement_quantity <= 0:
            raise ValueError("Decrement quantity must be a positive integer.")
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid decrement quantity"}), 400

    # Attempt to decrement inventory
    try:
        seller_id = current_user.id
        result = Inventory.decrement(seller_id, product_id, decrement_quantity)
        if result:
            flash(f"Successfully decremented {decrement_quantity} units for product ID {product_id}.")
            return redirect(url_for('inventory.inventory'))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('inventory.inventory'))
    except Exception as e:
        flash("An unexpected error occurred.")
        return jsonify({"error": "Failed to decrement inventory"}), 500
