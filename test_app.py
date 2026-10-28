# import pytest
# from server import app

# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client

# # ทดสอบหน้าเว็บหลัก
# def test_home_page(client):
#     response = client.get('/')
#     assert response.status_code == 200

# # เทสต์การเข้าถึงหน้าเครื่องมือหลัก (รวม PDF Merge แล้ว)
# def test_tools_pages(client):
#     assert client.get('/webp_pdf.html').status_code == 200
#     assert client.get('/x-downloader.html').status_code == 200
#     assert client.get('/tiktok-downloader.html').status_code == 200
#     assert client.get('/youtube-downloader.html').status_code == 200
#     assert client.get('/pdf_merge.html').status_code == 200  # เช็กหน้า รวมไฟล์ PDF

# # เทสต์การเข้าถึงโฟลเดอร์ public (โปรเจกต์ Craft)
# def test_public_craft_pages(client):
#     assert client.get('/public/photocraft/photocraft.html').status_code == 200
#     assert client.get('/public/pdfcraft/pdfcraft.html').status_code == 200

# # เทสต์ระบบ API บังคับดาวน์โหลดวิดีโอ (Proxy Download)
# def test_force_download_api_no_url(client):
#     response = client.get('/api/force_download')
#     if response.status_code != 404:
#         assert response.status_code == 400

# # ==================================================
# # Test Cases สำหรับ YouTube Downloader
# # ==================================================
# def test_get_youtube_video_api_no_url(client):
#     response = client.post('/api/get_youtube_video', json={})
#     assert response.status_code == 400
#     assert response.get_json()['error'] == 'กรุณาระบุ URL'

# def test_download_local_no_url(client):
#     response = client.get('/api/download_local')
#     assert response.status_code == 500
