# init.py

from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'

from flask import Blueprint
bp = Blueprint('users', __name__)



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .wishlist import bp as wishlist_bp
    app.register_blueprint(wishlist_bp)

    from .purchase import bp as purchase_bp
    app.register_blueprint(purchase_bp)

    from .product import bp as product_bp
    app.register_blueprint(product_bp)
    
    from .sellorders import bp as sellorder_bp
    app.register_blueprint(sellorder_bp)

    from .saleitem import bp as saleitem_bp
    app.register_blueprint(saleitem_bp)

    from .reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp)

    from .carts import bp as carts_bp
    app.register_blueprint(carts_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .profile import bp as profile_bp
    app.register_blueprint(profile_bp)

    from .fruit import bp as fruit_bp
    app.register_blueprint(fruit_bp)
    

    return app
