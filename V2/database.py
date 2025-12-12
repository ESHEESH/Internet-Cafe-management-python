# In your database.py file, add these methods:

import mysql.connector
import hashlib
from datetime import datetime

class Database:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""  # Change if needed
        self.database = "cybercafe_db"
        self.conn = None
        self.cursor = None
    
    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            # Try to create database if it doesn't exist
            return self.create_database()
    
    def create_database(self):
        try:
            # Connect without database
            temp_conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            temp_cursor = temp_conn.cursor()
            
            # Create database
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_cursor.execute(f"USE {self.database}")
            
            # Now connect with database
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            return True
        except mysql.connector.Error as err:
            print(f"Database creation error: {err}")
            return False
    
    def setup_database(self):
        """Create all necessary tables"""
        try:
            # Create users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    birthday DATE,
                    points INT DEFAULT 0,
                    streak INT DEFAULT 0,
                    remaining_minutes INT DEFAULT 0,
                    is_approved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create account_requests table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    birthday DATE,
                    status ENUM('Pending', 'Approved', 'Declined') DEFAULT 'Pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP NULL
                )
            ''')
            
            # Create pc_units table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS pc_units (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    status ENUM('Available', 'Occupied', 'Maintenance') DEFAULT 'Available',
                    current_user_id INT NULL,
                    session_start TIMESTAMP NULL,
                    FOREIGN KEY (current_user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            ''')
            
            # Create inventory table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    price DECIMAL(10, 2) NOT NULL,
                    stock INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # Create orders table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    status ENUM('Pending', 'Completed', 'Cancelled') DEFAULT 'Pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            # Create order_items table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES inventory(id) ON DELETE CASCADE
                )
            ''')
            
            # Create sessions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    pc_id INT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    minutes_used INT DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (pc_id) REFERENCES pc_units(id) ON DELETE CASCADE
                )
            ''')
            
            # Create admin table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            ''')
            
            # Insert default admin if not exists
            self.cursor.execute("SELECT * FROM admin WHERE username = 'admin'")
            if not self.cursor.fetchone():
                admin_pass_hash = hashlib.sha256("admin123".encode()).hexdigest()
                self.cursor.execute(
                    "INSERT INTO admin (username, password_hash) VALUES (%s, %s)",
                    ('admin', admin_pass_hash)
                )
            
            self.conn.commit()
            print("Database setup completed successfully!")
            return True
            
        except mysql.connector.Error as err:
            print(f"Error setting up database: {err}")
            return False
    
    # ===== USER METHODS =====
    def get_all_users(self):
        """Get all approved users"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE is_approved = TRUE ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting users: {err}")
            return []
    # In your database.py file, add these methods:

    def check_user_exists(self, username):
        """Check if a username already exists"""
        try:
            self.cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            return self.cursor.fetchone() is not None
        except mysql.connector.Error as err:
            print(f"Error checking user existence: {err}")
            return False

    def create_user_registration(self, username, password, full_name, phone, birthday):
        """Create a new user registration request (user self-registration)"""
        try:
            # Check if user already exists
            if self.check_user_exists(username):
                return "exists"
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, phone, birthday, 
                                points, remaining_minutes, is_approved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            ''', (username, password_hash, full_name, phone, birthday, 0, 0))
            self.conn.commit()
            return "success"
        except mysql.connector.Error as err:
            print(f"Error creating user registration: {err}")
            return "error"

    def get_all_users_with_status(self):
        """Get all users including admin-created and self-registered"""
        try:
            self.cursor.execute('''
                SELECT id, username, full_name, phone, birthday, 
                    points, remaining_minutes, streak, 
                    created_at, is_approved,
                    CASE 
                        WHEN is_approved = FALSE THEN 'Pending Approval'
                        ELSE 'Active'
                    END as status
                FROM users 
                WHERE username != 'admin'
                ORDER BY created_at DESC
            ''')
            columns = [desc[0] for desc in self.cursor.description]
            users = []
            for row in self.cursor.fetchall():
                user_dict = dict(zip(columns, row))
                user_dict['created_at'] = str(user_dict['created_at'])
                users.append(user_dict)
            return users
        except mysql.connector.Error as err:
            print(f"Error fetching users: {err}")
            return []
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error getting user: {err}")
            return None
    
    def create_user(self, username, password, full_name, phone, birthday):
        """Create a new user (approved)"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, phone, birthday, is_approved)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            ''', (username, password_hash, full_name, phone, birthday))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error creating user: {err}")
            return False
    
    def update_user_password(self, user_id, new_password):
        """Update user password"""
        try:
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            self.cursor.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (password_hash, user_id)
            )
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating password: {err}")
            return False
    
    def add_user_minutes(self, user_id, minutes):
        """Add minutes to user account"""
        try:
            self.cursor.execute(
                "UPDATE users SET remaining_minutes = remaining_minutes + %s WHERE id = %s",
                (minutes, user_id)
            )
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error adding minutes: {err}")
            return False
    
    # ===== ACCOUNT REQUEST METHODS =====
    def create_account_request(self, username, password, full_name, phone, birthday):
        """Create a new account request"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO account_requests (username, password_hash, full_name, phone, birthday)
                VALUES (%s, %s, %s, %s, %s)
            ''', (username, password_hash, full_name, phone, birthday))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error creating account request: {err}")
            return False
    
    def get_pending_requests(self):
        """Get all pending account requests"""
        try:
            self.cursor.execute("SELECT * FROM account_requests WHERE status = 'Pending' ORDER BY requested_at DESC")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting pending requests: {err}")
            return []
    
    def approve_account_request(self, request_id):
        """Approve an account request"""
        try:
            # Start transaction
            self.cursor.execute("START TRANSACTION")
            
            # Get the request
            self.cursor.execute("SELECT * FROM account_requests WHERE id = %s", (request_id,))
            request = self.cursor.fetchone()
            
            if not request:
                return False
            
            # Create the user in users table
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, phone, birthday, is_approved)
                VALUES (%s, %s, %s, %s, %s, TRUE)
            ''', (request['username'], request['password_hash'], request['full_name'], 
                  request['phone'], request['birthday']))
            
            # Update request status
            self.cursor.execute('''
                UPDATE account_requests 
                SET status = 'Approved', processed_at = NOW() 
                WHERE id = %s
            ''', (request_id,))
            
            self.conn.commit()
            return True
            
        except mysql.connector.Error as err:
            self.conn.rollback()
            print(f"Error approving request: {err}")
            return False
    
    def decline_account_request(self, request_id):
        """Decline an account request"""
        try:
            self.cursor.execute('''
                UPDATE account_requests 
                SET status = 'Declined', processed_at = NOW() 
                WHERE id = %s
            ''', (request_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error declining request: {err}")
            return False
    
    # ===== INVENTORY METHODS =====
    def get_inventory(self):
        """Get all inventory items"""
        try:
            self.cursor.execute("SELECT * FROM inventory ORDER BY name")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting inventory: {err}")
            return []
    
    def add_inventory_item(self, name, category, price, stock):
        """Add new inventory item"""
        try:
            self.cursor.execute('''
                INSERT INTO inventory (name, category, price, stock)
                VALUES (%s, %s, %s, %s)
            ''', (name, category, price, stock))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error adding inventory item: {err}")
            return False
    
    def update_inventory_stock(self, product_id, stock_change):
        """Update inventory stock"""
        try:
            self.cursor.execute(
                "UPDATE inventory SET stock = stock + %s WHERE id = %s",
                (stock_change, product_id)
            )
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating inventory: {err}")
            return False
    
    # ===== PC UNITS METHODS =====
    def get_pc_units(self):
        """Get all PC units"""
        try:
            self.cursor.execute("SELECT * FROM pc_units ORDER BY name")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting PC units: {err}")
            return []
    
    def update_pc_status(self, pc_id, status, user_id=None):
        """Update PC status"""
        try:
            if user_id:
                self.cursor.execute('''
                    UPDATE pc_units 
                    SET status = %s, current_user_id = %s, session_start = NOW() 
                    WHERE id = %s
                ''', (status, user_id, pc_id))
            else:
                self.cursor.execute('''
                    UPDATE pc_units 
                    SET status = %s, current_user_id = NULL, session_start = NULL 
                    WHERE id = %s
                ''', (status, pc_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error updating PC status: {err}")
            return False
    
    # ===== ORDER METHODS =====
    def get_orders(self):
        """Get all orders"""
        try:
            self.cursor.execute('''
                SELECT o.*, u.username, u.full_name 
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.order_date DESC
            ''')
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting orders: {err}")
            return []
    
    # ===== SESSION METHODS =====
    def get_recent_sessions(self, limit=10):
        """Get recent sessions"""
        try:
            self.cursor.execute('''
                SELECT s.*, u.username as user, p.name as pc
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                JOIN pc_units p ON s.pc_id = p.id
                ORDER BY s.start_time DESC
                LIMIT %s
            ''', (limit,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting sessions: {err}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()