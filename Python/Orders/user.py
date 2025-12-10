from flask import Blueprint, request, flash, redirect, url_for, render_template, session
from flask_login import login_user
from models import db, User, Basket, LoginToken
import secrets
from datetime import datetime, timedelta
from flask_mail import Message

user_bp = Blueprint('user', __name__)

def send_login_link(email, token):
    from app import mail
    login_url = url_for('user.verify_login', token=token, _external=True)
    msg = Message("Your login link", recipients=[email])
    msg.body = f"Click here to log in: {login_url}"
    try:
        mail.send(msg)
    except Exception as e:
        print("Email send failed:", e)

@user_bp.route('/verify/<token>')
def verify_login(token):
    login_token = LoginToken.query.filter_by(token=token).first()
    if not login_token or login_token.expires_at < datetime.utcnow():
        flash("Invalid or expired login link.")
        return redirect(url_for('user.start_login'))
    
    #Create user

    user = User.query.filter_by(email=login_token.email).first()
    if not user:
        user = User(email=login_token.email)
        db.session.add(user)
        db.session.commit()


    #Transfer basket

    basket = session.get('basket', {})
    for item_id_str, quantity in basket.items():
        item_id = int(item_id_str)
        existing = Basket.query.filter_by(user_id=user.id, item_id=item_id).first()
        if existing:
            existing.quantity += quantity
        else:
            db.session.add(Basket(user_id=user.id, item_id=item_id, quantity=quantity))
    
    db.session.commit()
    session.pop('basket', None)

    login_user(user)

    #Delete token on use

    db.session.delete(login_token)
    db.session.commit()

    return redirect(url_for('admin.dashboard' if user.has_role == "admin" else 'menu'))

@user_bp.route('/start-login', methods=['POST', 'GET'])
def start_login():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form.get('email')
    if not email:
        flash("Email is required")
        return redirect(url_for('user.start_login'))
    
    #Create login token

    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(minutes=10)

    login_token = LoginToken(email=email, token=token, expires_at=expires)
    db.session.add(login_token)
    db.session.commit()

    send_login_link(email, token)
    flash("Check your email for a login link.")
    return redirect(url_for('user.start_login'))