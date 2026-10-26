import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """ทดสอบว่าเข้าหน้าเว็บหลัก (/) ได้และได้สถานะ 200 OK"""
    response = client.get('/')
    assert response.status_code == 200