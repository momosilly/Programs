import pytest
from app import app, db
from models import User, Role, UserRole, Item

@pytest.fixture
def client():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    # Rebind db to the new URI
    with app.app_context():
        db.engine.dispose()
        db.drop_all()
        db.create_all()

        # seed roles
        admin_role = Role(role="admin")
        customer_role = Role(role="customer")
        db.session.add_all([admin_role, customer_role])
        db.session.commit()

        # seed users
        admin = User(email="admin@example.com")
        user = User(email="user@example.com")
        db.session.add_all([admin, user])
        db.session.commit()

        db.session.add(UserRole(user_id=admin.id, role_id=admin_role.id))
        db.session.add(UserRole(user_id=user.id, role_id=customer_role.id))
        db.session.commit()

        # seed item
        item = Item(name="Pizza", price=10.0, description="Cheesy", category="food", image_url="static/icons/default.png")
        db.session.add(item)
        db.session.commit()

    with app.test_client() as client:
        yield client