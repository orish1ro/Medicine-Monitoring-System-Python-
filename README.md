# MediTrack — Medicine Management System

Python CLI backend for managing medicine inventory, connected to MariaDB/MySQL.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Open `config.py` and set your DB password if needed:
   ```python
   DB_CONFIG = {
       'host':     '127.0.0.1',
       'password': 'your_password_here',
       ...
   }
   ```

3. Make sure `medicine_management_db` exists in phpMyAdmin (it already does).

4. Run the app:
   ```
   python main.py
   ```
   The app will auto-create any missing tables on first run.

## Project Structure

```
mms/
├── config.py                  # DB credentials
├── main.py                    # Entry point + menu loop
├── requirements.txt
├── controllers/               # Business logic layer
│   ├── auth_controller.py
│   ├── dashboard_controller.py
│   ├── expiry_controller.py
│   ├── inventory_controller.py
│   ├── medicine_controller.py
│   ├── report_controller.py
│   └── search_controller.py
├── database/                  # DB connection + setup
│   ├── db_connection.py
│   └── db_setup.py
├── models/                    # Raw SQL queries
│   ├── inventory_model.py
│   ├── medicine_model.py
│   ├── report_model.py
│   └── user_model.py
├── utils/                     # Helpers
│   ├── csv_exporter.py
│   ├── helpers.py
│   └── validators.py
└── views/                     # Print-based UI
    ├── add_medicine_view.py
    ├── dashboard_view.py
    ├── expiry_view.py
    ├── inventory_view.py
    ├── login_view.py
    ├── report_view.py
    ├── search_view.py
    └── signup_view.py
```
