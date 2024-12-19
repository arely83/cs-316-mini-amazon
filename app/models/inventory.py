from flask import current_app as app

class Inventory:
    def __init__(self, id, sellerid, pid, product_name, quantity, time_added):
        self.id = id
        self.sellerid = sellerid
        self.pid = pid
        self.product_name = product_name
        self.quantity = quantity
        self.time_added = time_added

    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT id, sellerid, pid, quantity, time_added
        FROM Inventory
        WHERE id = :id
        ''',
                              id=id)
        return Inventory(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_sellerid_since(sellerid, since):
        rows = app.db.execute('''
        SELECT id, sellerid, pid, quantity, time_added
        FROM Inventory
        WHERE sellerid = :sellerid
        AND time_added >= :since
        ORDER BY time_added DESC
        ''',
                              sellerid=sellerid,
                              since=since)
        return [Inventory(*row) for row in rows]

    @staticmethod
    def get_all_by_sellerid(sellerid):
        rows = app.db.execute("""
        SELECT id, sellerid, pid, product_name, quantity, time_added
        FROM Inventory
        WHERE sellerid = :sellerid
        ORDER BY time_added DESC
        """,
                              sellerid=sellerid)
        return [Inventory(*(row)) for row in rows]

    @staticmethod
    def register(sellerid, pid, product_name, quantity, time_added):
        try:
            rows = app.db.execute("""
            INSERT INTO Inventory(sellerid, pid, product_name, quantity, time_added)
            VALUES(:sellerid, :pid, :product_name, :quantity, :time_added)
            RETURNING id
            """,
                                  sellerid=sellerid,
                                  pid=pid,
                                  product_name=product_name,
                                  time_added=time_added,
                                  quantity=quantity)
            id = rows[0][0]
            return Inventory.get(id)
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def exists(sellerid, pid):
        try: 
            exists = app.db.execute("""
                SELECT * FROM Inventory
                WHERE sellerid = :sellerid AND pid = :pid
                """,
                                    sellerid=sellerid,
                                    pid=pid)
            print("exists?: ", exists)
            return exists
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def update(sellerid, pid, product_name, quantity, time_added):
        try:
            existing_item = app.db.execute('''
            SELECT quantity
            FROM Inventory
            WHERE sellerid = :sellerid AND pid = :pid
            ''', sellerid=sellerid, pid=pid)
            print("model update existing item: ", existing_item)

            if existing_item:
                app.db.execute("""
                UPDATE Inventory
                SET quantity = :quantity, time_added = :time_added
                WHERE sellerid = :sellerid AND pid = :pid
                """, sellerid=sellerid, pid=pid, quantity=quantity, time_added=time_added)
                print(f"Inventory updated: sellerid={sellerid}, pid={pid}, quantity={quantity}")
                return {"updated": True, "quantity": quantity}
            else:
                if not quantity: 
                    quantity = 1
                app.db.execute("""
                INSERT INTO Inventory(sellerid, pid, product_name, quantity, time_added)
                VALUES(:sellerid, :pid, :product_name, :quantity, :time_added)
                """, sellerid=sellerid, pid=pid, product_name=product_name, quantity=quantity, time_added=time_added)
                print(f"New inventory added: sellerid={sellerid}, pid={pid}, quantity={quantity}")
                return {"updated": False, "quantity": quantity}
            
            return Inventory.get_all_by_sellerid_and_pid(sellerid, pid)
        
        except Exception as e:
            print(f"Error in updating inventory: {e}")
            return None

    @staticmethod
    def get_all_by_sellerid_and_pid(sellerid, pid):
        rows = app.db.execute("""
        SELECT id, sellerid, pid, quantity, time_added
        FROM Inventory
        WHERE sellerid = :sellerid AND pid = :pid
        ORDER BY time_added DESC
        """,
                              sellerid=sellerid,
                              pid=pid)
        return [Inventory(*(row)) for row in rows]

    @staticmethod
    def decrement(sellerid, pid, amount):
        try:
            # Ensure no negative quantity
            app.db.execute('''
                UPDATE Inventory
                SET quantity = GREATEST(quantity - :amount, 0)
                WHERE sellerid = :sellerid AND pid = :pid
            ''', sellerid=sellerid, pid=pid, amount=amount)
        except Exception as e:
            print(f"Error in decrementing inventory: {e}")
