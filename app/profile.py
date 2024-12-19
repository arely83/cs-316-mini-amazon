from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask import jsonify
from werkzeug.security import generate_password_hash
from decimal import Decimal


from .models.user import User
from flask import current_app
from .db import DB



from flask import Blueprint
bp = Blueprint('myprofile', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/myprofile')
def profile():
    if current_user.is_authenticated:
        # Fetch the latest user data from the database
        sql_query = "SELECT firstname, lastname, email, address, account_balance, account_type FROM Users WHERE id = :user_id"
        result = current_app.db.execute(sql_query, user_id=current_user.id)
        
        # Check if the user exists in the database and fetch the data
        if result:
            user_data = result[0]
            firstname, lastname, email, address, account_balance, account_type = user_data
        else:
            flash("User not found", "error")
            return redirect(url_for('users.login'))  # Or some other error handling
        
        # Prepare profile info to be passed to the template
        profile_info = {
            "id": current_user.id,
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "address": address,
            "account_balance": account_balance,
            "account_type": account_type
        }
        
        # Render the profile template with updated profile info
        return render_template('profile.html', profile_info=profile_info)
    else: 
        return jsonify({"error": "User not authenticated"}), 404

    
@bp.route('/add-money', methods=['POST'])
def add_money():
    uid = current_user.id
    if current_user.is_authenticated:

        profile_info = {
            "id": current_user.id,
            "firstname": current_user.firstname,
            "lastname": current_user.lastname,
            "email": current_user.email,
            "address": current_user.address,
            "account_balance": current_user.account_balance
        }

        amount = float(request.form['amount'])

        if amount < 0:
            flash("Cannot add a negative amount", 'error')
            return redirect(url_for('myprofile.profile'))

        sql_update_balance = """
        UPDATE Users
        SET account_balance = account_balance + :amount
        WHERE id = :user_id
        """
        current_app.db.execute(sql_update_balance, amount=amount, user_id=uid)
        flash(f'${amount:.2f} has been added to your account!', 'success')

    return redirect(url_for('myprofile.profile'))


@bp.route('/withdraw_money', methods=['POST'])
def withdraw_money():
    uid = current_user.id
    if current_user.is_authenticated:

        profile_info = {
            "id": current_user.id,
            "firstname": current_user.firstname,
            "lastname": current_user.lastname,
            "email": current_user.email,
            "address": current_user.address,
            "account_balance": current_user.account_balance
        }

        amount = Decimal(request.form['withdraw'])

        if amount < 0:
            flash("Cannot withdraw a negative amount", 'error')
            return redirect(url_for('myprofile.profile'))

        if current_user.account_balance - amount < 0:
            flash("Unable to withdraw - insufficient funds", 'error')
            return redirect(url_for('myprofile.profile'))

        sql_update_balance = """
        UPDATE Users
        SET account_balance = account_balance - :amount
        WHERE id = :user_id
        """
        current_app.db.execute(sql_update_balance, amount=amount, user_id=uid)
        flash(f'${amount:.2f} has been withdrawn!', 'success')

    return redirect(url_for('myprofile.profile'))


@bp.route('/update-profile', methods=['POST'])
def update_profile():
    if current_user.is_authenticated:
        # Get the current user ID
        uid = current_user.id

        # Get the updated data from the form
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        account_type = request.form['account_type']
        
        # Validate email for uniqueness
        if User.email_exists(email) and email != current_user.email:
            flash("This email is already in use by another user.", "error")
            return redirect(url_for('myprofile.profile'))

        password = request.form['password']
        address = request.form['address']

        # If password is provided, hash it
        if password:
            password = generate_password_hash(password)

        # Prepare the SQL query to update the user's information
        sql_update = """
        UPDATE Users
        SET firstname = :firstname, lastname = :lastname, email = :email, password = :password, address = :address, account_type = :account_type
        WHERE id = :user_id
        """

        
        # Execute the query to update user data
        current_app.db.execute(sql_update, firstname=firstname, lastname=lastname, email=email, password=password, address=address, account_type=account_type, user_id=uid)
        
        # Flash a success message
        flash("Profile updated successfully!", "success")

        # Redirect back to the profile page
        return redirect(url_for('myprofile.profile'))  # Redirect back to the profile page
    
    else:
        return jsonify({"error": "User not authenticated"}), 404