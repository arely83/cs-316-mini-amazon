from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.review import Seller_Review
from .models.review import Review
from .db import DB
from flask import current_app
from humanize import naturaltime
import datetime


from flask import Blueprint
bp = Blueprint('users', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/delete-account', methods=['POST'])
def delete_account():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))

    sql_delete_carts = "DELETE FROM carts WHERE uid = :user_id"
    current_app.db.execute(sql_delete_carts, user_id=current_user.id)

    sql_delete_inventory = "DELETE FROM fruits WHERE uid = :user_id"
    current_app.db.execute(sql_delete_inventory, user_id=current_user.id)
    
    sql_delete_sellorders = "DELETE FROM sellorders WHERE buyerid = :user_id"
    current_app.db.execute(sql_delete_sellorders, user_id=current_user.id)
    
    sql_delete_wishlist = "DELETE FROM wishlist WHERE uid = :user_id"
    current_app.db.execute(sql_delete_wishlist, user_id=current_user.id)

    sql_delete_purchases = "DELETE FROM purchases WHERE uid = :user_id"
    current_app.db.execute(sql_delete_purchases, user_id=current_user.id)

    sql_delete_reviews = "DELETE FROM reviews WHERE uid = :user_id"
    current_app.db.execute(sql_delete_reviews, user_id=current_user.id)

    sql_delete_inventory = "DELETE FROM inventory WHERE sellerid = :user_id"
    current_app.db.execute(sql_delete_inventory, user_id=current_user.id)

    sql_delete_products = "DELETE FROM products WHERE sellerid = :user_id"
    current_app.db.execute(sql_delete_products, user_id=current_user.id)

    

    sql_delete_user = "DELETE FROM Users WHERE id = :user_id"
    current_app.db.execute(sql_delete_user, user_id=current_user.id)

    logout_user()
    return redirect(url_for('users.account_deleted'))

@bp.route('/account-deleted')
def account_deleted():
    return render_template('account_deleted.html')


@bp.route('/user/<int:uid>')
def public_user(uid):
    user = User.get(uid)
    reviews = None

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.account_type == 'Seller':
        reviews = Seller_Review.get_all_reviews_from_seller(user.id)

    return render_template('publicUser.html', user=user, reviews=reviews, humanize_time=humanize_time)
