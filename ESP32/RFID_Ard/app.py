from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, UTC

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mypassword'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/rfid'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    uid = db.Column(db.String(30), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

class Logs(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uid = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC))

@app.get("/scan")
def scan():
    uid = request.args.get("uid")

    log = Logs(uid=uid)
    db.session.add(log)
    db.session.commit()

    user = User.query.filter_by(uid=uid).first()

    if user:
        return {
            "status": "ok",
            "name": user.name,
            "admin": user.is_admin
        }
    else:
        return {
            "status": "unknown_uid",
            "uid": uid
        }
    
@app.get("/admin")
def admin_page():
    uid = request.args.get("uid")
    user = User.query.filter_by(uid=uid).first()

    if not user or not user.is_admin:
        return {"error": "Forbidden"}

    return {"message": "Welcome admin!"}