from flask import current_app as app
import json


class Fruit:
    def __init__(self, id, uid, sid, pid, quantity, time_ordered, time_fulfilled):
        self.id = id
        self.uid = uid
        self.sid = sid
        self.pid = pid
        self.quantity = quantity
        self.time_ordered = time_ordered
        self.time_fulfilled = time_fulfilled

    # Get all fruits by fruit id
    @staticmethod
    def get(id):
        rows = app.db.execute("""
                              SELECT *
                              FROM Fruits
                              WHERE id = :id
                              """,
                              id=id)
        return rows

    # Get all fruits by user id
    # Used to display ordered items in fruit page
    @staticmethod
    def get_by_uid(uid):
        rows = app.db.execute("""
                              SELECT *
                              FROM Fruits
                              WHERE uid = :uid
                              """,
                              uid=uid)
        return rows
    
    @staticmethod
    def get_by_date(uid, date):
        rows = app.db.execute("""
            SELECT Fruits.id AS id, Fruits.items, Fruits.time_ordered, Fruits.time_fulfilled
            FROM Fruits
            WHERE Fruits.uid = :uid
            AND Fruits.time_ordered::date = :date
        """, uid=uid, date=date)

        # Parsing the items JSON to get product details
        result = []
        for row in rows:
            fruit_id, items_json, time_ordered, time_fulfilled = row

            try:
                items = json.loads(items_json)
            except json.JSONDecodeError:
                print(f"Error: Failed to decode JSON for fruit ID: {fruit_id}")
                continue

            for item in items:
                if "pid" not in item or "quantity" not in item:
                    print(f"Error: Invalid item format in fruit ID: {fruit_id}")
                    continue

                result.append({
                    "fruit_id": fruit_id,
                    "pid": item["pid"],
                    "quantity": item["quantity"],
                    "time_ordered": time_ordered,
                    "time_fulfilled": time_fulfilled
                })

        return result

    
    # Get all fruits by seller id
    # Used to help sellers check which item to fulfill
    @staticmethod
    def get_by_sid(sid):
        rows = app.db.execute("""
                              SELECT *
                              FROM Fruits
                              WHERE sid = :sid
                              """,
                              sid=sid)
        return rows
    
    # Add item to fruit database
    # Used when the user submit order of items in the cart
    import json

    @staticmethod
    def add_to_fruit(uid, items):
        try:
            # Convert items (list) to JSON string
            items_json = json.dumps(items)

            # Insert the serialized items into the database
            rows = app.db.execute("""
                INSERT INTO Fruits (uid, sid, items, time_ordered)
                VALUES (%s, NULL, %s::jsonb, NOW())
                RETURNING id
            """, uid=uid, items=items_json)

            id = rows[0][0]
            print(f"Successfully added fruit entry with id: {id}")
            return Fruit.get(id)
        except Exception as e:
            print(f"Error adding fruit: {e}")
            return None



    @staticmethod
    def fulfill_fruit(id):
        try:
            app.db.execute("""
                UPDATE Fruits
                SET time_fulfilled = NOW()
                WHERE id = :id
            """, id=id)
            return Fruit.get(id)
        except Exception as e:
            print(str(e))
            return None

    # Return true if all items ordered is fulfilled, given user id
    # Used to check fulfillment status of entire fruit of each user
    @staticmethod
    def get_display_data(uid):
        rows = app.db.execute("""
            SELECT Fruits.id AS id, Fruits.items, Fruits.time_ordered, Fruits.time_fulfilled, Fruits.total_price
            FROM Fruits
            WHERE Fruits.uid = :uid
            ORDER BY Fruits.time_ordered DESC
        """, uid=uid)

        result = []
        product_ids = set()  # Collect all product IDs
        orders = {}  # Group items by order time

        for row in rows:
            fruit_id, items_json, time_ordered, time_fulfilled, total_price = row

            if isinstance(items_json, list):
                items_json = json.dumps(items_json)

            try:
                items = json.loads(items_json)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for fruit ID: {fruit_id} - {e}")
                continue

            if time_ordered not in orders:
                orders[time_ordered] = {
                    "items_list": [],
                    "grand_total": total_price,  # Directly set grand_total from total_price in the database
                    "time_fulfilled": time_fulfilled
                }

            for item in items:
                product_ids.add(item["pid"])
                orders[time_ordered]["items_list"].append({
                    "fruit_id": fruit_id,
                    "pid": item["pid"],
                    "quantity": item["quantity"],
                    "price": item.get("price"),
                })

        # Fetch product details for all unique product IDs
        if product_ids:
            product_rows = app.db.execute("""
                SELECT id, name, price FROM Products
                WHERE id = ANY(:product_ids)
            """, product_ids=list(product_ids))

            product_details = {row[0]: {"name": row[1], "price": row[2]} for row in product_rows}

            # Update items with product names and prices
            for order_time, order in orders.items():
                for item in order["items_list"]:
                    product_info = product_details.get(item["pid"])
                    if product_info:
                        item["name"] = product_info["name"]
                        if item["price"] is None:
                            item["price"] = product_info["price"]

                        subtotal = item["quantity"] * item["price"]
                        item["subtotal"] = subtotal

        # Now include total_price as grand_total in the final result
        for time_order, order_data in orders.items():
            result.append({
                "order_time": time_order,
                "items_list": order_data["items_list"],
                "grand_total": order_data["grand_total"],
                "time_fulfilled": order_data["time_fulfilled"]
            })

        return result




    @staticmethod
    def fulfill_fruit(fruit_id):
        try:
            app.db.execute("""
                UPDATE Fruits
                SET time_fulfilled = NOW()
                WHERE id = :fruit_id
            """, fruit_id=fruit_id)
            return True
        except Exception as e:
            print(f"Error fulfilling fruit: {e}")
            return False
