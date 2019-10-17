from flask import Blueprint, render_template, redirect, url_for, flash
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from ..services.user_services import register_user
from ..services.transaction_services import get_user_insights
from ..constants import RETAILER, SUPPLIER, COURIER


home = Blueprint('home', __name__)


@home.route('/')
@login_required
def dashboard():
    initiated_tx = get_user_insights(current_user)
    return render_template('home/index.html', title='Dashboard', number=initiated_tx)


@home.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('home.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home.dashboard'))
    return render_template('home/login.html', form=form)


@home.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.login'))


@home.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.dashboard'))
    form = RegistrationForm()
    roles = [RETAILER, SUPPLIER, COURIER]
    form.user_role.choices = [(x, x) for x in roles]
    if form.validate_on_submit():
        register_user(form)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('home.login'))
    return render_template('home/register.html', title='Register', form=form)
