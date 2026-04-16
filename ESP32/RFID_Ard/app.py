from flask import Flask, request, render_template, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, UTC

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mypassword'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/rfid'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ── Models ────────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(50))
    uid      = db.Column(db.String(30), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class Logs(db.Model):
    __tablename__ = 'logs'
    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uid       = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_logged_in_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


# ── RFID scan endpoint (called by Arduino) ────────────────────────────────────

@app.get("/scan")
def scan():
    uid = request.args.get("uid")
    user = User.query.filter_by(uid=uid).first()

    if not user:
        user = User(uid=uid, name=None, is_admin=False)
        db.session.add(user)
        db.session.commit()
        return {"status": "registered_pending", "uid": uid}

    log = Logs(user_id=user.id, uid=uid)
    db.session.add(log)
    db.session.commit()

    return {"status": "ok", "name": user.name, "admin": user.is_admin}


# ── Login ─────────────────────────────────────────────────────────────────────

@app.get("/login")
def login_page():
    return render_template("login.html")

@app.post("/login")
def login():
    uid = request.form.get("uid", "").strip()
    user = User.query.filter_by(uid=uid).first()

    if not user:
        return render_template("login.html", error="UID not found.")

    session["user_id"] = user.id

    if user.is_admin:
        return redirect(url_for("admin_page"))
    return redirect(url_for("user_page", user_id=user.id))

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ── Admin page ────────────────────────────────────────────────────────────────

@app.get("/admin")
def admin_page():
    current = get_logged_in_user()
    if not current or not current.is_admin:
        return redirect(url_for("login_page"))

    users = User.query.order_by(User.id).all()
    logs  = Logs.query.order_by(Logs.timestamp.desc()).limit(100).all()

    # Build a lookup so the template can show names in the log table
    user_map = {u.id: u for u in users}

    return render_template("admin.html", users=users, logs=logs, user_map=user_map, current=current)

@app.post("/admin/edit/<int:user_id>")
def admin_edit_user(user_id):
    current = get_logged_in_user()
    if not current or not current.is_admin:
        return redirect(url_for("login_page"))

    user = User.query.get_or_404(user_id)
    user.name     = request.form.get("name", "").strip() or None
    user.is_admin = "is_admin" in request.form
    db.session.commit()
    return redirect(url_for("admin_page"))

@app.post("/admin/delete/<int:user_id>")
def admin_delete_user(user_id):
    current = get_logged_in_user()
    if not current or not current.is_admin:
        return redirect(url_for("login_page"))

    user = User.query.get_or_404(user_id)
    Logs.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_page"))


# ── User page ─────────────────────────────────────────────────────────────────

@app.get("/user/<int:user_id>")
def user_page(user_id):
    current = get_logged_in_user()
    if not current:
        return redirect(url_for("login_page"))

    # Regular users can only see themselves
    if not current.is_admin and current.id != user_id:
        return redirect(url_for("user_page", user_id=current.id))

    user = User.query.get_or_404(user_id)
    logs = Logs.query.filter_by(user_id=user_id).order_by(Logs.timestamp.desc()).all()
    return render_template("user.html", user=user, logs=logs, current=current)


# ── Root redirect ─────────────────────────────────────────────────────────────

@app.get("/")
def index():
    current = get_logged_in_user()
    if not current:
        return redirect(url_for("login_page"))
    if current.is_admin:
        return redirect(url_for("admin_page"))
    return redirect(url_for("user_page", user_id=current.id))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')