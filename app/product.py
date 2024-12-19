
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime
from .models.product import Product
from .models.inventory import Inventory
from .models.review import Review
from flask import jsonify
from humanize import naturaltime
from flask import redirect, url_for
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

from flask import Blueprint
bp = Blueprint('product', __name__)
import os
from flask import current_app
from flask_login import login_required

# Define a route to get the products, with optional 'k'
@bp.route('/shop', methods=['GET'])
def get_all_or_top_k_products():
    # Extract filters and pagination parameters from the request
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('k', default=10, type=int)
    search = request.args.get('search', type=str)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    category = request.args.get('category', type=str)
    rating_min = request.args.get('rating_min', type=float)
    # Validate sort_by and order
    sort_by = request.args.get('sort_by', 'id')
    valid_sort_columns = {'id', 'name', 'price', 'category', 'avg_rating'}
    sort_by = sort_by if sort_by in valid_sort_columns else 'id'
    order = request.args.get('order', 'asc').lower()
    order = order if order in {'asc', 'desc'} else 'asc'
    # Calculate offset
    offset = (page - 1) * per_page
    # Fetch products
    products, avg_ratings = Product.get_filtered(
        search=search,
        min_price=min_price,
        max_price=max_price,
        category=category,
        rating_min=rating_min,
        sort_by=sort_by,
        order=order,
        available=True,
        k=per_page,
        offset=offset
    )
    # Fetch total product count for pagination
    total_products = Product.get_count(
        search=search,
        min_price=min_price,
        max_price=max_price,
        category=category,
        rating_min=rating_min,
        available=True
    )
    # Combine products and avg_ratings for rendering
    product_details = [
        {
            'product': product,
            'avg_rating': avg_rating,
            'review_count': Review.review_count(product.id)
        }
        for product, avg_rating in zip(products, avg_ratings)
    ]
    return render_template(
        'product.html',
        product_details=product_details,
        total_products=total_products,
        per_page=per_page,
        current_page=page,
        sort_by=sort_by,
        order=order
    )

# Define a route to get a single product by its id
@bp.route('/shop/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.get(id)
    if not product:
        return render_template('404.html'), 404

    # Fetch related products
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('k', default=5, type=int)
    offset = (page - 1) * per_page
    related_products = Product.get_related_products(
        category=product.category, 
        exclude_product_id=product.id, 
        k=per_page, 
        offset=offset
    )
    total_related = Product.get_count(category=product.category, available=True) - 1

    # Fetch inventory, reviews, etc., as before
    sellers = current_app.db.execute('''
        SELECT Inventory.sellerid, Users.firstname, Users.lastname, Inventory.quantity
        FROM Inventory
        JOIN Users ON Inventory.sellerid = Users.id
        WHERE Inventory.pid = :pid
    ''', pid=id)
    avg_rating = Review.avg_rating(id)
    review_number = Review.review_count(id)
    reviews = current_app.db.execute('''
        SELECT Reviews.rating, Reviews.details, Users.firstname, Users.lastname
        FROM Reviews
        JOIN Users ON Reviews.uid = Users.id
        WHERE Reviews.pid = :pid
    ''', pid=id)

    return render_template(
        'product_detail.html',
        product=product,
        sellers=sellers,
        avg_rating=avg_rating,
        reviews=reviews,
        review_number=review_number,
        user_authenticated=current_user.is_authenticated,
        related_products=related_products,
        total_related=total_related,
        current_page=page,
        per_page=per_page
    )

# Allowed extensions for image upload
ALLOWED_EXTENSIONS = {'jpeg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/product/new', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        category = request.form['category']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        sellerid = current_user.id

        # Check if a product with the same name exists
        existing_product = Product.get_by_name(name)
        if existing_product:
            return render_template(
                'create_product.html',
                existing_product_id=existing_product.id,
                existing_product_name=existing_product.name
            )

        # Create the product in the database
        product_id = Product.create(name, price, True, category, description, sellerid)
        Inventory.update(sellerid, product_id, name, quantity, datetime.datetime.now())

        # Handle image upload
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = f"{product_id}.jpeg"
            filepath = os.path.join(current_app.static_folder, 'css/images', filename)
            image.save(filepath)

        return redirect(url_for('product.get_product', id=product_id))

    return render_template('create_product.html')

@bp.route('/product/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.get(product_id)
    if not product or product.sellerid != current_user.id:
        flash("You are not authorized to edit this product.")
        return redirect(url_for('product.get_all_or_top_k_products'))
    if request.method == 'POST':
        # Update product fields
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.category = request.form['category']
        product.description = request.form['description']
        # Update the product in the database
        Product.update(product_id, product.name, product.price, product.category, product.description)
        # Handle updated image upload
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = f"{product_id}.jpeg"
            filepath = os.path.join(current_app.static_folder, 'css/images', filename)
            image.save(filepath)
        else:
            flash("No new image uploaded. Existing image will be retained.")
        flash("Product updated successfully!")
        return redirect(url_for('product.get_all_or_top_k_products'))
    return render_template('edit_product.html', product=product)
