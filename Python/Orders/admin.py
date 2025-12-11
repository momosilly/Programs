from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app as app
from flask_login import login_required, current_user
from models import Order, db, Item, User, UserRole, Role
import os
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    orders = Order.query.all()
    if not current_user.has_role("admin"):
        abort(403)
    
    item_query = request.args.get('query')
    if item_query:
        items = Item.query.filter(Item.name.ilike(f"%{item_query}%")).all()
    else:
        items = Item.query.all()
    
    user_query = request.args.get('user_query')
    if user_query:
        users = User.query.filter(User.email.ilike(f"%{user_query}%")).all()
    else:
        users = User.query.all()
    
    return render_template('admin.html', items=items, item_query=item_query, users=users, user_query=user_query, orders=orders)

@admin_bp.route('/add_role/<int:user_id>', methods=['POST'])
def add_role(user_id):
    if not current_user.has_role("admin"):
        abort(403)
    user = User.query.get_or_404(user_id)
    role_id = request.form.get("role_id")

    role = Role.query.get_or_404(role_id)
    existing = UserRole.query.filter_by(user_id=user.id, role_id=role.id).first()

    if existing:
        flash("Role already assigned")
        return redirect(url_for("admin.dashboard"))
    new_assignment = UserRole(user_id=user.id, role_id=role.id)
    db.session.add(new_assignment)
    db.session.commit()
    
    flash(f"Assigned role {role.role} to user {user.email}")
    return redirect(url_for("admin.dashboard"))

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
    if not current_user.has_role("admin"):
        abort(403)
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash(f"{item.name} deleted.")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_item/<int:item_id>', methods=['POST'])
@login_required
def edit_item(item_id):
    if not current_user.has_role("admin"):
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