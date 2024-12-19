from flask import current_app as app

class Carts:
    def __init__(self, id, uid, pid, quantity, product_name=None, price=None):
        """Initialize a cart instance."""
        self.id = id
        self.uid = uid
        self.pid = pid
        self.quantity = quantity
        self.product_name = product_name  # Product Name
        self.price = price

    @staticmethod
    def get_cart(uid):
        try:
            query = '''
            SELECT c.id, c.uid, c.pid, c.quantity, p.name, p.price
            FROM Carts c
            JOIN Products p ON c.pid = p.id
            WHERE c.uid = :uid
            '''
            rows = app.db.execute(query, uid=uid)

            if not rows:
                print(f"No items found in cart for user: {uid}")
                return []

            print(f"Rows fetched for user {uid}: {rows}")  # Debug print
            return [Carts(*row) for row in rows]
        except Exception as e:
            print(f"Error fetching cart for user {uid}: {e}")
            return []


    def add_item(self):
        """Add an item to the user's cart or update the quantity if it already exists."""
        try:
            # Check if item already exists in user's cart
            existing_item = app.db.execute('''
            SELECT id, quantity FROM Carts
            WHERE uid = :uid AND pid = :pid
            ''', uid=self.uid, pid=self.pid)

            if existing_item:
                # Item already in cart, update quantity
                existing_item_id, existing_quantity = existing_item[0]
                new_quantity = existing_quantity + self.quantity
                app.db.execute('''
                UPDATE Carts 
                SET quantity = :quantity 
                WHERE id = :id
                ''', quantity=new_quantity, id=existing_item_id)
                print(f"Updated item quantity: Cart ID={existing_item_id}, New Quantity={new_quantity}")
            else:
                # Item not in cart, insert new item
                app.db.execute('''
                INSERT INTO Carts (uid, pid, quantity) 
                VALUES (:uid, :pid, :quantity)
                ''', uid=self.uid, pid=self.pid, quantity=self.quantity)
                print(f"Item added: UID={self.uid}, PID={self.pid}, Quantity={self.quantity}")

        except Exception as e:
            print(f"Error adding item to cart: {e}")

    def update_quantity(self, new_quantity):
        """Update the quantity of an item in the user's cart."""
        try:
            app.db.execute('''
            UPDATE Carts 
            SET quantity = :quantity 
            WHERE id = :id
            ''', quantity=new_quantity, id=self.id)
            print(f"Quantity updated: Cart ID={self.id}, New Quantity={new_quantity}")
        except Exception as e:
            print(f"Error updating quantity in cart: {e}")

    def remove_item(uid, pid):
        try:
            # Execute the DELETE SQL command to remove the item from the user's cart
            app.db.execute('''
            DELETE FROM Carts 
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid)
            print(f"Item removed successfully: User ID={uid}, Product ID={pid}")
        except Exception as e:
            print(f"Error removing item from cart: {e}")
