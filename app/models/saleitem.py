from flask import current_app as app

class SaleItem:
    def __init__(self, id, uid, pid, cid, quantity):
        """Initialize a SaleItem instance."""
        self.id = id
        self.uid = uid
        self.pid = pid
        self.cid = cid
        self.quantity = quantity

    @staticmethod
    def get_solditems(uid):
        try:
            query = '''
            SELECT s.id, s.uid, s.pid, s.quantity, p.name
            FROM SaleItems s
            JOIN Products p ON s.pid = p.id
            WHERE s.uid = :uid
            '''
            rows = app.db.execute(query, uid=uid)

            if not rows:
                print(f"No items sold by user: {uid}")
                return []

            print(f"Rows fetched for user {uid}: {rows}")  # Debug print
            return [SaleItems(*row) for row in rows]
        except Exception as e:
            print(f"Error fetching items for sale by user {uid}: {e}")
            return []


    def add_item(self):
        """Add an item to the user's items sold, or update the quantity if it already exists."""
        try:
            # Check if item already exists in user's SaleItems
            existing_item = app.db.execute('''
            SELECT id, quantity FROM SaleItems
            WHERE uid = :uid AND pid = :pid
            ''', uid=self.uid, pid=self.pid)

            if existing_item:
                # Item already in SaleItems, update quantity
                existing_item_id, existing_quantity = existing_item[0]
                new_quantity = existing_quantity + self.quantity
                app.db.execute('''
                UPDATE SaleItems 
                SET quantity = :quantity 
                WHERE id = :id
                ''', quantity=new_quantity, id=existing_item_id)
                print(f"Updated item quantity: SaleItems ID={existing_item_id}, New Quantity={new_quantity}")
            else:
                # Item not in SaleItems, insert new item
                app.db.execute('''
                INSERT INTO SaleItems (uid, pid, quantity) 
                VALUES (:uid, :pid, :quantity)
                ''', uid=self.uid, pid=self.pid, quantity=self.quantity)
                print(f"Item added: UID={self.uid}, PID={self.pid}, Quantity={self.quantity}")

        except Exception as e:
            print(f"Error adding item to cart: {e}")

    def update_quantity(self, new_quantity):
        """Update the quantity of an item in the user's items for sale."""
        try:
            app.db.execute('''
            UPDATE SaleItems 
            SET quantity = :quantity 
            WHERE id = :id
            ''', quantity=new_quantity, id=self.id)
            print(f"Quantity updated: SaleItems ID={self.id}, New Quantity={new_quantity}")
        except Exception as e:
            print(f"Error updating quantity in SaleItems: {e}")

    def remove_item(uid, pid):
        try:
            # Execute the DELETE SQL command to remove the item from the user's items for sale
            app.db.execute('''
            DELETE FROM SaleItems 
            WHERE uid = :uid AND pid = :pid
            ''', uid=uid, pid=pid)
            print(f"Item removed successfully: User ID={uid}, Product ID={pid}")
        except Exception as e:
            print(f"Error removing item from SaleItems: {e}")
