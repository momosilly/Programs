from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mypassword'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/sprintplanner'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Models
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    learning_objectives = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    deadline = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "learning_objectives": self.learning_objectives,
            "start_date": self.start_date.isoformat(),
            "deadline": self.deadline.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
    
#Token helpers    
def create_token(user):
    payload = {
        "user_id": user.id,
        "is_admin": user.is_admin,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except:
        return None
    
def get_current_user():
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    
    token = auth.split(" ")[1]
    data = decode_token(token)
    return data

#Auth routes
@app.post("/signup")
def signup():
    data = request.json
    name = data["name"]
    email = data["email"]
    password = data["password"]

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 400

    hashed = generate_password_hash(password)

    new_user = User(name=name, email=email, password=hashed)
    db.session.add(new_user)
    db.session.commit()

    token = create_token(new_user)
    return jsonify({"token": token})

@app.post("/login")
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    
    token = create_token(user)
    return jsonify({"token": token})

#Protected routes
@app.post("/submit")
def submit_request():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    learning_objectives = data["learning_objectives"]
    start_date = datetime.fromisoformat(data["start_date"]).date()
    deadline = datetime.fromisoformat(data["deadline"]).date()

    new_project = Project(
        user_id=user["user_id"],
        learning_objectives=learning_objectives,
        start_date=start_date,
        deadline=deadline
    )

    db.session.add(new_project)
    db.session.commit()

    return jsonify({"status": "ok"})

@app.get("/projects")
def get_projects():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if user["is_admin"]:
        projects = Project.query.order_by(Project.created_at.desc()).all()
    else:
        projects = Project.query.filter_by(user_id=user["user_id"]).order_by(Project.created_at.desc()).all()

    return jsonify([p.to_dict() for p in projects])

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')