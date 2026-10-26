import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ทดสอบหน้าเว็บหลัก
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

# เทสต์การเข้าถึงหน้าเครื่องมือหลัก
def test_tools_pages(client):
    assert client.get('/webp_pdf.html').status_code == 200
    assert client.get('/x-downloader.html').status_code == 200
    assert client.get('/tiktok-downloader.html').status_code == 200

# เทสต์การเข้าถึงโฟลเดอร์ public (โปรเจกต์ Craft)
def test_public_craft_pages(client):
    assert client.get('/public/photocraft/photocraft.html').status_code == 200
    assert client.get('/public/pdfcraft/pdfcraft.html').status_code == 200

# เทสต์ระบบ API บังคับดาวน์โหลดวิดีโอ (X Downloader)
def test_force_download_api_no_url(client):
    response = client.get('/api/force_download')
    assert response.status_code == 400