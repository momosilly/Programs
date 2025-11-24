from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, flash,  url_for, redirect, session
from datetime import datetime
from flask_login import login_required, current_user, logout_user, LoginManager
from models import db, Basket, Item, Order
from admin import admin_bp
from user import user_bp, User
from flask_mail import Mail
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SECRET_KEY'] = 'mypassowrd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/orders'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

db.init_app(app)
app.register_blueprint(admin_bp)
migrate = Migrate(app, db)

@app.route('/menu', methods=['POST', 'GET'])
def menu():
    items = Item.query.all()
    basket = session.get('basket', {})
    basket_items = []

    for item_id_str, quantity in basket.items():
        item = Item.query.get(int(item_id_str))
        if item:
            item.quantity = quantity
            
            basket_items.append(item)
    return render_template('menu.html', items=items, basket=basket, basket_items=basket_items)

@app.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket(item_id):
    item = Item.query.get_or_404(item_id)
    
    basket = session.get('basket', {})

    item_id_str = str(item_id)
    if item_id_str in basket:
        basket[item_id_str] += 1
        flash(f"{item.name} added to basket!")
    else:
        basket[item_id_str] = 1
    
    session['basket'] = basket
    return redirect(url_for('menu'))

@app.route('/basket')
def view_basket():
    basket = session.get('basket', {})
    basket_items = []

    for item_id_str, quantity in basket.items():
        item = Item.query.get(int(item_id_str))
        if item:
            basket_items.append({
                'name': item.name,
                'price': item.price,
                'quantity': quantity
            })
    redirect(url_for('menu'))

@app.route('/increase_quantity/<int:item_id>', methods=['POST'])
def increase_quantity(item_id):
    basket = session.get('basket', {})
    item_id_str = str(item_id)
    if item_id_str in basket:
        basket[item_id_str] += 1
    session['basket'] = basket
    return redirect(url_for('menu'))

@app.route('/decrease_quantity/<int:item_id>', methods=['POST'])
def decrease_quantity(item_id):
    basket = session.get('basket', {})
    item_id_str = str(item_id)
    if item_id_str in basket:
        basket[item_id_str] -= 1
        if basket[item_id_str] <= 0:
            del basket[item_id_str]
    session['basket'] = basket
    return redirect(url_for('menu'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    basket_items = Basket.query.filter_by(user_id=current_user.id).all()
    for item in basket_items:
        order = Order(user_id=current_user.id, item_id=item.item_id)
        db.session.add(order)
        db.session.delete(item)

    db.session.commit()
    flash("Order placed successfully!")
    return redirect(url_for('menu'))

login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.init_app(app)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(user_bp)

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

if __name__ == '__main__':
    app.run(debug=True)