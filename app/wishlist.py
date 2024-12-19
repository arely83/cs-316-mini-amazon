from flask import redirect, url_for
from flask import jsonify
from flask import render_template
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.wishlist import WishlistItem
from flask import jsonify
from humanize import naturaltime
from flask import redirect, url_for

from flask import Blueprint
bp = Blueprint('wishlist', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/wishlist')
def wishlist():
    wishlistitems = None
    if current_user.is_authenticated:
        wishlistitems = WishlistItem.get_all_by_uid(current_user.id)
        
        # in render_template, you can specify a template HTML file (arg 1).
        # the variable on the left (wishlist_items) *within the template* is 
        # replaced by the data passed in.
        # Additionally, you can also specify functions to pass into the template. 
        return render_template('wishlist.html',
                                wishlist_items=wishlistitems,
                                humanize_time=humanize_time)
        return redirect(url_for('wishlist.wishlist'))


    else: 
        return jsonify({}), 404


@bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    if current_user.is_authenticated:

        WishlistItem.register(current_user.id, product_id, datetime.datetime.now())
        
        # this specifies both a flask blueprint (left wishlist, 
        # which is the name of the Python file in which it's defined)
        # and a route defined within that blueprint (right wishlist, 
        # corresponding to @bp.route('/wishlist').)
        return(redirect(url_for('wishlist.wishlist')))

    
    