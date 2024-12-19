from flask import current_app as app

class WishlistItem:
    def __init__(self, id, uid, pid, product_name, time_added):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.product_name = product_name
        self.time_added = time_added

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_added
FROM Wishlist
WHERE id = :id
''',
                              id=id)
        return WishlistItem(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_added
FROM Wishlist
WHERE uid = :uid
AND time_added >= :since
ORDER BY time_added DESC
''',
                              uid=uid,
                              since=since)
        return [WishlistItem(*row) for row in rows]

    @staticmethod
    def register(uid, pid, time_added):
        try:
            rows = app.db.execute("""
INSERT INTO Wishlist(uid, pid, time_added)
VALUES(:uid, :pid, :time_added)
RETURNING id
""",
                                  uid=uid,
                                  pid=pid,
                                  time_added=time_added)
            id = rows[0][0]
            return Wishlist.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None


    
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT w.id, w.uid, w.pid, p.name AS product_name, w.time_added
FROM Wishlist w
JOIN Products p on p.id = w.pid
WHERE uid = :uid
ORDER BY time_added DESC
''',
                              uid=uid)
        return [WishlistItem(*row) for row in rows]


    @staticmethod
    def get_all_by_id(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_added
FROM Wishlist
WHERE id = :id
ORDER BY time_added DESC
''',
                              id=id)
        return [WishlistItem(*row) for row in rows]
        

    @staticmethod
    def get_all():
        rows = app.db.execute('''
SELECT id, uid, pid, time_added
FROM Wishlist
ORDER BY time_added DESC
''',
                              )
        return [WishlistItem(*row) for row in rows]
