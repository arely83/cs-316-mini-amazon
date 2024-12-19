from flask import render_template, flash, request, session
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from flask import redirect, url_for
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.wishlist import WishlistItem
from .models.review import Review
from .models.review import Seller_Review
from .models.user import User
from .models.sellorder import SellOrder
from humanize import naturaltime
from flask import jsonify

from flask import Blueprint
bp = Blueprint('reviews', __name__)


def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

# Lists the reviews for a product
@bp.route('/shop/<int:product_id>/product_reviews', methods = ['GET', 'POST'])
def get_product_reviews(product_id):
    reviews = None

    if Product.get(product_id):
        page_number = request.args.get('page_number', 1, type = int)
        per_page = 10
        offset = (page_number - 1) * per_page

        sort_by = request.args.get('sort_by', 'time_posted')
        order = request.args.get('order', 'DESC').upper()

        reviews = Review.product_reviews_in_pages(product_id, offset, per_page, sort_by, order)

        return render_template('product_reviews.html', reviews = reviews, page_number = page_number, humanize_time = humanize_time, product_id = product_id, Product = Product, sort_by=sort_by, order=order)

    else:
        return jsonify({}), 404

# Lists the reviews for products authored by a user
@bp.route('/<int:user_id>/user_reviews', methods = ['GET'])
def get_user_reviews(user_id):
    reviews = None

    if User.get(user_id):
        page_number = request.args.get('page_number', 1, type = int)
        per_page = 10
        offset = (page_number - 1) * per_page 

        sort_by = request.args.get('sort_by', 'time_posted')
        order = request.args.get('order', 'DESC').upper()

        reviews = Review.user_reviews_in_pages(user_id, offset, per_page, sort_by, order)

        return render_template('user_reviews.html', reviews = reviews, page_number = page_number, humanize_time = humanize_time, sort_by = sort_by, order = order, User = User)

    else:
        return jsonify({}), 404

# Page for the current authorized user's product reviews
@bp.route('/myproductreviews', methods = ['GET', 'POST'])
def get_current_user_reviews():
    reviews = None
    if current_user.is_authenticated:

        page_number = request.args.get('page_number', 1, type = int)
        per_page = 10
        offset = (page_number - 1) * per_page

        sort_by = request.args.get('sort_by', 'time_posted')
        order = request.args.get('order', 'DESC').upper()

        reviews = Review.user_reviews_in_pages(current_user.id, offset, per_page, sort_by, order)

        return render_template('reviews.html', reviews = reviews, page_number = page_number, humanize_time = humanize_time, Product = Product, sort_by = sort_by, order = order)
    
    else:
        return jsonify({}), 404

# Page for the current authorized user's seller reviews
@bp.route('/mysellerreviews', methods = ['GET', 'POST'])
def get_current_user_reviews_s():
    reviews = None
    if current_user.is_authenticated:

        page_number = request.args.get('page_number', 1, type = int)
        per_page = 10
        offset = (page_number - 1) * per_page

        sort_by = request.args.get('sort_by', 'time_posted')
        order = request.args.get('order', 'DESC').upper()

        reviews = Seller_Review.user_reviews_in_pages(current_user.id, offset, per_page, sort_by, order)

        return render_template('s_reviews.html', reviews = reviews, page_number = page_number, humanize_time = humanize_time, Product = Product, User = User, sort_by = sort_by, order = order)
    
    else:
        return jsonify({}), 404

# Form for submitting reviews
class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators = [DataRequired(), NumberRange(min=1, max=5)])
    details = StringField('Review', validators = [DataRequired()])
    submit = SubmitField('Submit')

# Link for submitting a new review for a product
@bp.route('/<int:product_id>/submit_review', methods = ["GET", "POST"])
def submit(product_id):
    if Review.review_exists(product_id, current_user.id):
        flash("You have already submitted a review for this product.")
        return redirect("/myproductreviews")
    else:
        form = ReviewForm()
        if form.validate_on_submit():
            if Review.submit_review(product_id,
                                    current_user.id,
                                    form.rating.data,
                                    datetime.datetime.now(), 
                                    form.details.data):
                flash('Review submitted.')
                return redirect("/myproductreviews")
        return render_template("rate_product.html", title = "Review", form = form, product_id = product_id, humanize_time = humanize_time)

# Link for updating an already existing review for a product
@bp.route('/<int:product_id>/my_review', methods = ["GET", "POST"])
def update(product_id):
    review = Review.get_review(product_id, current_user.id)

    if not review:
        flash("You have not reviewed this product.")
        return redirect('/')

    form = ReviewForm(obj = review)

    if form.validate_on_submit():
        if Review.update_review(product_id,
                                current_user.id,
                                form.rating.data,
                                datetime.datetime.now(),
                                form.details.data):
            flash("Review updated.")
            return redirect("/myproductreviews")

    return render_template("update_review.html", form = form, product_id = product_id, humanize_time = humanize_time)

# Link for deleting a review for a product
@bp.route('/delete_review/<int:product_id>', methods = ["POST"])
def delete(product_id):
    
    deleted = Review.delete_review(product_id, current_user.id)

    flash("Review deleted.")
    
    return redirect("/myproductreviews")

# Lists the reviews for a seller
@bp.route('/<int:seller_id>/seller_reviews', methods = ['GET', 'POST'])
def get_seller_reviews(seller_id):
    reviews = None

    if User.get(seller_id):
        page_number = request.args.get('page_number', 1, type = int)
        per_page = 10
        offset = (page_number - 1) * per_page
        reviews = Seller_Review.seller_reviews_in_pages(seller_id, offset, per_page)

        return render_template('seller_reviews.html', reviews = reviews, page_number = page_number, humanize_time = humanize_time, seller_id = seller_id, User = User)

    else:
        return jsonify({}), 404

# Lists the reviews for sellers authored by a user
@bp.route('/<int:user_id>/user_reviews_s', methods = ['GET'])
def get_user_reviews_s(user_id):
    reviews = None

    if User.get(user_id):
        page_number = request.args.get('page_number', 1, type = int)
        per_page = 10
        offset = (page_number - 1) * per_page

        sort_by = request.args.get('sort_by', 'time_posted')
        order = request.args.get('order', 'DESC').upper()

        reviews = Seller_Review.user_reviews_in_pages(user_id, offset, per_page, sort_by, order)

        return render_template('user_reviews_s.html', reviews = reviews, page_number = page_number, humanize_time = humanize_time, User = User, sort_by = sort_by, order = order, user_id = user_id)

    else:
        return jsonify({}), 404

# Link for submitting a new review for a seller
@bp.route('/<int:seller_id>/submit_review_seller', methods = ["GET", "POST"])
def submit_seller(seller_id):
    if Seller_Review.review_exists(seller_id, current_user.id):
        flash("You have already submitted a review for this seller.")
        return redirect("/mysellerreviews")
    else:
        if Seller_Review.from_seller(current_user.id):
            flash("You must purchase something from this seller to review them.")
            return redirect("/mysellerreviews")
        else:
            form = ReviewForm()
            if form.validate_on_submit():
                if Seller_Review.submit_review(seller_id,
                                    current_user.id,
                                    form.rating.data,
                                    datetime.datetime.now(), 
                                    form.details.data):
                    flash('Review submitted.')
                    return redirect("/mysellerreviews")
            return render_template("rate_seller.html", title = "Review", form = form, seller_id = seller_id, humanize_time = humanize_time)

# Link for updating an already existing review for a seller
@bp.route('/<int:seller_id>/my_review_seller', methods = ["GET", "POST"])
def update_seller(seller_id):
    review = Seller_Review.get_review(seller_id, current_user.id)

    if not review:
        flash("You have not reviewed this seller.")
        return redirect('/')

    form = ReviewForm(obj = review)

    if form.validate_on_submit():
        if Seller_Review.update_review(seller_id,
                                current_user.id,
                                form.rating.data,
                                datetime.datetime.now(),
                                form.details.data):
            flash("Review updated.")
            return redirect("/mysellerreviews")

    return render_template("update_seller_review.html", form = form, seller_id = seller_id, humanize_time = humanize_time)

# Link for deleting a review for a seller
@bp.route('/delete_review_s/<int:seller_id>', methods = ["POST"])
def delete_seller(seller_id):
    
    deleted = Seller_Review.delete_review(seller_id, current_user.id)

    flash("Review deleted.")
    
    return redirect("/mysellerreviews")

