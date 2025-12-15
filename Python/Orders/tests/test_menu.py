from models import User, Basket, Item
from app import app, db

"""Running this test will affect the acutal database"""

def test_menu_shows_items(client):
    response = client.get('/menu')
    assert response.status_code == 200
    assert b"Pizza" in response.data

def test_menu_session_basket(client):
    with client.session_transaction() as sess:
        sess['basket'] = {"1": 2}

    response = client.get('/menu')
    assert b"Pizza" in response.data
    assert b"2" in response.data

def test_menu_authenticated_user(client):
    with app.app_context():
        user = User.query.filter_by(email="user@example.com").first()
        item = Item.query.first()
        db.session.add(Basket(user_id=user.id, item_id=item.id, quantity=3))
        db.session.commit()
        user_id = user.id

    with client.session_transaction() as sess:
        sess['_user_id'] = str(user_id)

    response = client.get('/menu')
    assert response.status_code == 200
    assert b"Pizza" in response.data
    assert b"3" in response.data