from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address=None, account_balance=0.00, account_type='Buyer'):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.account_balance = account_balance
        self.account_type = account_type

    def get_by_auth(email, password):
        # Query to fetch the user by email
        rows = app.db.execute("""
        SELECT password, id, email, firstname, lastname
        FROM Users
        WHERE email = :email
        """, email=email)

        if not rows:  # Email not found
            return None

        # Fetch the hashed password from the database
        hashed_password = rows[0][0]

        # Validate the provided password against the stored hash
        if not check_password_hash(hashed_password, password):
            return None

        # Return a User object if the password is correct
        return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname)
VALUES(:email, :password, :firstname, :lastname)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname, address, account_balance, account_type
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None

    @staticmethod
    def get_name(id):
        rows = app.db.execute("""
        SELECT firstname, lastname
        FROM Users
        WHERE id = :id
        """, id = id)

        return (rows[0][0] + " " + rows[0][1]) if rows else None

