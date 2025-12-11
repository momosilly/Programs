from flask import Blueprint, request, render_template, redirect, url_for, flash, abort, current_app as app
from flask_login import login_required, current_user
from models import Order, db, OrderStatus
from datetime import datetime

delivery_bp = Blueprint("delivery", __name__, url_prefix='/delivery')

@delivery_bp.route('/')
def dashboard():
    orders = (
        db.session.query(Order)
        .join(OrderStatus)
        .filter(OrderStatus.delivered == False)
        .all()
    )
    if not current_user.has_role("delivery"):
        abort(403)

    return render_template("delivery.html", orders=orders)

@delivery_bp.route('/ship/<int:order_id>', methods=['POST'])
@login_required
def shipped(order_id):
    order = Order.query.get_or_404(order_id)

    if not current_user.has_role("delivery"):
        abort(403)

    delivered = request.form.get('delivered')

    if not delivered:
        flash("Please confirm the delivery of the order")
        return redirect(url_for('delivery.dashboard'))

    order.status.delivered = True
    order.status.delivered_at = datetime.utcnow()

    db.session.add(order.status)
    db.session.commit()

    flash("Order marked as shipped.")
    return redirect(url_for('delivery.dashboard'))