from flask import current_app as app


class Order:
    def __init__(self, id, uid, pid, time_ordered):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_ordered = time_ordered

    @staticmethod
    def get(id):
        rows = app.db.execute('''
        SELECT id, uid, pid, time_added
        FROM Orders
        WHERE id = :id
        ''',
                              id=id)
        return Order(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
        SELECT id, uid, pid, time_added
        FROM Orders
        WHERE uid = :uid
        AND time_purchased >= :since
        ORDER BY time_added DESC
        ''',
                              uid=uid,
                              since=since)
        return [Order(*row) for row in rows]

    @staticmethod
    def get_user_orders(uid):
        rows = app.db.execute("""
        SELECT id, uid, pid, time_added
        FROM Orders
        WHERE uid = :uid
        ORDER BY time_added DESC
        """,
                uid=uid)
        return [Order(*(row)) for row in rows]

    
    @staticmethod
    def register(uid, pid, time_added):
        try:
            rows = app.db.execute("""
            INSERT INTO Orders(uid, pid, time_added)
            VALUES(:uid, :pid, :time_added)
            RETURNING id
            """,
                                  uid=uid,
                                  pid=pid,
                                  time_added=time_added)
            id = rows[0][0]
            return Order.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

