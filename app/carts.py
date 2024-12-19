from flask import redirect, url_for, jsonify, render_template, request, flash
from flask_login import current_user
import datetime
from humanize import naturaltime
from .models.carts import Carts
from .models.purchase import Purchase
from .models.sellorder import SellOrder
from .models.product import Product
from .models.inventory import Inventory
from flask import Blueprint
import json
import csv
from flask import session, current_app
import os
from decimal import Decimal

bp = Blueprint('carts', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/carts', methods=['GET'])
def carts():
    if current_user.is_authenticated:
        uid = current_user.id
        items = Carts.get_cart(uid)

        # Fetch the total price by summing product prices based on the quantity in the cart
        row = current_app.db.execute('''
            SELECT SUM(p.price * c.quantity)
            FROM Carts c
            JOIN Products p ON c.pid = p.id
            WHERE c.uid = :uid
        ''', uid=uid)

        total_price = 0  # Default to 0 if no total price is found
        if row and row[0][0] is not None:
            total_price = row[0][0]
            print(f"Total price calculated from cart items: {total_price}")
        
        # Fetch applied coupon and discount from the database
        coupon_data = current_app.db.execute('''
            SELECT applied_coupon, discount
            FROM Carts
            WHERE uid = :uid
            LIMIT 1
        ''', uid=uid)

        if coupon_data:
            applied_coupon, discount = coupon_data[0]
            if discount is not None:
                new_total = Decimal(total_price) * Decimal(1 - discount / 100)
                print(f"Discount applied: {discount}, new subtotal after discount: {new_total}")
                # Update the total price with the discounted price
                current_app.db.execute('''
                    UPDATE Carts
                    SET total_price = :new_total
                    WHERE uid = :uid
                ''', new_total=new_total, uid=uid)
                total_price = new_total
            else:
                print(f"No discount applied, total price remains: {total_price}")
                # No discount, just update the original total price
                current_app.db.execute('''
                    UPDATE Carts
                    SET total_price = :total_price
                    WHERE uid = :uid
                ''', total_price=total_price, uid=uid)

        return render_template('carts.html', carts=items, total_price=total_price)
    else:
        return jsonify({"error": "User not authenticated"}), 404



@bp.route('/carts/purchase_cart', methods=['POST'])
def purchase_cart():
    if current_user.is_authenticated:
        uid = current_user.id
        items = Carts.get_cart(uid)  # Fetch cart items for the current user

        # Fetch applied coupon and discount for the cart
        coupon_data = current_app.db.execute('''
            SELECT applied_coupon, discount
            FROM Carts
            WHERE uid = :uid
            LIMIT 1
        ''', uid=uid)

        applied_coupon = None
        discount = Decimal(0)  # Default discount is 0%
        if coupon_data:
            applied_coupon, discount = coupon_data[0]
            discount = Decimal(discount or 0) / 100  # Handle NoneType and convert to decimal

        # Calculate total price with discount
        total_price = sum(item.quantity * item.price for item in items)
        discounted_total = total_price * (1 - discount)

        # Update the total_price in the Carts table
        try:
            current_app.db.execute('''
                UPDATE Carts
                SET total_price = :total_price
                WHERE uid = :uid
            ''', total_price=discounted_total, uid=uid)
        except Exception as e:
            flash("Error updating cart total price.", "error")
            print(f"Error updating total_price in Carts: {e}")
            return redirect(url_for('carts.carts'))

        # Check user's account balance
        user_balance = current_app.db.execute('''
            SELECT account_balance
            FROM Users
            WHERE id = :uid
        ''', uid=uid)[0][0]

        if user_balance < discounted_total:
            flash("Insufficient balance to complete the purchase.", "error")
            return redirect(url_for('carts.carts'))

        # Prepare the JSON array for the `items` column in the Fruits table
        fruits_items = [{"pid": item.pid, "quantity": item.quantity} for item in items]

        # Add entry to the `Fruits` table
        try:
            current_app.db.execute('''
                INSERT INTO Fruits (uid, sid, items, time_ordered, total_price)
                VALUES (:uid, NULL, :items, NOW(), :total_price)
            ''', uid=uid, items=json.dumps(fruits_items), total_price=discounted_total)  # Ensure JSON is serialized properly
            print(f"Added entry to Fruits table for User ID {uid}.")
        except Exception as e:
            flash("Error adding entry to Fruits table.", "error")
            print(f"Error inserting into Fruits: {e}")
            return redirect(url_for('carts.carts'))

        # Update user's account balance
        try:
            current_app.db.execute('''
                UPDATE Users
                SET account_balance = account_balance - :amount
                WHERE id = :uid
            ''', amount=discounted_total, uid=uid)
        except Exception as e:
            flash("Error updating user balance.", "error")
            print(f"Error updating balance: {e}")
            return redirect(url_for('carts.carts'))

        # Further processing for each item in the cart
        for item in items:
            try:
                sellerid = Product.get_sellerid_by_pid(item.pid)[0][0]

                # Add purchase record
                Purchase.add_purchase_for_uid(uid, item.pid, item.quantity, datetime.datetime.now())

                # Register the sell order
                SellOrder.register(uid, sellerid, item.pid, item.quantity, datetime.datetime.now(), False)

                # Decrease inventory quantity
                current_app.db.execute('''
                    UPDATE Inventory
                    SET quantity = quantity - :quantity
                    WHERE pid = :pid AND quantity >= :quantity
                ''', quantity=item.quantity, pid=item.pid)

                # Check inventory update success
                updated_quantity = current_app.db.execute('''
                    SELECT quantity
                    FROM Inventory
                    WHERE pid = :pid
                ''', pid=item.pid)[0][0]

                if updated_quantity < 0:
                    raise ValueError(f"Inventory quantity for Product ID {item.pid} cannot be negative.")

                # Remove the item from the cart
                Carts.remove_item(uid, item.pid)

                print(f"Purchase and sell order processed for Product ID {item.pid}. Remaining inventory: {updated_quantity}")
            except Exception as e:
                flash(f"Error processing Product ID {item.pid}.", "error")
                print(f"Error processing Product ID {item.pid}: {e}")

        # Clear the cart and show success message
        flash(f"Purchase successful! Total charged: ${discounted_total:.2f}", "success")
        return redirect(url_for('purchase.get_all_purchases_by_id'))

    else:
        return jsonify({"error": "User not authenticated"}), 404



@bp.route('/carts/update_quantity', methods=['POST'])
def update_quantity():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 404

    # Retrieve data from request (e.g., item ID and action)
    item_id = request.form.get('pid')  # Product ID from form
    action = request.form.get('action')  # Action: 'increase' or 'decrease'

    # Ensure values are present and valid
    if not item_id or not action:
        print("Invalid input received")
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Convert to appropriate types if necessary
        item_id = int(item_id)

        # Fetch the item from the cart
        cart_items = Carts.get_cart(current_user.id)
        cart_item = next((item for item in cart_items if item.pid == item_id), None)
        if not cart_item:
            return jsonify({"error": "Item not found in cart"}), 404

        # Update quantity based on action
        if action == 'increase':
            new_quantity = cart_item.quantity + 1
        elif action == 'decrease' and cart_item.quantity > 1:
            new_quantity = cart_item.quantity - 1
        else:
            return jsonify({"error": "Invalid action or quantity too low"}), 400

        # Update the item quantity in the database
        cart_item.quantity = new_quantity
        cart_item.update_quantity(new_quantity)

        print(f"Quantity updated successfully for item ID: {item_id}, new quantity: {new_quantity}")
        return redirect(url_for('carts.carts'))
    except Exception as e:
        print(f"Error updating quantity: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/carts/remove_item', methods=['POST'])
def remove_item():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 404

    # Retrieve data from request (e.g., item ID)
    item_id = request.form.get('pid')

    # Ensure values are present and valid
    if not item_id:
        print("Invalid input received")
        return jsonify({"error": "Invalid input"}), 400

    try:
        # Convert to appropriate types if necessary
        item_id = int(item_id)

        # Remove the item from the cart for the current user
        Carts.remove_item(current_user.id, item_id)

        print(f"Item removed successfully for item ID: {item_id}")
        return redirect(url_for('carts.carts'))
    except Exception as e:
        print(f"Error removing item: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/carts/add/<int:product_id>/<int:seller_id>', methods=['POST'])
def add_to_cart(product_id, seller_id):
    if not current_user.is_authenticated:
        flash("You must be logged in to add items to the cart.", "error")
        return redirect(url_for('users.login'))

    # Check if the seller has enough stock
    seller_inventory = current_app.db.execute('''
        SELECT quantity
        FROM Inventory
        WHERE sellerid = :seller_id AND pid = :product_id
    ''', seller_id=seller_id, product_id=product_id)

    if not seller_inventory or seller_inventory[0][0] <= 0:
        flash("This product is currently out of stock for the selected seller.", "error")
        return redirect(url_for('product.get_product', id=product_id))

    # Add the item to the cart
    quantity = int(request.form.get('quantity', 1))  # Default to 1 if no quantity provided
    if quantity > seller_inventory[0][0]:
        flash("Not enough stock available for the requested quantity.", "error")
        return redirect(url_for('product.get_product', id=product_id))

    cart_item = Carts(id=None, uid=current_user.id, pid=product_id, quantity=quantity)
    cart_item.add_item()

    flash("Product added to cart successfully.", "success")
    return redirect(url_for('carts.carts'))


@bp.route('/carts/apply_coupon', methods=['POST'])
def apply_coupon():
    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 404

    coupon_code = request.form.get('coupon_code')
    if not coupon_code:
        flash("Please enter a coupon code.", "error")
        return redirect(url_for('carts.carts'))

    # Load Coupons.csv and check for the coupon
    coupons_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'data', 'Coupons.csv')
    with open(coupons_path, 'r') as file:
        coupons = {row[0]: Decimal(row[1]) for row in csv.reader(file)}

    discount = coupons.get(coupon_code)
    if discount is None:
        flash("Invalid coupon code.", "error")
        return redirect(url_for('carts.carts'))

    # Save the coupon and discount to the database
    current_app.db.execute('''
        UPDATE Carts
        SET applied_coupon = :coupon_code, discount = :discount
        WHERE uid = :uid
    ''', coupon_code=coupon_code, discount=discount, uid=current_user.id)

    flash(f"Coupon applied! {discount}% off your total price.", "success")
    return redirect(url_for('carts.carts'))