from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from flask_login import LoginManager, login_user
from models import db, User, Basket

user_bp = Blueprint('user', __name__)

@user_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_email:
            flash("An accounnt with this email already exists. Please try another one.")
            return redirect(url_for('user.signup'))
        
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created! You can now log in.')
        return redirect(url_for('user.login'))
    return render_template('signup.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user is None:
            flash('No account found with this email.')
            return redirect(url_for('user.login'))
        
        if user.check_password(password):
            login_user(user)

            #Transfer session basket to database
            basket = session.get('basket', {})
            for item_id_str, quantity in basket.items():
                item_id = int(item_id_str)
                existing = Basket.query.filter_by(user_id=user.id, item_id=item_id).first()
                if existing:
                    existing.quantity += quantity
                else:
                    new_item = Basket(user_id=user.id, item_id=item_id, quantity=quantity)
                    db.session.add(new_item)
            db.session.commit()
            session.pop('basket', None)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('menu'))
        else:
            flash("Incorrect password. Please try again")
            return redirect(url_for('user.login'))
        
    return render_template('login.html')
