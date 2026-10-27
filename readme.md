# My Web Tools

รวมเครื่องมือออนไลน์ที่ใช้บ่อยไว้ในที่เดียว

**Demo:** https://my-web-tools-axku.onrender.com

## Features

- **X Video Downloader** — ดาวน์โหลดวิดีโอ MP4 พร้อมแสดงขนาดไฟล์
- **TikTok Downloader** — ไม่มีลายน้ำ / HD / MP3
- **WEBP to PDF** — แปลงรูป WEBP เป็น PDF
- **Dark / Light Mode** — จดจำธีมผ่าน localStorage

## Tech Stack

- **Backend:** Python, Flask, yt-dlp
- **Frontend:** HTML, Tailwind CSS (CDN), Vanilla JS
- **Deploy:** Render

## Getting Started

```bash
pip install -r requirements.txt
python server.py
```

เปิด http://127.0.0.1:5000

## Environment Variables

| ชื่อ             | คำอธิบาย                                                          |
| ---------------- | ----------------------------------------------------------------- |
| `COOKIE_CONTENT` | คุกกี้ที่ Export จากบัญชี X ขณะล็อกอิน ใช้ให้ yt-dlp ดึงวิดีโอได้ |

## Structure

```
my-web-tools/
├── server.py          # Flask API & routing
├── requirements.txt
├── templates/         # HTML pages
├── static/            # CSS / JS
└── public/            # sub-projects (photoCraft, pdfCraft)
```
