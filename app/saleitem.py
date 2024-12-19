from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
import datetime

from .models.saleitem import SaleItem
from flask import jsonify
from humanize import naturaltime
from flask import redirect, url_for

from werkzeug.urls import url_parse
from flask_wtf import FlaskForm


from flask import Blueprint
bp = Blueprint('saleitem', __name__)

def humanize_time(dt):
    return naturaltime(datetime.datetime.now() - dt)

@bp.route('/saleorders')
def get_sales():
    saleitems = None
    if current_user.is_authenticated:

        saleitems = SaleItem.get_solditems(current_user.id)
        
        return render_template('saleitems.html',
                                humanize_time=humanize_time)
    else: 
        return jsonify({}), 404
