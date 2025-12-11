from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, render_template, flash,  url_for, redirect, session, jsonify, request
from datetime import datetime
from flask_login import login_required, current_user, logout_user, LoginManager
from models import db, Basket, Item, Order, LoginToken, OrderItem, Address, OrderStatus
from admin import admin_bp
from delivery import delivery_bp
from user import user_bp, User
from flask_mail import Mail
import os
from dotenv import load_dotenv
import re


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
app.register_blueprint(delivery_bp)
migrate = Migrate(app, db)

def build_from_session(basket_dict):
    items = []
    for item_id_str, quantity in basket_dict.items():
        item = item.query.get(int(item_id_str))
        if item:
            items.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'quantity': quantity
            })
    return items

@app.route('/menu', methods=['POST', 'GET'])
def menu():
    items = Item.query.all()
    basket = session.get('basket', {})
    basket_items = []

    if current_user.is_authenticated:
        basket_items = Basket.query.filter_by(user_id=current_user.id).all()
    else:
        basket_items = build_from_session(session.get('basket', {}))

    for item_id_str, quantity in basket.items():
        item = Item.query.get(int(item_id_str))
        if item:
            item.quantity = quantity
            basket_items.append(item)
    return render_template('menu.html', items=items, basket=basket, basket_items=basket_items)

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

@app.route('/add_to_basket/<int:item_id>', methods=['POST'])
def add_to_basket(item_id):
    item = Item.query.get_or_404(item_id)

    if current_user.is_authenticated:
        # Update basket in DB
        existing = Basket.query.filter_by(user_id=current_user.id, item_id=item_id).first()
        if existing:
            existing.quantity += 1
        else:
            basket_item = Basket(user_id=current_user.id, item_id=item_id, quantity=1)
            db.session.add(basket_item)
            existing = basket_item
        db.session.commit()

        return jsonify({
            'success': True,
            'item_id': item_id,
            'quantity': existing.quantity,
            'name': item.name,
            'price': item.price
        })

    else:
        # Update basket in session
        basket = session.get('basket', {})
        item_id_str = str(item_id)
        if item_id_str in basket:
            basket[item_id_str] += 1
        else:
            basket[item_id_str] = 1

        session['basket'] = basket

        return jsonify({
            'success': True,
            'item_id': item_id,
            'quantity': basket[item_id_str],
            'name': item.name,
            'price': item.price
        })

@app.route('/increase_quantity/<int:item_id>', methods=['POST'])
def increase_quantity(item_id):
    if current_user.is_authenticated:
        basket_item = Basket.query.filter_by(user_id=current_user.id, item_id=item_id).first()
        if basket_item:
            basket_item.quantity += 1
            db.session.commit()
            return jsonify({'quantity': basket_item.quantity})
    else:
        basket = session.get('basket', {})
        item_id_str = str(item_id)
        if item_id_str in basket:
            basket[item_id_str] += 1
        session['basket'] = basket

        return jsonify({
            'success': True,
            'item_id': item_id,
            'quantity': basket[item_id_str]
        })

@app.route('/decrease_quantity/<int:item_id>', methods=['POST'])
def decrease_quantity(item_id):
    basket = session.get('basket', {})
    item_id_str = str(item_id)
    quantity = 0

    if current_user.is_authenticated:
        basket_item = Basket.query.filter_by(user_id=current_user.id, item_id=item_id).first()
        if basket_item:
            basket_item.quantity -= 1
            if basket_item.quantity <= 0:
                #Delete item
                db.session.delete(basket_item)
                db.session.commit()
                return jsonify({'quantity': 0})
            
            db.session.commit()
            return jsonify({'quantity': basket_item.quantity})
        else:
            return jsonify({'quantity': 0})
    else:
        if item_id_str in basket:
            basket[item_id_str] -= 1
            if basket[item_id_str] <= 0:
                del basket[item_id_str]
            else:
                quantity = basket[item_id_str]

        session['basket'] = basket
        return jsonify({
            'success': True,
            'item_id': item_id,
            'quantity': quantity
        })

@app.route('/checkout', methods=['POST', 'GET'])
@login_required
def checkout():
    basket_items = Basket.query.filter_by(user_id=current_user.id).all()
    address = Address.query.filter_by(user_id=current_user.id).all()

    def validate_checout_form():
        name = request.form.get("name")
        street = request.form.get("street")
        postcode = request.form.get("postcode")
        city = request.form.get("city")
        phone = request.form.get("phone")

        patters = {
        "name": r"^[A-Za-z]+ [A-Za-z]+$",
        "street": r"^[A-Za-z0-9]+ [A-Za-z0-9\s]+$",
        "postcode": r"^[0-9]{4}[A-Za-z]{2}$",
        "city": r"^[A-Za-z\s]{2,50}$",
        "phone": r"^06[0-9]{8}$"
        }

        for field, regex in patters.items():
            value = locals()[field]
            if not re.match(regex, value or ""):
                flash(f"Invalid {field} format.")
                return False
        return True


    if request.method == "POST":

        if not basket_items:
            flash("Your basket is empty")
            return redirect(url_for('menu'))

        selected_id = request.form.get('address_id')

        if selected_id and selected_id.strip():
            address_id = int(selected_id)
        else:
            name = request.form.get('name')
            street = request.form.get('street')
            postal_code = request.form.get('postcode')
            city = request.form.get('city')
            phone_number = request.form.get('phone')

            if not validate_checout_form():
                return render_template("checkout.html", address=address, basket_items=basket_items)

            if name and street and postal_code and city and phone_number:
                new_address = Address(
                    user_id=current_user.id,
                    name=name,
                    street=street,
                    postal_code=postal_code,
                    city=city,
                    phone_number=phone_number
                )
                db.session.add(new_address)
                db.session.commit()
                address_id=new_address.id
            else:
                flash("Please select a saved address or enter a new one")
                return redirect(url_for("checkout"))

        order = Order(
            user_id=current_user.id,
            address_id=address_id, 
            timestamp=datetime.utcnow()
            )

        db.session.add(order)
        db.session.flush() #ensures order.id is available before adding items

        new_status = OrderStatus(order_id=order.id)

        db.session.add(new_status)
        db.session.commit()

        total = 0
        for basket_item in basket_items:
            price = basket_item.item.price
            quantity = basket_item.quantity

            order_item = OrderItem(
                order_id=order.id,
                item_id=basket_item.item_id,
                quantity=quantity,
                price=price
            )
            db.session.add(order_item)

            total += price * quantity
            db.session.delete(basket_item)
        
        order.total = total
        db.session.commit()

        return redirect(url_for('thanks', order_id=order.id))
    return render_template("checkout.html", basket_items=basket_items, address=address)

@app.route("/thanks/<int:order_id>")
@login_required
def thanks(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("thanks.html", order=order)

login_manager = LoginManager()
login_manager.login_view = 'user.start_login'
login_manager.init_app(app)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully")
    return redirect(url_for('user.start_login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(user_bp)


if __name__ == '__main__':
    app.run(debug=True)