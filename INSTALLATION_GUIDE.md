# Starbroke Internet Cafe System - Installation Guide

## Prerequisites

### 1. Python Installation
- **Python 3.10 or higher** is required
- Download from: https://www.python.org/downloads/
- During installation, **CHECK** "Add Python to PATH"

### 2. MySQL/XAMPP Installation
You need a MySQL database server. Choose one option:

#### Option A: XAMPP (Recommended for beginners)
1. Download XAMPP from: https://www.apachefriends.org/
2. Install XAMPP (default settings are fine)
3. Open XAMPP Control Panel
4. Click "Start" next to MySQL
5. The database will be created automatically when you run the app

#### Option B: MySQL Server (Advanced users)
1. Download MySQL Community Server from: https://dev.mysql.com/downloads/mysql/
2. Install with default settings
3. Remember your root password (or leave it empty)
4. The database will be created automatically when you run the app

---

## Installation Steps

### Step 1: Extract the Project Files
Extract all files to a folder, for example:
```
C:\Starbroke\
```

### Step 2: Open Command Prompt/Terminal
1. Press `Windows + R`
2. Type `cmd` and press Enter
3. Navigate to the project folder:
```bash
cd C:\Starbroke
```

### Step 3: Install Required Python Packages

#### Method 1: Using requirements.txt (Recommended)
```bash
pip install -r requirements.txt
```

#### Method 2: Install packages individually
```bash
pip install mysql-connector-python
pip install pywin32
pip install Pillow
```

### Step 4: Verify Installation
Check if packages are installed:
```bash
pip list
```

You should see:
- mysql-connector-python
- pywin32
- Pillow

---

## Running the Application

### 1. Start MySQL Server
- **If using XAMPP**: Open XAMPP Control Panel and start MySQL
- **If using MySQL Server**: It should start automatically

### 2. Run the Application
```bash
python main.py
```

Or simply double-click `main.py` if Python is associated with .py files.

### 3. First Time Setup
The application will automatically:
- Create the database named `internet_cafe`
- Create all necessary tables
- Create a default admin account:
  - **Username**: `admin`
  - **Password**: `admin123`

---

## Default Login Credentials

### Admin Panel
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **IMPORTANT**: Change the admin password after first login!

---

## Troubleshooting

### Error: "Python was not found"
- Reinstall Python and check "Add Python to PATH"
- Or use `py` instead of `python`:
  ```bash
  py main.py
  ```

### Error: "No module named 'mysql'"
- Install mysql-connector-python:
  ```bash
  pip install mysql-connector-python
  ```

### Error: "Can't connect to MySQL server"
- Make sure MySQL is running (check XAMPP Control Panel)
- Verify MySQL is running on port 3306
- Check if another program is using port 3306

### Error: "Authentication plugin cannot be loaded"
- This is already fixed in the code with `use_pure=True`
- If still occurs, reinstall mysql-connector-python:
  ```bash
  pip uninstall mysql-connector-python
  pip install mysql-connector-python
  ```

### Error: "No module named 'win32gui'"
- Install pywin32:
  ```bash
  pip install pywin32
  ```

### PC Lock Mode Not Working
- PC lock features require Windows OS
- Make sure pywin32 is installed
- Run as Administrator for full functionality

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 or higher
- **Python**: 3.10+
- **RAM**: 4GB
- **Storage**: 500MB free space
- **Display**: 1024x768 resolution

### Recommended Requirements
- **OS**: Windows 10/11
- **Python**: 3.11+
- **RAM**: 8GB
- **Storage**: 1GB free space
- **Display**: 1920x1080 resolution

---

## Features

### User Features
- ✅ PC selection and login
- ✅ Time-based billing system
- ✅ Cafe menu ordering
- ✅ Account balance management
- ✅ Session time tracking
- ✅ Kiosk mode (full-screen lock)

### Admin Features
- ✅ PC unit management
- ✅ User account creation and approval
- ✅ Order management
- ✅ Inventory tracking
- ✅ Menu item management
- ✅ PC lock/unlock controls
- ✅ **Global Kiosk Mode Control** (NEW!)
- ✅ Emergency exit with admin authentication

---

## Security Features

### Kiosk Mode
When a user logs in, the system automatically enables:
- Full-screen mode
- Alt+Tab blocking
- Task Manager blocking
- Windows key blocking
- Taskbar hiding

### Emergency Exit
- Requires admin authentication
- Available on PC selection and login screens
- Safely closes the application

### Emergency Unlock
- Allows admin to unlock a user's PC
- Disables kiosk mode temporarily
- User session remains active

---

## Database Configuration

If you need to change database settings, edit `main.py` and `admin_panel.py`:

```python
self.db_connection = mysql.connector.connect(
    host='localhost',      # Change if MySQL is on another server
    port=3306,            # Change if using different port
    user='root',          # Change if using different user
    password='',          # Add password if MySQL has one
    database='internet_cafe',
    use_pure=True
)
```

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all prerequisites are installed
3. Make sure MySQL is running
4. Check Python version: `python --version`

---

## Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] XAMPP/MySQL installed and running
- [ ] All pip packages installed (`pip install -r requirements.txt`)
- [ ] Project files extracted
- [ ] Run `python main.py`
- [ ] Login to admin panel (admin/admin123)
- [ ] Create user accounts
- [ ] Test PC selection and login

---

## File Structure

```
Starbroke/
├── main.py                    # Main application file
├── admin_panel.py             # Admin panel interface
├── user_home.py              # User home screen
├── user_cafe.py              # Cafe ordering system
├── user_account.py           # User account management
├── requirements.txt          # Python dependencies
├── INSTALLATION_GUIDE.md     # This file
├── images/                   # Menu item images
│   ├── item_1.jfif
│   ├── item_2.jpg
│   └── ...
└── __pycache__/              # Python cache (auto-generated)
```

---

## License

This software is provided as-is for educational and commercial use.

---

**Enjoy using Starbroke Internet Cafe System! ☕🖥️**
