from flask import current_app as app
from flask import flash
from flask_login import current_user
from humanize import naturaltime
import datetime


class Purchase:
    def __init__(self, id, uid, pid, product_name, quantity, total_price, time_purchased, time_fulfilled=None):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.product_name = product_name
        self.quantity = quantity
        self.total_price = total_price
        self.time_purchased = time_purchased
        self.time_fulfilled = time_fulfilled

    def humanize_time(dt):
        return naturaltime(datetime.datetime.now() - dt)

    @staticmethod
    def get(id):
        try:
            rows = app.db.execute('''
            SELECT pur.id, pur.uid, pur.pid, p.name AS product_name, pur.quantity, NULL AS total_price, 
                   pur.time_purchased, NULL AS time_fulfilled
            FROM Purchases pur
            JOIN Products p ON p.id = pur.pid
            WHERE pur.id = :id
            ''', id=id)
            return Purchase(*rows[0]) if rows else None
        except Exception as e:
            flash(f"Error fetching purchase: {e}", "error")
            return None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        try:
            rows = app.db.execute('''
            SELECT pur.id, pur.uid, pur.pid, p.name AS product_name, pur.quantity, NULL AS total_price, 
                   pur.time_purchased, NULL AS time_fulfilled
            FROM Purchases pur
            JOIN Products p ON p.id = pur.pid
            WHERE pur.uid = :uid
            AND pur.time_purchased >= :since
            ORDER BY pur.time_purchased DESC
            ''', uid=uid, since=since)
            return [Purchase(*row) for row in rows]
        except Exception as e:
            flash(f"Error fetching purchases since {since}: {e}", "error")
            return []

    @staticmethod
    def get_user_purchases(uid, sort_by='time_purchased', order='desc'):
        valid_sort_columns = {'name': 'p.name', 'time_purchased': 'pur.time_purchased'}
        valid_orders = {'asc': 'ASC', 'desc': 'DESC'}

        sort_column = valid_sort_columns.get(sort_by, 'pur.time_purchased')
        sort_order = valid_orders.get(order, 'DESC')

        try:
            rows = app.db.execute(f'''
                SELECT pur.id, pur.uid, pur.pid, p.name AS product_name, pur.quantity, NULL AS total_price, 
                       pur.time_purchased, NULL AS time_fulfilled
                FROM Purchases pur
                JOIN Products p ON p.id = pur.pid
                WHERE pur.uid = :uid
                ORDER BY {sort_column} {sort_order}
            ''', uid=uid)
            return [Purchase(*row) for row in rows]
        except Exception as e:
            flash(f"Error fetching user purchases: {e}", "error")
            return []

    @staticmethod
    def add_purchase_for_uid(uid, pid, quantity, time_purchased):
        try:
            user_balance = app.db.execute('''
            SELECT account_balance
            FROM Users
            WHERE id = :uid
            ''', uid=uid)

            current_balance = user_balance[0][0] if user_balance else 0

            cart_items = app.db.execute('''
            SELECT c.pid, c.quantity, p.price
            FROM Carts c
            JOIN Products p ON c.pid = p.id
            WHERE c.uid = :uid
            ''', uid=uid)

            total_cost = sum(item[1] * item[2] for item in cart_items)

            if current_balance < total_cost:
                flash(f"Insufficient funds. Available balance: ${current_balance}, Total cost: ${total_cost}", "error")
                return False

            new_balance = current_balance - total_cost

            app.db.execute('''
            UPDATE Users
            SET account_balance = :new_balance
            WHERE id = :uid
            ''', new_balance=new_balance, uid=uid)

            for item in cart_items:
                pid, quantity, price = item
                app.db.execute('''
                INSERT INTO Purchases (uid, pid, time_purchased, quantity)
                VALUES (:uid, :pid, :time_purchased, :quantity)
                ''', uid=uid, pid=pid, time_purchased=time_purchased, quantity=quantity)

            # Clear the cart after purchase
            app.db.execute('''
            DELETE FROM Carts
            WHERE uid = :uid
            ''', uid=uid)

            flash("Purchased successfully!", "success")
            return True
        except Exception as e:
            flash(f"Error adding purchase: {e}", "error")
            return False
