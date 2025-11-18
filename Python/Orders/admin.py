from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app as app
from flask_login import login_required, current_user
from models import Order, db, Item
import os
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    orders = Order.query.all()
    if not current_user.is_admin:
        abort(403)
    
    query = request.args.get('query')
    if query:
        items = Item.query.filter(Item.name.ilike(f"%{query}%")).all()
    else:
        items = Item.query.all()
    
    return render_template('admin.html', items=items, query=query, orders=orders) #orders=orders

@admin_bp.route('/ship/<int:order_id>', methods=['POST'])
@login_required
def mark_shipped(order_id):
    order = Order.query.get_or_404(order_id)
    order.shipped = True
    db.session.commit()
    flash("Order marked as shipped.")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/add_item', methods=['POST'])
@login_required
def add_item():
    if not current_user:
        abort(403)
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    category = request.form.get('category')
    image = request.files['image']

    if image:
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(user_folder, exist_ok=True)

        ext = image.filename.rsplit('.',1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(user_folder, unique_filename)
        file_path_db = file_path.replace("\\", "/")

        image.save(file_path)

    item = Item(name=name, description=description, price=float(price), category=category, image_url=file_path_db)
    db.session.add(item)
    db.session.commit()
    flash(f"{item.name} added to menu")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if not current_user.is_admin:
        abort(403)
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"{item.name} deleted.")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_item/<int:item_id>', methods=['POST'])
@login_required
def edit_item(item_id):
    if not current_user.is_admin:
        abort(403)
    item = Item.query.get_or_404(item_id)
    item.name = request.form.get('name')
    item.description = request.form.get('description')
    item.price = float(request.form.get('price'))
    item.category = request.form.get('category')

    image = request.files.get('image')

    if image and image.filename:
        ext = image.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id))
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, unique_filename)
        image.save(file_path)
        item.image_url = file_path.replace("\\", "/")

    db.session.commit()
    flash(f"{item.name} updated.")
    return redirect(url_for('admin.dashboard'))