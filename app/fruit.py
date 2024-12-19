from flask import jsonify, redirect, url_for
from flask_login import current_user
from flask import render_template

from .models.fruit import Fruit

from flask import Blueprint
bp = Blueprint('fruit', __name__)

# Main fruit page where user can see all of the previous fruits
@bp.route('/fruit')
def fruit():
    # If not logged in
    if not current_user.is_authenticated:
        return redirect(url_for('users.login')) # send to login.page
    
    uid = current_user.id
    rows = Fruit.get_display_data(uid)  

    return render_template('fruit.html', in_fruit=rows)


# Indirect fruit page displaying only fruits in specific date given
# Used to redirect user from purchases page
@bp.route('/fruit/<date>')
def fruit_by_date(date):
    # If not logged in
    if not current_user.is_authenticated:
        return redirect(url_for('users.login')) # send to login.page
    
    uid = current_user.id

    # date should be in 'YYYY-MM-DD' format.
    rows = Fruit.get_by_date(uid, date)
    
    return render_template('fruit.html', in_fruit=rows)

