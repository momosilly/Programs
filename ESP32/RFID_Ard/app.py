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

