from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mypassword'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myuser:mypassword@localhost/sprintplanner'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

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
    created_at = db.Column(db.DateTime, default=datetime.now(UTC))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "learning_objectives": self.learning_objectives,
            "start_date": self.start_date.isoformat(),
            "deadline": self.deadline.isoformat(),
            "created_at": self.created_at.isoformat(),
        }
    
class Status(db.Model):
    __tablename__ = 'status'

    id = db.Column(db.Integer,primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    pending = db.Column(db.Boolean, default=True)
    approved = db.Column(db.Boolean, default=False)
    approved_at = db.Column(db.Date)
    handed_in = db.Column(db.Boolean, default=False)
    handed_in_at = db.Column(db.Date)
    signed = db.Column(db.Boolean, default=False)
    signed_at = db.Column(db.Date)

#Auth routes
@app.post("/signup")
def signup():
    data = request.get_json()
    name = data["name"]
    email = data["email"]
    password = generate_password_hash(data["password"])

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 400

    user = User(name=name, email=email, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Account created"}), 201

@app.post("/login")
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=str(user.id), additional_claims={"is_admin": user.is_admin})
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

#Protected routes
@app.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access_token}), 200

@app.post("/submit")
@jwt_required()
def submit_request():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    is_admin = claims["is_admin"]

    if is_admin:
        return jsonify({"error": "Admins cannot submit requests"}), 403

    data = request.json
    learning_objectives = data["learning_objectives"]
    start_date = datetime.fromisoformat(data["start_date"]).date()
    deadline = datetime.fromisoformat(data["deadline"]).date()

    if learning_objectives and start_date and deadline:

        new_project = Project(
            user_id=user_id,
            learning_objectives=learning_objectives,
            start_date=start_date,
            deadline=deadline
        )

        db.session.add(new_project)
        db.session.commit()

        new_status = Status(project_id=new_project.id)
        db.session.add(new_status)
        db.session.commit()

        return jsonify({"status": "ok"})
    else:
        return jsonify({"error": "Make sure to fill in all the fields"}), 400

@app.get("/projects")
@jwt_required()
def get_projects():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    is_admin = claims["is_admin"]

    if is_admin:
        projects = db.session.query(Project, User).join(User, Project.user_id == User.id).all()
        result = [
            {
                "id": p.id,
                "learning_objectives": p.learning_objectives,
                "start_date": p.start_date,
                "deadline": p.deadline,
                "user_id": p.user_id,
                "user_name": u.name
            }
            for p, u in projects
        ]
    else:
        projects = Project.query.filter_by(user_id=user_id).all()
        result = [
            {
                "id": p.id,
                "learning_objectives": p.learning_objectives,
                "start_date": p.start_date,
                "deadline": p.deadline,
                "user_id": p.user_id

            }
            for p in projects
        ]
    return jsonify(result)

@app.get('/projects/<int:project_id>')
@jwt_required()
def get_single_project(project_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    is_admin = claims["is_admin"]

    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if not is_admin and project.user_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    status = Status.query.filter_by(project_id=project_id).first()

    return jsonify({
        "project": project.to_dict(),
        "status": {
            "pending": status.pending,
            "approved": status.approved,
            "approved_at": status.approved_at,
            "handed_in": status.handed_in,
            "handed_in_at": status.handed_in_at,
            "signed": status.signed,
            "signed_at": status.signed_at
        }
    })

@app.patch('/projects/<int:project_id>/status')
@jwt_required()
def update_status(project_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    is_admin = claims['is_admin']

    status = Status.query.filter_by(project_id=project_id).first()

    if not status:
        return jsonify({"error": "Status not found"}), 404
    
    data = request.get_json()

    if not is_admin:
        if data.get("handed_in"):
            if not status.approved:
                return jsonify({"error": "Project must be approved before handing in"})
            
            status.pending = False
            status.approved = False
            status.signed = False

            status.handed_in = True
            status.handed_in_at = datetime.now(UTC).date()
        
    if is_admin:
        if data.get("approved"):
            status.pending = False
            status.handed_in = False
            status.signed = False

            status.approved = True
            status.approved_at = datetime.now().date()

        if data.get("signed"):
            status.pending = False
            status.approved = False
            status.handed_in = False

            status.signed = True
            status.signed_at = datetime.now().date()

           

    db.session.commit()
    return jsonify({"status": "updated"})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')