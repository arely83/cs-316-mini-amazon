from flask import current_app as app


class Review:
    def __init__(self, id, pid, uid, rating, time_posted, details):
        self.id = id
        self.pid = pid
        self.uid = uid
        self.rating = rating
        self.time_posted = time_posted
        self.details = details
    
    # To get a review by the id (only one since id is unique)
    @staticmethod
    def get(id):
        rows = app.db.execute("""
        SELECT id, pid, uid, rating, time_posted, details
        FROM Reviews
        WHERE id = :id
        """, id = id)
        return Review(*(rows[0])) if rows is not None else None

    # Get a review by the pid, uid tuple (also unique since each user can only submit one review per product)
    @staticmethod
    def get_review(pid, uid):
        rows = app.db.execute("""
        SELECT id, pid, uid, rating, time_posted, details
        FROM Reviews
        WHERE pid = :pid AND uid = :uid
        """, pid = pid, uid = uid)
        return Review(*(rows[0])) if rows is not None else None

    # Check if a review exists in the database by the unique pid, uid tuple
    @staticmethod
    def review_exists(pid, uid):
        rows = app.db.execute("""
        SELECT pid, uid
        FROM Reviews
        WHERE pid = :pid AND uid = :uid
        """, pid = pid, uid = uid)
        return len(rows) == 1

    # Submit a new review into the database
    @staticmethod
    def submit_review(pid, uid, rating, time_posted, details):
        try:
            rows = app.db.execute("""
            INSERT INTO Reviews(pid, uid, rating, time_posted, details)
            VALUES(:pid, :uid, :rating, :time_posted, :details)
            RETURNING id
            """, pid = pid, uid = uid, rating = rating, time_posted = time_posted, details = details)
            id = rows[0][0]
            return Review.get(id)
        except Exception as e:
            print(str(e))
            return None

    # Update an already existing review in the database
    @staticmethod
    def update_review(pid, uid, rating, time_posted, details):
        rows = app.db.execute('''
        UPDATE Reviews
        SET rating = :rating,
            time_posted = :time_posted,
            details = :details
        WHERE pid = :pid AND uid = :uid
        RETURNING id
        ''', pid = pid, uid = uid, rating = rating, time_posted = time_posted, details = details)
        id = rows[0][0]
        return Review.get(id)
    
    # Delete a review from the database
    @staticmethod
    def delete_review(pid, uid):
        rows = app.db.execute('''
        DELETE FROM Reviews
        WHERE pid = :pid
        AND uid = :uid
        ''', pid = pid, uid = uid)
        return None

    # Get all the reviews authored by a user with id uid ordered by descending time
    @staticmethod
    def get_all_reviews_from_user(uid):
        rows = app.db.execute('''
        SELECT id, pid, uid, rating, time_posted, details
        FROM Reviews
        WHERE uid = :uid
        ORDER BY time_posted DESC
        ''', uid = uid)
        return [Review(*row) for row in rows]

    # Get the five most recent reviews authored by a user with id uid
    @staticmethod
    def get_five_recent_reviews_from_user(uid):
        rows = app.db.execute('''
        SELECT *
        FROM Reviews
        WHERE uid = :uid
        ORDER BY time_posted DESC
        OFFSET 0 ROWS
        FETCH NEXT 5 ROWS ONLY
        ''', uid = uid)
        return [Review(*row) for row in rows]

    # Get all of the reviews submitted for a product with id pid
    @staticmethod
    def get_all_reviews_from_product(pid):
        rows = app.db.execute('''
        SELECT id, pid, uid, rating, time_posted, details
        FROM Reviews
        WHERE pid = :pid
        ORDER BY time_posted DESC
        ''', pid = pid)
        return [Review(*row) for row in rows]

    # Get the five most recent reviews submitted for a product with id pid
    @staticmethod
    def get_five_recent_reviews_from_product(pid):
        rows = app.db.execute('''
        SELECT *
        FROM Reviews
        WHERE pid = :pid
        ORDER BY time_posted DESC
        OFFSET 0 ROWS
        FETCH NEXT 5 ROWS ONLY
        ''', pid = pid)
        return [Review(*row) for row in rows]

    # Get all the product reviews authored by a user with pageination implemented
    @staticmethod
    def user_reviews_in_pages(uid, offset, limit, sort_by, order):

        valid_columns = {'time_posted', 'rating'}
        if sort_by not in valid_columns:
            sort_by = 'time_posted'
        if order not in ['ASC', 'DESC']:
            order = 'DESC'

        rows = app.db.execute(f'''
        SELECT *
        FROM Reviews
        WHERE uid = :uid
        ORDER BY {sort_by} {order}
        LIMIT :limit OFFSET :offset;
        ''', uid = uid, offset = offset, limit = limit)
        return [Review(*row) for row in rows]

    # Get all the reviews submitted for a product with pageination implemented
    @staticmethod
    def product_reviews_in_pages(pid, offset, limit, sort_by, order):
        rows = app.db.execute(f'''
        SELECT *
        FROM Reviews
        WHERE pid = :pid
        ORDER BY {sort_by} {order}
        LIMIT :limit OFFSET :offset;
        ''', pid = pid, offset = offset, limit = limit)
        return [Review(*row) for row in rows]

    # Get the average rating for a product
    @staticmethod
    def avg_rating(productID):
        rows = app.db.execute('''
        SELECT COALESCE(AVG(rating), 0)
        FROM Reviews
        WHERE pid = :productID;
        ''', productID = productID)
        return rows[0][0] if len(rows) > 0 else None

    # Get the number of reviews for a product
    @staticmethod
    def review_count(productID):
        rows = app.db.execute( '''
        SELECT COUNT(*)
        FROM Reviews
        WHERE pid = :productID;
        ''', productID = productID)
        return rows[0][0] if len(rows) > 0 else None

    # Sort the reviews by date added
    @staticmethod
    def time_sort(order):
        if order not in ['ASC', 'DESC']:
            order = 'ASC'
        rows = app.db.execute(f'''
        SELECT *
        FROM Reviews
        ORDER BY time_posted {order};
        ''')
        return [Review(*row) for row in rows]



class Seller_Review:
    def __init__(self, id, sid, uid, rating, time_posted, details):
        self.id = id
        self.sid = sid
        self.uid = uid
        self.rating = rating
        self.time_posted = time_posted
        self.details = details

    # To get a seller review by the id (only one since id is unique)
    @staticmethod
    def get(id):
        rows = app.db.execute("""
        SELECT id, sid, uid, rating, time_posted, details
        FROM SellerReviews
        WHERE id = :id
        """, id = id)
        return Seller_Review(*(rows[0])) if rows is not None else None

    # Get a review by the sid, uid tuple (also unique since each user can only submit one review per seller)
    @staticmethod
    def get_review(sid, uid):
        rows = app.db.execute("""
        SELECT id, sid, uid, rating, time_posted, details
        FROM SellerReviews
        WHERE sid = :sid AND uid = :uid
        """, sid = sid, uid = uid)
        return Seller_Review(*(rows[0])) if rows is not None else None

    # Check if a review exists in the database by the unique pid, uid tuple
    @staticmethod
    def review_exists(sid, uid):
        rows = app.db.execute("""
        SELECT sid, uid
        FROM SellerReviews
        WHERE sid = :sid AND uid = :uid
        """, sid = sid, uid = uid)
        return len(rows) == 1

    # Check if the user has bought something from the seller
    @staticmethod
    def from_seller(uid):
        rows = app.db.execute("""
        SELECT COUNT(*)
        FROM Purchases p
        JOIN Products pro ON p.pid = pro.id
        WHERE p.uid = :uid
        """, uid = uid)
        return len(rows) != 0

    # Submit a new review into the database
    @staticmethod
    def submit_review(sid, uid, rating, time_posted, details):
        try:
            rows = app.db.execute("""
            INSERT INTO SellerReviews(sid, uid, rating, time_posted, details)
            VALUES(:sid, :uid, :rating, :time_posted, :details)
            RETURNING id
            """, sid = sid, uid = uid, rating = rating, time_posted = time_posted, details = details)
            id = rows[0][0]
            return Seller_Review.get(id)
        except Exception as e:
            print(str(e))
            return None

    # Update an already existing review in the database
    @staticmethod
    def update_review(sid, uid, rating, time_posted, details):
        rows = app.db.execute('''
        UPDATE SellerReviews
        SET rating = :rating,
            time_posted = :time_posted,
            details = :details
        WHERE sid = :sid AND uid = :uid
        RETURNING id
        ''', sid = sid, uid = uid, rating = rating, time_posted = time_posted, details = details)
        id = rows[0][0]
        return Seller_Review.get(id)

    # Delete a review from the database
    @staticmethod
    def delete_review(sid, uid):
        rows = app.db.execute('''
        DELETE FROM SellerReviews
        WHERE sid = :sid
        AND uid = :uid
        ''', sid = sid, uid = uid)
        return None

    # Get all the seller reviews authored by a user with id uid ordered by descending time
    @staticmethod
    def get_all_reviews_from_user(uid):
        rows = app.db.execute('''
        SELECT id, sid, uid, rating, time_posted, details
        FROM SellerReviews
        WHERE uid = :uid
        ORDER BY time_posted DESC
        ''', uid = uid)
        return [Seller_Review(*row) for row in rows]

    # Get all of the reviews submitted for a seller with id sid
    @staticmethod
    def get_all_reviews_from_seller(sid):
        rows = app.db.execute('''
        SELECT id, sid, uid, rating, time_posted, details
        FROM SellerReviews
        WHERE sid = :sid
        ORDER BY time_posted DESC
        ''', sid = sid)
        return [Seller_Review(*row) for row in rows]

    # Get all the seller reviews authored by a user with pageination implemented
    @staticmethod
    def user_reviews_in_pages(uid, offset, limit, sort_by, order):
        rows = app.db.execute(f'''
        SELECT *
        FROM SellerReviews
        WHERE uid = :uid
        ORDER BY {sort_by} {order}
        LIMIT :limit OFFSET :offset;
        ''', uid = uid, offset = offset, limit = limit)
        return [Seller_Review(*row) for row in rows]

    # Get all the reviews submitted for a product with pageination implemented
    @staticmethod
    def seller_reviews_in_pages(sid, offset, limit):
        rows = app.db.execute('''
        SELECT *
        FROM SellerReviews
        WHERE sid = :sid
        ORDER BY time_posted DESC
        LIMIT :limit OFFSET :offset;
        ''', sid = sid, offset = offset, limit = limit)
        return [Seller_Review(*row) for row in rows]

    # Get the average rating for a seller
    @staticmethod
    def avg_rating(sellerID):
        rows = app.db.execute('''
        SELECT COALESCE(AVG(rating), 0)
        FROM SellerReviews
        WHERE sid = :sellerID;
        ''', sellerID = sellerID)
        return rows[0][0] if len(rows) > 0 else None

    # Get the number of reviews for a seller
    def review_count(sellerID):
        rows = app.db.execute( '''
        SELECT COUNT(*)
        FROM SellerReviews
        WHERE sid = :sellerID;
        ''', sellerID = sellerID)
        return rows[0][0] if len(rows) > 0 else None