<div align="center">
  <img src="https://img.icons8.com/color/96/whatsapp--v1.png" alt="WhatsApp Logo" width="80"/>
  <h1>WhatsApp Bulk Messenger</h1>
  <p><strong>Send bulk WhatsApp messages effortlessly — 100% Python, no paid APIs, no Node.js</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Django-4.2-green?logo=django" alt="Django">
    <img src="https://img.shields.io/badge/Selenium-4.15-orange?logo=selenium" alt="Selenium">
    <img src="https://img.shields.io/badge/Celery-5.3-brightgreen?logo=celery" alt="Celery">
    <img src="https://img.shields.io/badge/Bootstrap-5-purple?logo=bootstrap" alt="Bootstrap">
    <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
  </p>

  <br>
  <img src="https://via.placeholder.com/800x450/1e2a3a/25D366?text=WhatsApp+Bulk+Sender+Dashboard" alt="Dashboard Preview" width="80%" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);"/>
  <br><br>
</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **WhatsApp Web Automation** | Selenium-powered Chrome browser that automates WhatsApp Web — session persists so you only scan QR once |
| **No Page Reloads** | Uses WhatsApp's built-in search bar to switch contacts instead of navigating to a new URL each time |
| **Contact Management** | Add, edit, delete, search, paginate. Group contacts. Bulk CSV import/export. |
| **Smart Campaigns** | Compose messages with `{{name}}` placeholders, live preview, image attachments |
| **Delay Control** | Configurable min/max delay (default 5–10s) between messages to avoid spam detection |
| **Live Progress** | Real-time campaign progress bar, recipient log auto-refreshes every 5 seconds |
| **Pause/Resume/Cancel** | Control campaigns mid-flight — pause and resume without losing progress |
| **Export Logs** | Download per-recipient send logs as CSV |
| **Dashboard** | At-a-glance stats: total contacts, campaigns, sent today, running campaigns |
| **Bootstrap 5 UI** | Clean dark sidebar, responsive layout, toast notifications, AJAX forms |
| **WebSocket Support** | Django Channels for live updates on campaign and connection status |

---

## 🖥️ Screenshots

<div align="center">
  <table>
    <tr>
      <td><img src="https://via.placeholder.com/400x250/1e2a3a/25D366?text=Dashboard" width="100%"/></td>
      <td><img src="https://via.placeholder.com/400x250/1e2a3a/25D366?text=WhatsApp+QR+Scan" width="100%"/></td>
    </tr>
    <tr>
      <td align="center"><strong>Dashboard</strong></td>
      <td align="center"><strong>WhatsApp QR Connection</strong></td>
    </tr>
    <tr>
      <td><img src="https://via.placeholder.com/400x250/1e2a3a/25D366?text=Contact+Manager" width="100%"/></td>
      <td><img src="https://via.placeholder.com/400x250/1e2a3a/25D366?text=Campaign+Logs" width="100%"/></td>
    </tr>
    <tr>
      <td align="center"><strong>Contact Management</strong></td>
      <td align="center"><strong>Campaign Live Logs</strong></td>
    </tr>
  </table>
</div>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Django ASGI Server                 │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │  HTTP Views  │  │  WebSocket   │  │  Campaign  │  │
│  │  (REST API)  │  │  Consumers   │  │  Thread    │  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬──────┘  │
│         │                │                │         │
│  ┌──────┴────────────────┴────────────────┴──────┐  │
│  │         WhatsApp Selenium Service              │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │         Chrome WebDriver                  │  │  │
│  │  │   web.whatsapp.com ← session persisted   │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │         Redis           │
              │  ┌──────────────────┐   │
              │  │  Pause/Resume    │   │
              │  │  Cache Flags     │   │
              │  └──────────────────┘   │
              └─────────────────────────┘
```

---

## 🛠️ Tech Stack

<div align="center">

| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **Django 4.2** | Web framework (ASGI via Daphne) |
| **Django REST Framework** | JSON API endpoints |
| **Selenium** | WhatsApp Web browser automation |
| **Chrome WebDriver** | Browser control (auto-managed) |
| **Celery** | Background task queue |
| **Redis** | Message broker + caching + pause flags |
| **Django Channels** | WebSocket for live updates |
| **Bootstrap 5** | Frontend UI framework |
| **SQLite** | Database (zero config) |
| **Whitenoise** | Static file serving |

</div>

---

## 📦 Project Structure

```
whatsapp_bulk_sender/
├── config/                  # Django project configuration
│   ├── settings.py          # Settings (DB, Channels, Celery, Redis)
│   ├── urls.py              # URL routing
│   ├── asgi.py              # ASGI entry point (HTTP + WebSocket)
│   ├── wsgi.py              # WSGI entry point
│   └── celery.py            # Celery app configuration
├── apps/
│   ├── contacts/            # Contact management module
│   │   ├── models.py        # Contact, ContactGroup
│   │   ├── views.py         # CRUD, CSV import/export, groups
│   │   ├── urls.py          # Contact routes
│   │   └── admin.py         # Django admin config
│   ├── campaigns/           # Campaign management module
│   │   ├── models.py        # Campaign, CampaignRecipient
│   │   ├── views.py         # Compose, launch, pause/resume, logs
│   │   ├── urls.py          # Campaign routes
│   │   ├── tasks.py         # Background sending logic (threaded)
│   │   └── admin.py         # Django admin config
│   └── whatsapp/            # WhatsApp automation module
│       ├── selenium_service.py  # Core Selenium WebDriver singleton
│       ├── views.py         # QR polling, connect/disconnect, dashboard
│       ├── consumers.py     # WebSocket consumers
│       ├── routing.py       # WebSocket URL patterns
│       ├── context_processors.py  # Template context (WhatsApp status)
│       └── urls.py          # WhatsApp routes
├── templates/               # Django templates (Bootstrap 5)
│   ├── base.html            # Layout with dark sidebar
│   ├── dashboard.html       # Stats dashboard
│   ├── whatsapp.html        # QR scan page
│   ├── contacts.html        # Contact management
│   ├── campaigns.html       # Campaign list
│   ├── compose.html         # Campaign compose form
│   └── logs.html            # Campaign detail + logs
├── media/                   # Uploaded images
├── .whatsapp_session/       # Chrome profile (persists login)
├── requirements.txt
├── manage.py
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Installation |
|-------------|-------------|
| Python 3.10+ | [python.org](https://python.org) |
| Google Chrome | [google.com/chrome](https://google.com/chrome) |
| Redis | `winget install Redis-64` (Windows) / `brew install redis` (Mac) / `sudo apt install redis-server` (Linux) |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sahil-TRCAC/whatsapp_bulk_messenger.git
cd whatsapp_bulk_messenger

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run database migrations
python manage.py migrate

# 4. Start Redis (separate terminal)
redis-server

# 5. Start Celery worker (separate terminal)
celery -A config worker -l info --pool=solo

# 6. Start Django development server
python manage.py runserver
```

Open **http://localhost:8000** in your browser.

---

## 📱 Usage Guide

### 1️⃣ Connect WhatsApp
1. Click **WhatsApp** in the sidebar
2. Click **Connect WhatsApp** — a Chrome window opens
3. Open WhatsApp on your phone → **Linked Devices** → **Link a Device**
4. Scan the QR code displayed on the screen
5. Status changes to **Connected** (green) ✅

### 2️⃣ Add Contacts
1. Click **Contacts** → **Add**
2. Enter name and phone number with country code (e.g., `919876543210`)
3. Optionally assign to groups
4. For bulk import, click **Import** → upload CSV with `name,phone` columns

### 3️⃣ Create a Campaign
1. Click **Compose** → enter campaign name
2. Write your message with `{{name}}` as a placeholder (e.g., *"Hello {{name}}, special offer just for you!"*)
3. Watch the live preview update as you type
4. Select recipients: all contacts, specific groups, or custom numbers
5. Set delay between messages (recommended: 5–10s)
6. Click **Launch Campaign**

### 4️⃣ Monitor Sending
1. Go to **Campaigns** → click your campaign name
2. Watch the **progress bar** fill up in real-time
3. The **recipient log** table auto-refreshes every 5 seconds
4. Use **Pause / Resume / Cancel** buttons to control the campaign

---

## ⚙️ Configuration

### Delay Settings
Edit `config/settings.py` or set per-campaign in the Compose form:
```python
WHATSAPP_DELAY_MIN = 5  # Minimum seconds between messages
WHATSAPP_DELAY_MAX = 10  # Maximum seconds between messages
```

### Phone Number Format
```
✅ 919876543210    (India — country code 91 + 10 digits)
✅ 14155552671     (US — country code 1 + 10 digits)
❌ +919876543210   (no plus sign)
❌ 9876543210      (missing country code)
❌ 91 98765 43210  (no spaces)
```

---

## ⚠️ Important Notes

- **WhatsApp may ban your account** if you send too many messages too quickly. Keep delays at 5–10+ seconds and avoid sending more than 50–100 messages per hour.
- The Chrome browser window opens visibly — this is normal. It's Selenium controlling WhatsApp Web.
- Session data is saved in `.whatsapp_session/`. You only need to scan the QR code once.
- This uses **unofficial** WhatsApp Web automation. For production/commercial use, consider the official [WhatsApp Business API](https://business.whatsapp.com/).

---

## 🧪 Development

```bash
# Run checks
python manage.py check

# Create superuser for admin panel
python manage.py createsuperuser

# Run tests (if any)
python manage.py test apps/
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues and pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
  <p>Built with ❤️ using Python & Django</p>
  <p>
    <a href="https://github.com/Sahil-TRCAC/whatsapp_bulk_messenger/issues">Report Bug</a>
    ·
    <a href="https://github.com/Sahil-TRCAC/whatsapp_bulk_messenger/issues">Request Feature</a>
  </p>
</div>
