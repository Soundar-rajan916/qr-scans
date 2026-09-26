# Event QR Scan Management System

A robust Django-based event management system designed to handle user registrations, exhibitor tiered plans, device session tracking, and QR code scanning logic.

## Features

- **User Management & Questionnaires:** Users can register for the event, answer dynamic questionnaires, and receive a score based on their responses.
- **Exhibitor Tiers & Device Limits:** Exhibitors are categorized into `Silver`, `Gold`, and `Platinum` tiers, which dynamically restrict the number of concurrently active devices allowed for their account (1, 2, and 3 respectively).
- **Secure QR Scanning:** Users are assigned a uniquely signed QR code. Exhibitors can securely scan these QR codes using their authorized devices.
- **Scan Logging:** Every QR scan is securely logged into the database tracking the exact Exhibitor, the specific Device, the scanned User, and the exact timestamp.
- **Strict Device Session Management:** Login and logout sessions are strictly tracked on a per-device level ensuring a robust history of exactly when and where an exhibitor logged in. 
- **Tailored Django Admin:** A heavily customized Django Admin panel that provides real-time counts of total scans per exhibitor, currently logged-in devices, and a focused view of each exhibitor's isolated scan logs.

## Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** SQLite (development)
- **Security:** Django Signed Tokens (for QR generation & verification)

## Core Models

### Exhibitors
- **Exhibitor**: Represents the company/entity. Tied to Django Auth Users and assigned a tier (Silver, Gold, Platinum).
- **ExhibitorDevice**: Tracks the physical devices (e.g. mobile phones or browsers) tied to an Exhibitor.
- **ExhibitorDeviceSession**: Robust login history tracker that enforces the tier limits using active unclosed sessions.
- **ScanLog**: The historical ledger of every successful QR scan.

### Users
- **EventUser**: The attendees of the event. Contains their questionnaire responses, generated score, and unique user ID.
- **Question & Option**: Models allowing dynamic questionnaires with individual scoring capabilities.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Soundar-rajan916/qr-scans.git
   cd qr-scans
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser for Admin Access:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the Application:**
   - Frontend: `http://127.0.0.1:8000/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`

## Testing

The project includes an exhaustive suite of backend tests simulating the full E2E session flows, concurrent device limit rejections, and QR scanning endpoints. 

To run the test suite:
```bash
python manage.py test
```
