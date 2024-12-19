from flask import current_app as app
from flask import jsonify
import logging
logging.basicConfig(level=logging.DEBUG)
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class SellOrder:
    def __init__(self, id, buyerid, sellerid, pid, quantity, time_ordered, fulfilled):
        self.id = id
        self.sellerid = sellerid
        self.buyerid = buyerid
        self.pid = pid
        self.quantity = quantity
        self.time_ordered = time_ordered
        self.fulfilled = fulfilled

    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT *
        FROM SellOrders
        WHERE id = :id
        ''',
                              id=id)
        return SellOrder(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_buyerid(buyerid):
        rows = app.db.execute('''
        SELECT *
        FROM SellOrders
        WHERE buyerid = :buyerid
        ORDER BY time_ordered DESC
        ''',
                              buyerid=buyerid)
        return [SellOrder(*row) for row in rows]
        
    @staticmethod
    def get_all_by_sellerid(sellerid):
        rows = app.db.execute('''
            WITH expanded_items AS (
                SELECT 
                    f.id AS order_id,
                    f.uid AS buyerid,
                    jsonb_array_elements(f.items) AS item,
                    f.time_ordered,
                    f.time_fulfilled
                FROM Fruits f
                WHERE f.sid = :sellerid
            )
            SELECT 
                ei.order_id,
                ei.buyerid,
                (ei.item->>'pid')::INTEGER AS pid,
                p.name AS product_name,
                (ei.item->>'quantity')::INTEGER AS quantity,
                p.price,
                u.firstname || ' ' || u.lastname AS buyer_name,
                u.address,
                ei.time_ordered,
                ei.time_fulfilled,
                ((ei.item->>'quantity')::INTEGER * p.price) AS total_amount
            FROM expanded_items ei
            JOIN Users u ON ei.buyerid = u.id
            JOIN Products p ON (ei.item->>'pid')::INTEGER = p.id
            ORDER BY ei.time_ordered DESC;
        ''', sellerid=sellerid)

        # Define column names manually to map to the rows
        columns = [
            "order_id", "buyerid", "pid", "product_name", "quantity", "price",
            "buyer_name", "address", "time_ordered", "time_fulfilled", "total_amount"
        ]

        # Convert rows (tuples) to dictionaries
        result = []
        for row in rows:
            try:
                result.append(dict(zip(columns, row)))
            except Exception as e:
                print(f"Error converting row to dict: {e}, row: {row}")
                continue
        return result


        
    @staticmethod
    def get_all_by_buyerid(buyerid):
        # s.buyerid, s.sellerid, s.pid, p.name, s.quantity, s.time_ordered, s.fulfilled
        rows = app.db.session.execute('''
        SELECT *
        FROM SellOrders s JOIN Products p ON p.id = s.pid
        WHERE s.buyerid = :buyerid
        ORDER BY time_ordered DESC
        ''',
                              {'buyerid':buyerid})
        
        return rows.fetchall()
        # return [SellOrder(*row) for row in rows]

    
    @staticmethod
    def register(buyerid, sellerid, pid, quantity, time_ordered, fulfilled):
        try:
            rows = app.db.execute("""
            INSERT INTO SellOrders(buyerid, sellerid, pid, quantity, time_ordered, fulfilled)
            VALUES(:buyerid, :sellerid, :pid, :quantity, :time_ordered, :fulfilled)
            RETURNING id
            """,
                                  buyerid=buyerid,
                                  sellerid=sellerid, 
                                  pid=pid, 
                                  quantity=quantity,
                                  time_ordered=time_ordered,
                                  fulfilled=fulfilled)
            id = rows[0][0]
            return SellOrder.get(id)

        except Exception as e:
            print(str(e))
            return None


    @staticmethod
    def fulfill_order(order_id):
        try:
            # Mark the SellOrder as fulfilled
            app.db.execute("""
                UPDATE SellOrders
                SET fulfilled = TRUE
                WHERE id = :order_id
            """, order_id=order_id)

            # Update the Fruits table for the same order
            app.db.execute("""
                UPDATE Fruits
                SET time_fulfilled = NOW()
                WHERE id = (
                    SELECT f.id
                    FROM Fruits f
                    JOIN SellOrders s ON f.id = s.id
                    WHERE s.id = :order_id
                )
            """, order_id=order_id)

            return True
        except Exception as e:
            print(f"Error fulfilling order: {e}")
            return False

    @staticmethod
    def search_orders(sellerid, fulfilled=None, start_date=None, end_date=None):
        query = '''
            SELECT s.id AS order_id, s.buyerid, s.pid, p.name AS product_name, s.quantity, 
                s.time_ordered, s.fulfilled, u.firstname || ' ' || u.lastname AS buyer_name,
                u.address, SUM(s.quantity * p.price) AS total_amount, COUNT(s.pid) AS total_items
            FROM SellOrders s
            JOIN Products p ON s.pid = p.id
            JOIN Users u ON s.buyerid = u.id
            WHERE s.sellerid = :sellerid
        '''
        
        filters = {'sellerid': sellerid}
        
        if fulfilled is not None:
            query += ' AND s.fulfilled = :fulfilled'
            filters['fulfilled'] = fulfilled
        if start_date:
            query += ' AND s.time_ordered >= :start_date'
            filters['start_date'] = start_date
        if end_date:
            query += ' AND s.time_ordered <= :end_date'
            filters['end_date'] = end_date

        query += ' GROUP BY s.id, u.firstname, u.lastname, u.address ORDER BY s.time_ordered DESC'
        
        rows = app.db.execute(query, **filters)
        return [dict(row) for row in rows]

