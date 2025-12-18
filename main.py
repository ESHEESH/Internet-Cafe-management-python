import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
import hashlib
import sys
import os
from user_home import HomeFrame
from user_cafe import CafeFrame
from user_account import AccountsFrame
from admin_panel import AdminApp

# Windows-specific imports for PC locking
try:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        import win32gui
        import win32con
        import win32api
        import win32process
        WINDOWS_LOCK_AVAILABLE = True
    else:
        WINDOWS_LOCK_AVAILABLE = False
except ImportError:
    WINDOWS_LOCK_AVAILABLE = False
    print("⚠️ Windows API not available - PC lock features will be limited")

class CafeSystemApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Starbroke - Internet Cafe System")
        self.root.state('zoomed')
        self.root.minsize(1024, 768)

        self.admin_window = None
        self.admin_app_instance = None

        # 🎨 COLOR SCHEME (define FIRST)
        self.bg_color = "#FFF8F0"
        self.secondary_bg = "#FFFFFF"
        self.accent_color = "#8BA888"
        self.primary_btn = "#8BA888"
        self.dark_brown = "#4A3728"
        self.light_brown = "#D4B896"
        self.text_color = "#2D2D2D"
        self.text_secondary = "#8B8B8B"

        self.root.configure(bg=self.bg_color)

        self.current_user = None
        self.db_connection = None

        # PC Selection variables
        self.selected_pc = None
        self.pc_frames_data = {}
        
        # PC Lock variables
        self.is_locked = False
        self.original_window_state = None
        self.blocked_keys = []

        # Setup
        self.setup_database()
        
        # Check if kiosk mode should be enabled from database settings
        if self.should_enable_kiosk_mode():
            self.enable_pc_lock()
        
        self.show_pc_selection()   # ✅ now safe

    
    def setup_database(self):
        """Setup database with ALL features"""
        try:
            self.db_connection = mysql.connector.connect(
                host='localhost',
                port=3306,  # Your port
                user='root',
                password='',
                database='internet_cafe',
                use_pure=True  # Fix for authentication plugin issue
            )
            


            if self.db_connection.is_connected():
                cursor = self.db_connection.cursor()
                
                # Admins table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        admin_id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Users table with NEW fields
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        phone_number VARCHAR(20),
                        account_balance DECIMAL(10, 2) DEFAULT 0.00,
                        session_time_limit INT DEFAULT 120,
                        hourly_rate DECIMAL(10, 2) DEFAULT 20.00,
                        is_approved BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # NEW: PC Units table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pc_units (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        unit_name VARCHAR(20) UNIQUE NOT NULL,
                        status ENUM('Available', 'Occupied', 'Offline', 'Maintenance') DEFAULT 'Available',
                        current_user_id INT NULL,
                        session_start TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (current_user_id) REFERENCES users(user_id) ON DELETE SET NULL
                    )
                """)
                
                # Cafe items with image support (create BEFORE orders table)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cafe_items (
                        item_id INT AUTO_INCREMENT PRIMARY KEY,
                        item_name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        price DECIMAL(10, 2) NOT NULL,
                        image_path VARCHAR(255) DEFAULT NULL,
                        available BOOLEAN DEFAULT TRUE
                    )
                """)
                
                # Orders table (create AFTER cafe_items table)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        item_id INT NULL,
                        item_name VARCHAR(100) NOT NULL,
                        quantity INT NOT NULL,
                        price DECIMAL(10, 2) NOT NULL,
                        total_price DECIMAL(10, 2) NOT NULL,
                        order_status VARCHAR(20) DEFAULT 'Pending',
                        order_type VARCHAR(50) DEFAULT 'Deliver to PC',
                        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                        FOREIGN KEY (item_id) REFERENCES cafe_items(item_id)
                    )
                """)
                
                # Check if order_type column exists, if not add it (for existing databases)
                cursor.execute("SHOW COLUMNS FROM orders LIKE 'order_type'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE orders ADD COLUMN order_type VARCHAR(50) DEFAULT 'Deliver to PC'")
                    print("✅ Added order_type column to orders table")
                
                # NEW: Inventory table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) DEFAULT 'General',
                        quantity INT DEFAULT 0,
                        unit_price DECIMAL(10,2) NOT NULL,
                        min_stock_level INT DEFAULT 0,
                        description TEXT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Check if is_locked column exists, if not add it
                cursor.execute("SHOW COLUMNS FROM pc_units LIKE 'is_locked'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE pc_units ADD COLUMN is_locked BOOLEAN DEFAULT FALSE")
                    print("✅ Added is_locked column to pc_units")
                
                # Create system settings table and set default kiosk mode
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        setting_name VARCHAR(50) PRIMARY KEY,
                        setting_value VARCHAR(100),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                # Set default kiosk mode to enabled (for security)
                cursor.execute("""
                    INSERT IGNORE INTO system_settings (setting_name, setting_value) 
                    VALUES ('kiosk_mode_enabled', 'true')
                """)
                print("✅ System settings table created with default kiosk mode")
                
                # Create default admin
                cursor.execute("SELECT COUNT(*) FROM admins")
                if cursor.fetchone()[0] == 0:
                    default_password = hashlib.sha256("admin123".encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO admins (username, password, full_name) VALUES (%s, %s, %s)",
                        ('admin', default_password, 'System Administrator')
                    )
                    print("✓ Default admin created")
                
                # NEW: Create default PC units
                cursor.execute("SELECT COUNT(*) FROM pc_units")
                if cursor.fetchone()[0] == 0:
                    for i in range(1, 11):
                        cursor.execute(
                            "INSERT INTO pc_units (unit_name, status) VALUES (%s, %s)",
                            (f'PC-{i:02d}', 'Available')
                        )
                    print("✓ Default PC units created")
                
                # Create sample cafe items (from ORIGINAL - more items)
                cursor.execute("SELECT COUNT(*) FROM cafe_items")
                if cursor.fetchone()[0] == 0:
                    sample_items = [
                        ('Espresso', 'Coffee', 45.00),
                        ('Cappuccino', 'Coffee', 65.00),
                        ('Latte', 'Coffee', 70.00),
                        ('Iced Coffee', 'Coffee', 60.00),
                        ('Americano', 'Coffee', 55.00),
                        ('Mocha', 'Coffee', 75.00),
                        ('Club Sandwich', 'Food', 120.00),
                        ('Burger', 'Food', 150.00),
                        ('Fries', 'Snack', 50.00),
                        ('Pizza Slice', 'Food', 80.00),
                        ('Pasta', 'Food', 130.00),
                        ('Bottled Water', 'Drinks', 20.00),
                        ('Soda', 'Drinks', 35.00),
                        ('Iced Tea', 'Drinks', 40.00),
                        ('Fruit Juice', 'Drinks', 45.00),
                        ('Cookies', 'Snack', 35.00),
                        ('Muffin', 'Snack', 45.00),
                        ('Donut', 'Dessert', 40.00),
                        ('Cake Slice', 'Dessert', 65.00),
                        ('Ice Cream', 'Dessert', 55.00)
                    ]
                    cursor.executemany(
                        "INSERT INTO cafe_items (item_name, category, price) VALUES (%s, %s, %s)",
                        sample_items
                    )
                    print("✓ Sample cafe items added")
                
                self.db_connection.commit()
                cursor.close()
                print("✓ Database setup complete!")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")


        # main.py

    def open_admin_panel(self):
        """Creates a new Toplevel window for the AdminApp."""
        # Temporarily release global grab to allow admin panel to work
        if self.is_locked:
            self.root.grab_release()
        
        if self.admin_window is None or not self.admin_window.winfo_exists():
            admin_root = tk.Toplevel(self.root)
            admin_root.attributes('-topmost', True)  # Make sure it appears above kiosk mode
            admin_root.overrideredirect(False)  # Keep window decorations
            self.admin_window = admin_root
            self.admin_app_instance = AdminApp(admin_root)
            admin_root.protocol("WM_DELETE_WINDOW", self.on_admin_panel_close)
        else:
            self.admin_window.lift()
            self.admin_window.attributes('-topmost', True)

    def on_admin_panel_close(self):
        """Clean up references when the admin panel is closed."""
        if self.admin_window:
            self.admin_window.destroy()
            self.admin_window = None
            self.admin_app_instance = None
            
            # Restore global grab if still in kiosk mode
            if self.is_locked:
                self.root.grab_set_global()
                self.root.focus_force()    


    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password(self, password):
        """Validate password strength - requires 8+ chars, 1 number, 1 symbol"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        has_number = any(char.isdigit() for char in password)
        if not has_number:
            return False, "Password must contain at least 1 number"
        
        has_symbol = any(not char.isalnum() for char in password)
        if not has_symbol:
            return False, "Password must contain at least 1 special character"
        
        return True, "Password is strong"
    
    def toggle_password_visibility(self, entry, var):
        """Toggle password visibility"""
        if var.get():
            entry.config(show="")
            var.set(False)
        else:
            entry.config(show="●")
            var.set(True)
    
    def should_enable_kiosk_mode(self):
        """Check if kiosk mode should be enabled from database settings"""
        try:
            if not self.db_connection or not self.db_connection.is_connected():
                return True  # Default to enabled for security
                
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_name = 'kiosk_mode_enabled'")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                is_enabled = result['setting_value'].lower() == 'true'
                print(f"🔧 Kiosk mode setting from database: {is_enabled}")
                return is_enabled
            else:
                print("🔧 No kiosk mode setting found, defaulting to enabled")
                return True
                
        except Error as e:
            print(f"🔧 Database error checking kiosk mode: {e}, defaulting to enabled")
            return True
    
    def enable_pc_lock(self):
        """Enable PC lock mode - prevents alt-tab, task manager, etc."""
        try:
            self.is_locked = True
            
            # Force fullscreen and always on top
            self.root.attributes('-fullscreen', True)
            self.root.attributes('-topmost', True)
            self.root.state('zoomed')  # Maximize
            
            # Remove window decorations
            self.root.overrideredirect(True)
            
            # Set window to cover entire screen
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            
            # Force focus and grab
            self.root.focus_force()
            self.root.grab_set_global()  # Global grab prevents other windows
            
            # Hide taskbar if on Windows
            if WINDOWS_LOCK_AVAILABLE:
                self.hide_taskbar()
                self.block_system_keys()
            
            # Bind ALL possible escape keys
            self.bind_all_escape_keys()
            
            # Continuous focus monitoring
            self.monitor_focus()
            
            print("🔒 KIOSK MODE ENABLED - Full screen lock active")
            
        except Exception as e:
            print(f"Error enabling PC lock: {e}")
            self.enable_basic_lock()
    
    def enable_basic_lock(self):
        """Basic lock mode without Windows API - fullscreen only"""
        try:
            self.is_locked = True
            
            # Make window always on top and fullscreen
            self.root.attributes('-topmost', True)
            self.root.attributes('-fullscreen', True)
            self.root.overrideredirect(True)
            self.root.focus_force()
            self.root.grab_set_global()
            
            # Bind basic key blocks
            self.bind_all_escape_keys()
            
            # Monitor focus
            self.monitor_focus()
            
            print("🔒 Basic KIOSK Mode ENABLED - Limited protection active")
            
        except Exception as e:
            print(f"Error enabling basic PC lock: {e}")
    
    def bind_all_escape_keys(self):
        """Bind all possible escape key combinations"""
        escape_keys = [
            '<Alt-Tab>', '<Alt-Shift-Tab>',
            '<Control-Alt-Delete>', '<Control-Alt-Del>',
            '<Control-Shift-Escape>', '<Control-Shift-Esc>',
            '<Alt-F4>', '<Control-F4>',
            '<Control-c>', '<Control-v>', '<Control-x>', '<Control-z>',
            '<Control-s>', '<Control-o>', '<Control-n>',
            '<F1>', '<F2>', '<F3>', '<F4>', '<F5>', '<F6>',
            '<F7>', '<F8>', '<F9>', '<F10>', '<F11>', '<F12>',
            '<Alt-F1>', '<Alt-F2>', '<Alt-F3>', '<Alt-F4>',
            '<Control-w>', '<Control-t>', '<Control-n>',
            '<Super_L>', '<Super_R>',  # Windows keys
            '<Menu>',  # Context menu key
            '<Escape>', '<Alt-Escape>',
            '<Control-Escape>',
            '<Print>', '<Scroll_Lock>', '<Pause>',
            '<Insert>', '<Delete>', '<Home>', '<End>',
            '<Page_Up>', '<Page_Down>',
            '<Control-Insert>', '<Shift-Insert>',
            '<Control-Delete>', '<Shift-Delete>'
        ]
        
        for key in escape_keys:
            try:
                self.root.bind_all(key, self.block_key_event)
            except:
                pass
    
    def unbind_all_escape_keys(self):
        """Unbind all escape key combinations"""
        escape_keys = [
            '<Alt-Tab>', '<Alt-Shift-Tab>',
            '<Control-Alt-Delete>', '<Control-Alt-Del>',
            '<Control-Shift-Escape>', '<Control-Shift-Esc>',
            '<Alt-F4>', '<Control-F4>',
            '<Control-c>', '<Control-v>', '<Control-x>', '<Control-z>',
            '<Control-s>', '<Control-o>', '<Control-n>',
            '<F1>', '<F2>', '<F3>', '<F4>', '<F5>', '<F6>',
            '<F7>', '<F8>', '<F9>', '<F10>', '<F11>', '<F12>',
            '<Alt-F1>', '<Alt-F2>', '<Alt-F3>', '<Alt-F4>',
            '<Control-w>', '<Control-t>', '<Control-n>',
            '<Super_L>', '<Super_R>',
            '<Menu>',
            '<Escape>', '<Alt-Escape>',
            '<Control-Escape>',
            '<Print>', '<Scroll_Lock>', '<Pause>',
            '<Insert>', '<Delete>', '<Home>', '<End>',
            '<Page_Up>', '<Page_Down>',
            '<Control-Insert>', '<Shift-Insert>',
            '<Control-Delete>', '<Shift-Delete>'
        ]
        
        for key in escape_keys:
            try:
                self.root.unbind_all(key)
            except:
                pass
    
    def block_key_event(self, event):
        """Block key events and show warning"""
        print(f"🚫 Blocked key combination: {event.keysym}")
        return "break"
    
    def monitor_focus(self):
        """Continuously monitor and maintain focus"""
        if self.is_locked:
            try:
                # Check if there are any Toplevel windows (dialogs) open
                has_dialogs = any(isinstance(child, tk.Toplevel) for child in self.root.winfo_children())
                
                if not has_dialogs:
                    # Only force focus if no dialogs are open
                    self.root.lift()
                    self.root.focus_force()
                    self.root.attributes('-topmost', True)
                
                # Schedule next check with longer interval to reduce interference
                self.focus_monitor_id = self.root.after(500, self.monitor_focus)
            except:
                pass
    
    def disable_pc_lock(self):
        """Disable PC lock mode - restore normal functionality"""
        try:
            self.is_locked = False
            
            # Stop focus monitoring
            if hasattr(self, 'focus_monitor_id'):
                self.root.after_cancel(self.focus_monitor_id)
            
            # Restore window properties
            self.root.overrideredirect(False)
            self.root.attributes('-topmost', False)
            self.root.attributes('-fullscreen', False)
            self.root.state('zoomed')  # Keep maximized but not fullscreen
            
            # Restore taskbar if on Windows
            if WINDOWS_LOCK_AVAILABLE:
                self.show_taskbar()
                self.unblock_system_keys()
            
            # Release all grabs
            self.root.grab_release()
            
            # Unbind all escape key events
            self.unbind_all_escape_keys()
            
            print("🔓 KIOSK MODE DISABLED - Normal access restored")
            
        except Exception as e:
            print(f"Error disabling PC lock: {e}")
    
    def block_system_keys(self):
        """Block system keys like Alt+Tab, Windows key, etc."""
        if sys.platform != "win32":
            return
            
        try:
            # Block Alt+Tab
            self.block_key(win32con.VK_TAB, win32con.MOD_ALT)
            
            # Block Windows key
            self.block_key(win32con.VK_LWIN)
            self.block_key(win32con.VK_RWIN)
            
            # Block Ctrl+Alt+Del (limited effectiveness)
            self.block_key(win32con.VK_DELETE, win32con.MOD_CONTROL | win32con.MOD_ALT)
            
            # Block Ctrl+Shift+Esc (Task Manager)
            self.block_key(win32con.VK_ESCAPE, win32con.MOD_CONTROL | win32con.MOD_SHIFT)
            
            # Block Alt+F4
            self.block_key(win32con.VK_F4, win32con.MOD_ALT)
            
        except Exception as e:
            print(f"Error blocking system keys: {e}")
    
    def block_key(self, vk_code, modifiers=0):
        """Block a specific key combination"""
        if sys.platform != "win32":
            return
            
        try:
            # Register hotkey to block it
            win32gui.RegisterHotKey(None, 1, modifiers, vk_code)
            self.blocked_keys.append((1, modifiers, vk_code))
        except:
            pass
    
    def unblock_system_keys(self):
        """Unblock all previously blocked keys"""
        if sys.platform != "win32":
            return
            
        try:
            for key_id, modifiers, vk_code in self.blocked_keys:
                try:
                    win32gui.UnregisterHotKey(None, key_id)
                except:
                    pass
            self.blocked_keys.clear()
        except Exception as e:
            print(f"Error unblocking keys: {e}")
    
    def hide_taskbar(self):
        """Hide Windows taskbar"""
        if sys.platform != "win32":
            return
            
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_HIDE)
        except Exception as e:
            print(f"Error hiding taskbar: {e}")
    
    def show_taskbar(self):
        """Show Windows taskbar"""
        if sys.platform != "win32":
            return
            
        try:
            taskbar = win32gui.FindWindow("Shell_TrayWnd", None)
            if taskbar:
                win32gui.ShowWindow(taskbar, win32con.SW_SHOW)
        except Exception as e:
            print(f"Error showing taskbar: {e}")
    
    def on_window_focus_out(self, event):
        """Handle when window loses focus - force it back"""
        if self.is_locked and self.current_user:
            self.root.after(10, lambda: self.root.focus_force())
            self.root.after(10, lambda: self.root.lift())
    
    def prevent_window_close(self):
        """Prevent window from being closed during locked session"""
        if self.is_locked and self.current_user:
            messagebox.showwarning("Session Active", 
                                 "You must logout properly to exit.\n\n"
                                 "Use the Logout button in the menu.")
            return False
        return True
    
    def emergency_unlock(self):
        """Emergency unlock for administrators"""
        if not self.is_locked:
            messagebox.showinfo("PC Lock Status", "PC is not currently locked.")
            return
            
        # Create admin authentication dialog
        unlock_window = tk.Toplevel(self.root)
        unlock_window.title("Emergency Unlock")
        unlock_window.geometry("600x500")
        unlock_window.configure(bg=self.bg_color)
        unlock_window.attributes('-topmost', True)
        unlock_window.grab_set()
        unlock_window.resizable(True, True)
        unlock_window.minsize(550, 450)
        unlock_window.overrideredirect(False)  # Keep window decorations
        
        # Temporarily release global grab
        self.root.grab_release()
        
        # Center the window
        unlock_window.transient(self.root)
        
        container = tk.Frame(unlock_window, bg=self.bg_color)
        container.pack(expand=True, fill='both', padx=30, pady=30)
        
        tk.Label(container, text="🚨 EMERGENCY UNLOCK", font=("Segoe UI", 20, "bold"),
                bg=self.bg_color, fg="#e74c3c").pack(pady=(0, 10))
        
        tk.Label(container, text="Administrator authentication required", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(pady=(0, 25))
        
        # Form frame
        form_frame = tk.Frame(container, bg=self.bg_color)
        form_frame.pack(fill='x', pady=(0, 20))
        
        # Admin credentials form with better visibility
        tk.Label(form_frame, text="Admin Username:", font=("Segoe UI", 14, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack(anchor='w', pady=(0, 10))
        
        admin_user_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=40,
                                   bg=self.secondary_bg, fg=self.text_color, bd=3, relief='solid',
                                   insertbackground=self.text_color, highlightthickness=3,
                                   highlightcolor=self.accent_color)
        admin_user_entry.pack(fill='x', pady=(0, 25), ipady=15)
        
        tk.Label(form_frame, text="Admin Password:", font=("Segoe UI", 14, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack(anchor='w', pady=(0, 10))
        
        # Password frame with show/hide button
        pass_frame = tk.Frame(form_frame, bg=self.bg_color)
        pass_frame.pack(fill='x', pady=(0, 30))
        
        admin_pass_entry = tk.Entry(pass_frame, font=("Segoe UI", 14), show="*",
                                   bg=self.secondary_bg, fg=self.text_color, bd=3, relief='solid',
                                   insertbackground=self.text_color, highlightthickness=3,
                                   highlightcolor=self.accent_color)
        admin_pass_entry.pack(side='left', fill='x', expand=True, ipady=15)
        
        # Show/hide password button
        show_unlock_var = tk.BooleanVar()
        show_unlock_btn = tk.Button(pass_frame, text="👁", font=("Segoe UI", 12),
                                   bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                                   command=lambda: self.toggle_emergency_password(admin_pass_entry, show_unlock_var))
        show_unlock_btn.pack(side='right', padx=(8, 0), ipady=15)
        
        # Buttons
        btn_frame = tk.Frame(container, bg=self.bg_color)
        btn_frame.pack(pady=15)
        
        btn_container = tk.Frame(btn_frame, bg=self.bg_color)
        btn_container.pack()
        
        cancel_unlock_btn = tk.Button(btn_container, text="Cancel", font=("Segoe UI", 12),
                                     bg="#6c757d", fg="white", bd=0, cursor="hand2", 
                                     padx=25, pady=12, command=unlock_window.destroy)
        cancel_unlock_btn.pack(side='left', padx=(0, 15))
        
        unlock_btn = tk.Button(btn_container, text="🔓 UNLOCK PC", font=("Segoe UI", 12, "bold"),
                              bg="#e74c3c", fg="white", bd=0, cursor="hand2", 
                              padx=25, pady=12,
                              command=lambda: self.verify_admin_unlock(
                                  admin_user_entry.get(), admin_pass_entry.get(), unlock_window
                              ))
        unlock_btn.pack(side='left')
        
        # Tab navigation
        admin_user_entry.focus()
        admin_user_entry.bind('<Tab>', lambda e: admin_pass_entry.focus())
        admin_pass_entry.bind('<Tab>', lambda e: cancel_unlock_btn.focus())
        cancel_unlock_btn.bind('<Tab>', lambda e: unlock_btn.focus())
        unlock_btn.bind('<Tab>', lambda e: admin_user_entry.focus())
        
        # Enter key bindings
        admin_user_entry.bind('<Return>', lambda e: admin_pass_entry.focus())
        admin_pass_entry.bind('<Return>', lambda e: self.verify_admin_unlock(
            admin_user_entry.get(), admin_pass_entry.get(), unlock_window
        ))
        
        # Escape to close
        unlock_window.bind('<Escape>', lambda e: unlock_window.destroy())
        
        # Restore grab when dialog is closed
        def on_unlock_close():
            if self.is_locked:
                self.root.grab_set_global()
                self.monitor_focus()  # Restart focus monitoring
            unlock_window.destroy()
        
        unlock_window.protocol("WM_DELETE_WINDOW", on_unlock_close)
        cancel_unlock_btn.config(command=on_unlock_close)
    
    def verify_admin_unlock(self, username, password, window):
        """Verify admin credentials for emergency unlock"""
        if not username or not password:
            messagebox.showerror("Error", "Please enter admin credentials")
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            hashed_pw = self.hash_password(password)
            
            cursor.execute(
                "SELECT * FROM admins WHERE username = %s AND password = %s",
                (username, hashed_pw)
            )
            admin = cursor.fetchone()
            cursor.close()
            
            if admin:
                # Valid admin - disable PC lock
                self.disable_pc_lock()
                window.destroy()
                
                messagebox.showinfo("PC Unlocked", 
                                  f"PC has been unlocked by administrator: {admin['full_name']}\n\n"
                                  f"⚠️ WARNING: User session is still active!\n"
                                  f"User: {self.current_user['full_name']}\n"
                                  f"PC: {self.selected_pc}\n\n"
                                  f"PC Lock mode has been disabled for this session.")
                
                # Update the interface to show unlocked status
                self.show_main_interface()
                
            else:
                messagebox.showerror("Access Denied", "Invalid administrator credentials")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error verifying admin: {e}")
    
    def emergency_exit(self):
        """Emergency exit that requires admin authentication"""
        # Temporarily disable focus monitoring to allow dialog interaction
        if hasattr(self, 'focus_monitor_id'):
            self.root.after_cancel(self.focus_monitor_id)
        
        # Create emergency exit dialog
        exit_window = tk.Toplevel(self.root)
        exit_window.title("🚨 EMERGENCY EXIT")
        exit_window.geometry("700x600")
        exit_window.configure(bg="#2d2d2d")
        exit_window.attributes('-topmost', True)
        exit_window.resizable(True, True)  # Make resizable
        exit_window.minsize(650, 550)  # Set minimum size
        exit_window.overrideredirect(False)  # Keep window decorations for resizing
        
        # Center the window on screen
        screen_width = exit_window.winfo_screenwidth()
        screen_height = exit_window.winfo_screenheight()
        x = (screen_width - 700) // 2
        y = (screen_height - 600) // 2
        exit_window.geometry(f"700x600+{x}+{y}")
        
        # Temporarily release global grab to allow this dialog to work
        self.root.grab_release()
        
        # Main container with scrollable frame
        main_container = tk.Frame(exit_window, bg="#2d2d2d")
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Warning header
        header_frame = tk.Frame(main_container, bg="#2d2d2d")
        header_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(header_frame, text="🚨 EMERGENCY EXIT", font=("Segoe UI", 22, "bold"),
                bg="#2d2d2d", fg="#e74c3c").pack()
        
        tk.Label(header_frame, text="⚠️ WARNING ⚠️", font=("Segoe UI", 16, "bold"),
                bg="#2d2d2d", fg="#FFA726").pack(pady=(5, 0))
        
        # Warning message
        warning_frame = tk.Frame(main_container, bg="#1a1a1a", relief='solid', bd=1)
        warning_frame.pack(fill='x', pady=(0, 20), padx=10)
        
        tk.Label(warning_frame, text="This will completely exit the application", 
                font=("Segoe UI", 12, "bold"), bg="#1a1a1a", fg="white").pack(pady=(10, 5))
        tk.Label(warning_frame, text="and disable all security features.", 
                font=("Segoe UI", 12, "bold"), bg="#1a1a1a", fg="white").pack(pady=(0, 10))
        
        # Auth section
        auth_frame = tk.Frame(main_container, bg="#2d2d2d")
        auth_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(auth_frame, text="Administrator Authentication Required:", 
                font=("Segoe UI", 14, "bold"), bg="#2d2d2d", fg="white").pack(pady=(0, 20))
        
        # Form container for better layout
        form_frame = tk.Frame(auth_frame, bg="#2d2d2d")
        form_frame.pack(fill='x', padx=20)
        
        # Username field with better visibility
        tk.Label(form_frame, text="Admin Username:", font=("Segoe UI", 14, "bold"),
                bg="#2d2d2d", fg="#FFA726").pack(anchor='w', pady=(0, 10))
        
        admin_user_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=45,
                                   bg="#4d4d4d", fg="white", bd=3, relief='solid',
                                   insertbackground="white", highlightthickness=3,
                                   highlightcolor="#8BA888", highlightbackground="#3d3d3d")
        admin_user_entry.pack(fill='x', pady=(0, 25), ipady=15)
        
        # Password field with better visibility
        tk.Label(form_frame, text="Admin Password:", font=("Segoe UI", 14, "bold"),
                bg="#2d2d2d", fg="#FFA726").pack(anchor='w', pady=(0, 10))
        
        # Password frame with show/hide button
        pass_frame = tk.Frame(form_frame, bg="#2d2d2d")
        pass_frame.pack(fill='x', pady=(0, 30))
        
        admin_pass_entry = tk.Entry(pass_frame, font=("Segoe UI", 14), show="*",
                                   bg="#4d4d4d", fg="white", bd=3, relief='solid',
                                   insertbackground="white", highlightthickness=3,
                                   highlightcolor="#8BA888", highlightbackground="#3d3d3d")
        admin_pass_entry.pack(side='left', fill='x', expand=True, ipady=15)
        
        # Show/hide password button
        show_pass_var = tk.BooleanVar()
        show_pass_btn = tk.Button(pass_frame, text="👁", font=("Segoe UI", 12),
                                 bg="#4d4d4d", fg="white", bd=0, cursor="hand2",
                                 command=lambda: self.toggle_emergency_password(admin_pass_entry, show_pass_var))
        show_pass_btn.pack(side='right', padx=(8, 0), ipady=15)
        
        # Buttons with better spacing
        btn_frame = tk.Frame(main_container, bg="#2d2d2d")
        btn_frame.pack(fill='x', pady=(20, 0))
        
        # Button container for centering
        btn_container = tk.Frame(btn_frame, bg="#2d2d2d")
        btn_container.pack()
        
        cancel_btn = tk.Button(btn_container, text="Cancel", font=("Segoe UI", 12),
                              bg="#6c757d", fg="white", bd=0, cursor="hand2", 
                              padx=30, pady=15, command=exit_window.destroy)
        cancel_btn.pack(side='left', padx=(0, 20))
        
        exit_btn = tk.Button(btn_container, text="🚪 EXIT APPLICATION", font=("Segoe UI", 12, "bold"),
                            bg="#e74c3c", fg="white", bd=0, cursor="hand2", 
                            padx=30, pady=15,
                            command=lambda: self.verify_emergency_exit(
                                admin_user_entry.get(), admin_pass_entry.get(), exit_window
                            ))
        exit_btn.pack(side='left')
        
        # Tab order and focus management
        admin_user_entry.focus()
        
        # Bind Tab key for proper navigation
        admin_user_entry.bind('<Tab>', lambda e: admin_pass_entry.focus())
        admin_pass_entry.bind('<Tab>', lambda e: cancel_btn.focus())
        cancel_btn.bind('<Tab>', lambda e: exit_btn.focus())
        exit_btn.bind('<Tab>', lambda e: admin_user_entry.focus())
        
        # Bind Enter key
        admin_user_entry.bind('<Return>', lambda e: admin_pass_entry.focus())
        admin_pass_entry.bind('<Return>', lambda e: self.verify_emergency_exit(
            admin_user_entry.get(), admin_pass_entry.get(), exit_window
        ))
        
        # Bind Escape key to close
        exit_window.bind('<Escape>', lambda e: exit_window.destroy())
        
        # Make sure this dialog stays on top even in lock mode
        exit_window.lift()
        exit_window.focus_force()
        exit_window.grab_set()  # Grab focus for this dialog
        
        # Restore grab when dialog is closed
        def on_dialog_close():
            if self.is_locked:
                self.root.grab_set_global()
                self.monitor_focus()  # Restart focus monitoring
            exit_window.destroy()
        
        exit_window.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Update cancel button to use the same close function
        cancel_btn.config(command=on_dialog_close)
        
        # Store references for the toggle function
        exit_window.admin_pass_entry = admin_pass_entry
        exit_window.show_pass_var = show_pass_var
    
    def toggle_emergency_password(self, entry, var):
        """Toggle password visibility in emergency dialog"""
        if var.get():
            entry.config(show="")
            var.set(False)
        else:
            entry.config(show="*")
            var.set(True)
    
    def verify_emergency_exit(self, username, password, window):
        """Verify admin credentials for emergency exit"""
        if not username or not password:
            messagebox.showerror("Error", "Please enter admin credentials", parent=window)
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            hashed_pw = self.hash_password(password)
            
            cursor.execute(
                "SELECT * FROM admins WHERE username = %s AND password = %s",
                (username, hashed_pw)
            )
            admin = cursor.fetchone()
            cursor.close()
            
            if admin:
                # Valid admin - emergency exit
                window.destroy()
                
                # Show final confirmation
                if messagebox.askyesno("FINAL CONFIRMATION", 
                                     f"Emergency exit authorized by: {admin['full_name']}\n\n"
                                     f"⚠️ This will:\n"
                                     f"• Close the application completely\n"
                                     f"• Disable all PC lock features\n"
                                     f"• Log out any active users\n"
                                     f"• Restore normal system access\n\n"
                                     f"Are you absolutely sure?"):
                    
                    # Disable PC lock first
                    self.disable_pc_lock()
                    
                    # Log out current user if any
                    if self.current_user:
                        self.logout()
                    
                    try:
                        # Force close application immediately
                        print("🚨 EMERGENCY EXIT ACTIVATED - Closing application")
                        
                        # Disable all event processing
                        self.root.quit()
                        
                        # Destroy the window
                        self.root.destroy()
                        
                        # Force exit
                        os._exit(0)
                        
                    except:
                        # Fallback exit method
                        sys.exit(0)
                
            else:
                messagebox.showerror("Access Denied", "Invalid administrator credentials", parent=window)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error verifying admin: {e}", parent=window)
    
    def refresh_db_connection(self):
        """Refresh database connection"""
        try:
            if self.db_connection and self.db_connection.is_connected():
                # Consume any unread results
                try:
                    cursor = self.db_connection.cursor()
                    cursor.fetchall()  # Consume any unread results
                    cursor.close()
                except:
                    pass
                self.db_connection.commit()
        except Error:
            self.setup_database()
    
    def show_pc_selection(self):
        """NEW: Display PC selection screen with LOCK status"""
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title with ORIGINAL style
        title_frame = tk.Frame(container, bg=self.bg_color)
        title_frame.pack(pady=(0, 10))
        
        tk.Label(title_frame, text="Star", font=("Segoe UI", 48, "bold"),
                bg=self.bg_color, fg=self.dark_brown).pack(side='left')
        
        tk.Label(title_frame, text="broke", font=("Segoe UI", 48, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side='left')
        
        tk.Label(container, text="Select Your PC Station ☕", font=("Segoe UI", 18),
                bg=self.bg_color, fg=self.text_secondary).pack(pady=(0, 10))
        
        # Kiosk mode indicator
        kiosk_frame = tk.Frame(container, bg="#e74c3c", padx=15, pady=8)
        kiosk_frame.pack(pady=(0, 20))
        
        tk.Label(kiosk_frame, text="🔒 KIOSK MODE ACTIVE", font=("Segoe UI", 12, "bold"),
                bg="#e74c3c", fg="white").pack(side='left')
        
        tk.Label(kiosk_frame, text="• Alt+Tab Disabled • System Keys Blocked • Secure Mode", 
                font=("Segoe UI", 9), bg="#e74c3c", fg="white").pack(side='left', padx=(10, 0))
        
        # Admin and Emergency buttons
        admin_frame = tk.Frame(container, bg=self.bg_color)
        admin_frame.pack(fill='x', pady=(0, 20))
        
        tk.Button(admin_frame, text="🚨 Emergency Exit", font=("Segoe UI", 11, "bold"),
                bg="#e74c3c", fg="white", bd=0, cursor="hand2",
                command=self.emergency_exit, padx=20, pady=10).pack(side='right', padx=(0, 10))
        
        tk.Button(admin_frame, text="🔒 Admin Panel", font=("Segoe UI", 11, "bold"),
                bg=self.light_brown, fg=self.dark_brown, bd=0, cursor="hand2",
                command=self.open_admin_panel, padx=20, pady=10).pack(side='right')
        
        # PC Grid with ORIGINAL styling
        pc_frame = tk.Frame(container, bg=self.bg_color)
        pc_frame.pack(fill='both', expand=True)
        
        try:
            self.refresh_db_connection()
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pc_units ORDER BY unit_name")
            pc_units = cursor.fetchall()
            cursor.close()
            
            for i, pc in enumerate(pc_units[:10]):
                row = i // 5
                col = i % 5
                
                pc_btn_frame = tk.Frame(pc_frame, bg=self.secondary_bg, relief='flat', bd=0,
                                    width=180, height=140)
                pc_btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
                pc_btn_frame.pack_propagate(False)
                
                # Check if PC is locked and determine status
                is_locked = pc.get('is_locked', False)
                
                # Enhanced status display with lock information
                if is_locked:
                    status_color = "#6c757d"  # Gray for locked
                    status_text = "🔒 Admin Locked"
                    btn_state = 'disabled'
                    tooltip_text = "This PC has been locked by an administrator"
                elif pc['status'] == 'Available':
                    status_color = self.accent_color  # Sage green
                    status_text = "✅ Available"
                    btn_state = 'normal'
                    tooltip_text = "Click to login to this PC"
                elif pc['status'] == 'Occupied':
                    status_color = "#FFA726"  # Orange
                    status_text = "👤 In Use"
                    btn_state = 'disabled'
                    tooltip_text = "This PC is currently being used"
                elif pc['status'] == 'Offline':
                    status_color = "#e74c3c"  # Red
                    status_text = "⚠️ Offline"
                    btn_state = 'disabled'
                    tooltip_text = "This PC is offline"
                elif pc['status'] == 'Maintenance':
                    status_color = "#9C27B0"  # Purple
                    status_text = "🔧 Maintenance"
                    btn_state = 'disabled'
                    tooltip_text = "This PC is under maintenance"
                else:
                    status_color = "#e74c3c"  # Red
                    status_text = pc['status']
                    btn_state = 'disabled'
                    tooltip_text = f"PC status: {pc['status']}"
                
                # Icon - centered
                icon_frame = tk.Frame(pc_btn_frame, bg=self.secondary_bg)
                icon_frame.pack(pady=(15, 5))
                tk.Label(icon_frame, text="     🖥️", font=("Segoe UI", 40),
                        bg=self.secondary_bg).pack()
                
                # PC name - centered
                tk.Label(pc_btn_frame, text=pc['unit_name'], font=("Segoe UI", 14, "bold"),
                        bg=self.secondary_bg, fg=self.text_color).pack()
                
                # Status badge - centered
                status_badge = tk.Label(pc_btn_frame, text=status_text,
                                    font=("Segoe UI", 9, "bold"),
                                    bg=status_color, fg="#FFFFFF",
                                    padx=10, pady=3)
                status_badge.pack(pady=(5, 0))
                
                # Make clickable only if not locked and available
                if btn_state == 'normal':
                    pc_btn_frame.bind("<Button-1>", lambda e, pc_name=pc['unit_name']: self.select_pc(pc_name))
                    pc_btn_frame.config(cursor="hand2")
                    for child in pc_btn_frame.winfo_children():
                        child.bind("<Button-1>", lambda e, pc_name=pc['unit_name']: self.select_pc(pc_name))
                        child.config(cursor="hand2")
                
                self.pc_frames_data[pc['unit_name']] = {
                    'frame': pc_btn_frame,
                    'pc_data': pc
                }
            
            for i in range(2):
                pc_frame.grid_rowconfigure(i, weight=1)
            for i in range(5):
                pc_frame.grid_columnconfigure(i, weight=1)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading PCs: {e}")
        
        # Refresh button
        refresh_btn = tk.Button(container, text="↻ Refresh Status", font=("Segoe UI", 11),
                            bg=self.primary_btn, fg=self.secondary_bg, bd=0,
                            cursor="hand2", padx=20, pady=10,
                            command=self.show_pc_selection)
        refresh_btn.pack(pady=20)
        
        # Auto-refresh
        self.root.after(5000, self.refresh_pc_data)
        
    def refresh_pc_data(self):
        """NEW: Auto-refresh PC status"""
        try:
            if hasattr(self, 'pc_frames_data') and self.pc_frames_data:
                self.refresh_db_connection()
                # Refresh logic here (simplified for space)
                self.root.after(5000, self.refresh_pc_data)
        except:
            pass
    
    def select_pc(self, pc_name):
        """Select PC and check if locked before proceeding"""
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pc_units WHERE unit_name = %s", (pc_name,))
            pc = cursor.fetchone()
            cursor.close()
            
            if pc:
                # Check if PC is locked by admin
                if pc.get('is_locked', False):
                    messagebox.showwarning("🔒 PC Access Restricted", 
                                        f"{pc_name} has been locked by the administrator.\n\n"
                                        "This PC is currently unavailable for use.\n"
                                        "Please contact an administrator or try another PC.")
                    return
                
                # Check if PC is available
                if pc['status'] != 'Available':
                    status_messages = {
                        'Occupied': f"{pc_name} is currently being used by another user.",
                        'Offline': f"{pc_name} is offline and unavailable.",
                        'Maintenance': f"{pc_name} is under maintenance."
                    }
                    messagebox.showwarning("PC Unavailable", 
                                        status_messages.get(pc['status'], 
                                        f"{pc_name} is currently {pc['status'].lower()}."))
                    return
                
                # PC is available and unlocked - proceed to login
                self.selected_pc = pc_name
                self.show_login_screen()
            else:
                messagebox.showerror("Error", "PC not found in system")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error accessing PC data: {e}")
    
    
    def show_login_screen(self):
        """Display login with ORIGINAL styling"""
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_frame = tk.Frame(container, bg=self.bg_color)
        title_frame.pack(pady=(0, 10))
        
        tk.Label(title_frame, text="Star", font=("Segoe UI", 48, "bold"),
                bg=self.bg_color, fg=self.dark_brown).pack(side='left')
        
        tk.Label(title_frame, text="broke", font=("Segoe UI", 48, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side='left')
        
        tk.Label(container, text=f"Login to {self.selected_pc} 💻", font=("Segoe UI", 16),
                bg=self.bg_color, fg=self.accent_color).pack(pady=(5, 40))
        
        # Login form
        login_frame = tk.Frame(container, bg=self.secondary_bg, padx=50, pady=40)
        login_frame.pack()
        
        # Username field
        tk.Label(login_frame, text="Username", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        username_entry = tk.Entry(login_frame, font=("Segoe UI", 12), width=30,
                                 bg="#FAF5EF", fg=self.text_color,
                                 insertbackground=self.text_color, bd=0, relief='flat')
        username_entry.grid(row=1, column=0, columnspan=2, pady=(0, 20), ipady=10, sticky='ew')
        
        # Password field with show/hide button
        tk.Label(login_frame, text="Password", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color).grid(row=2, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        password_frame = tk.Frame(login_frame, bg=self.secondary_bg)
        password_frame.grid(row=3, column=0, columnspan=2, pady=(0, 30), sticky='ew')
        
        password_entry = tk.Entry(password_frame, font=("Segoe UI", 12), width=25, show="●",
                                 bg="#FAF5EF", fg=self.text_color,
                                 insertbackground=self.text_color, bd=0, relief='flat')
        password_entry.pack(side='left', ipady=10, fill='x', expand=True)
        
        show_password_var = tk.BooleanVar()
        show_btn = tk.Button(password_frame, text="👁", font=("Segoe UI", 10),
                            bg="#FAF5EF", fg=self.text_color, bd=0, cursor="hand2",
                            command=lambda: self.toggle_password_visibility(password_entry, show_password_var))
        show_btn.pack(side='right', padx=(5, 0), ipady=10)
        
        # Login button
        tk.Button(login_frame, text="LOGIN", font=("Segoe UI", 12, "bold"),
                 bg=self.primary_btn, fg=self.secondary_bg, bd=0, cursor="hand2",
                 activebackground="#7A9977", activeforeground=self.secondary_bg,
                 command=lambda: self.login(username_entry.get(), password_entry.get())).grid(
                     row=4, column=0, columnspan=2, sticky='ew', ipady=12)
        
        # Back and Emergency Exit buttons
        button_frame = tk.Frame(login_frame, bg=self.secondary_bg)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(15, 0))
        
        tk.Button(button_frame, text="← Back to PC Selection", font=("Segoe UI", 10),
                 bg=self.secondary_bg, fg=self.accent_color, bd=0, cursor="hand2",
                 command=self.show_pc_selection).pack(side='left', padx=(0, 20))
        
        tk.Button(button_frame, text="🚨 Emergency Exit", font=("Segoe UI", 10, "bold"),
                 bg="#e74c3c", fg="white", bd=0, cursor="hand2",
                 command=self.emergency_exit).pack(side='left')
        
        # Configure grid weights
        login_frame.grid_columnconfigure(0, weight=1)
        
        password_entry.bind('<Return>', lambda e: self.login(username_entry.get(), password_entry.get()))
    
    def login(self, username, password):
        """Authenticate user and assign PC with enhanced security checks"""
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password")
            return
        
        # Input validation
        if len(username.strip()) < 3:
            messagebox.showerror("Login Error", "Username must be at least 3 characters")
            return
            
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            hashed_pw = self.hash_password(password)
            
            # Check user credentials
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username.strip(), hashed_pw)
            )
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                messagebox.showerror("Authentication Failed", 
                                   "Invalid username or password.\n\n"
                                   "Please check your credentials and try again.")
                return
            
            # Check if account is approved
            if not user['is_approved']:
                cursor.close()
                messagebox.showwarning("Account Pending Approval",
                                     "Your account is waiting for administrator approval.\n\n"
                                     "Please contact an administrator to activate your account.")
                return
            
            # Check if user has sufficient balance
            if user['account_balance'] <= 0:
                cursor.close()
                messagebox.showwarning("Insufficient Balance",
                                     f"Your account balance is ₱{user['account_balance']:.2f}.\n\n"
                                     "Please add funds to your account before using the system.")
                return
            
            # Double-check PC availability and lock status before assignment
            cursor.execute("SELECT * FROM pc_units WHERE unit_name = %s", (self.selected_pc,))
            pc_check = cursor.fetchone()
            
            if not pc_check:
                cursor.close()
                messagebox.showerror("PC Error", "Selected PC not found in system")
                self.show_pc_selection()
                return
                
            if pc_check.get('is_locked', False):
                cursor.close()
                messagebox.showwarning("PC Locked", 
                                     f"{self.selected_pc} has been locked by administrator.\n\n"
                                     "Please select another PC.")
                self.show_pc_selection()
                return
                
            if pc_check['status'] != 'Available':
                cursor.close()
                messagebox.showwarning("PC Unavailable", 
                                     f"{self.selected_pc} is no longer available.\n\n"
                                     "Please select another PC.")
                self.show_pc_selection()
                return
            
            # Assign PC to user
            cursor.execute("""
                UPDATE pc_units
                SET status = 'Occupied', current_user_id = %s, session_start = NOW()
                WHERE unit_name = %s AND status = 'Available' AND (is_locked = FALSE OR is_locked IS NULL)
            """, (user['user_id'], self.selected_pc))
            
            if cursor.rowcount == 0:
                cursor.close()
                messagebox.showerror("Assignment Failed", 
                                   f"Could not assign {self.selected_pc}.\n\n"
                                   "The PC may have been locked or occupied by another user.")
                self.show_pc_selection()
                return
            
            self.db_connection.commit()
            cursor.close()
            
            # Successful login
            self.current_user = user
            
            # Check if kiosk mode should be enabled for this session
            kiosk_enabled = self.should_enable_kiosk_mode()
            if kiosk_enabled:
                # Keep PC lock enabled for user session
                security_msg = (f"🔒 PC LOCK MODE: ENABLED\n"
                               f"• Alt+Tab is disabled\n"
                               f"• Task Manager is blocked\n"
                               f"• Window switching is prevented\n"
                               f"• Use 'Emergency Unlock' if needed\n\n"
                               f"Your session is now secured.")
            else:
                # Disable PC lock for normal operation
                self.disable_pc_lock()
                security_msg = (f"🔓 PC LOCK MODE: DISABLED\n"
                               f"• Normal window behavior\n"
                               f"• System keys are functional\n"
                               f"• Reduced security mode active")
            
            messagebox.showinfo("Login Successful", 
                              f"Welcome, {user['full_name']}!\n\n"
                              f"You are now logged into {self.selected_pc}\n"
                              f"Account Balance: ₱{user['account_balance']:.2f}\n\n"
                              f"{security_msg}")
            
            self.show_main_interface()
                
        except Error as e:
            messagebox.showerror("Database Error", f"Login failed due to database error:\n{e}")
            try:
                self.db_connection.rollback()
            except:
                pass
    
    def show_main_interface(self):
        """Display main interface with enhanced security"""
        # Final authentication check before showing interface
        if not self.check_authentication():
            return
            
        self.clear_window()
        
        # Top bar with security indicator
        top_bar = tk.Frame(self.root, bg=self.secondary_bg, height=80)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(top_bar, bg=self.secondary_bg)
        logo_frame.pack(side='left', padx=30, pady=20)
        
        tk.Label(logo_frame, text="Star", font=("Segoe UI", 20, "bold"),
                bg=self.secondary_bg, fg=self.dark_brown).pack(side='left')
        
        tk.Label(logo_frame, text="broke", font=("Segoe UI", 20, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(side='left')
        
        tk.Label(logo_frame, text=f"• {self.selected_pc}", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.accent_color).pack(side='left', padx=(10, 0))
        
        # Session info
        session_frame = tk.Frame(logo_frame, bg=self.secondary_bg)
        session_frame.pack(side='left', padx=(15, 0))
        
        tk.Label(session_frame, text="🔐", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.accent_color).pack(side='left')
        
        tk.Label(session_frame, text="Secure Session", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.accent_color).pack(side='left', padx=(5, 0))
        
        # User info
        user_frame = tk.Frame(top_bar, bg=self.secondary_bg)
        user_frame.pack(side='right', padx=30, pady=20)
        
        avatar = tk.Label(user_frame, text=self.current_user['username'][0].upper(),
                         font=("Segoe UI", 14, "bold"),
                         bg=self.accent_color, fg=self.secondary_bg,
                         width=3, height=1, bd=0, relief='flat')
        avatar.pack(side='left', padx=(0, 10))
        
        user_info = tk.Frame(user_frame, bg=self.secondary_bg)
        user_info.pack(side='left')
        
        tk.Label(user_info, text=self.current_user['username'],
                font=("Segoe UI", 12, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w')
        
        tk.Label(user_info, text=f"Balance: ₱{self.current_user['account_balance']:.2f}",
                font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_secondary).pack(anchor='w')
        
        # Main content
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_frame, bg=self.secondary_bg, width=180)
        sidebar.pack(side='left', fill='y', padx=(20, 0), pady=20)
        sidebar.pack_propagate(False)
        
        # Content
        content = tk.Frame(main_frame, bg=self.bg_color)
        content.pack(side='left', fill='both', expand=True, padx=20, pady=20)
        
        # Navigation
        tk.Label(sidebar, text="Menu", font=("Segoe UI", 14, "bold"),
                bg=self.secondary_bg, fg=self.text_color, anchor='w').pack(
                    fill='x', padx=20, pady=(10, 20))
        
        nav_buttons = [
            ("🏠 Home", lambda: self.show_frame(HomeFrame)),
            ("☕ Coffee", lambda: self.show_frame(CafeFrame)),
            ("👤 Account", lambda: self.show_frame(AccountsFrame)),
            ("🚪 Logout", self.logout)
        ]
        
        for text, command in nav_buttons:
            tk.Button(sidebar, text=text, font=("Segoe UI", 11),
                     bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                     anchor='w', activebackground=self.light_brown,
                     activeforeground=self.dark_brown,
                     command=command).pack(fill='x', padx=15, pady=2, ipady=12)
        
        self.content_frame = content
        self.show_frame(HomeFrame)
        
        # NEW: Start billing system
        self.start_billing_system()
    
    def check_authentication(self):
        """Check if user is properly authenticated and PC is assigned"""
        if not self.current_user:
            messagebox.showerror("Authentication Required", 
                               "You must be logged in to access this feature.\n\n"
                               "Please log in first.")
            self.show_pc_selection()
            return False
            
        if not self.selected_pc:
            messagebox.showerror("PC Assignment Required", 
                               "No PC assigned to your session.\n\n"
                               "Please select and log into a PC first.")
            self.show_pc_selection()
            return False
            
        # Verify PC is still assigned to this user
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT status, current_user_id, is_locked 
                FROM pc_units 
                WHERE unit_name = %s
            """, (self.selected_pc,))
            pc_status = cursor.fetchone()
            cursor.close()
            
            if not pc_status:
                messagebox.showerror("PC Error", "Your assigned PC is no longer available.")
                self.logout()
                return False
                
            if pc_status.get('is_locked', False):
                messagebox.showwarning("PC Locked", 
                                     f"Your PC ({self.selected_pc}) has been locked by administrator.\n\n"
                                     "Your session will be ended.")
                self.logout()
                return False
                
            if pc_status['current_user_id'] != self.current_user['user_id']:
                messagebox.showerror("Session Invalid", 
                                   "Your PC session is no longer valid.\n\n"
                                   "You will be logged out.")
                self.logout()
                return False
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error verifying session: {e}")
            return False
            
        return True
    
    def show_frame(self, frame_class):
        """Display selected frame with authentication check"""
        # Check authentication before showing any frame
        if not self.check_authentication():
            return
            
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        frame = frame_class(self.content_frame, self)
        frame.pack(fill='both', expand=True)
    
    def start_billing_system(self):
        """NEW: Time-based billing"""
        if self.current_user and self.selected_pc:
            self.root.after(60000, self.process_billing)
    
    def process_billing(self):
        """Process per-minute billing with enhanced security checks"""
        if not self.current_user or not self.selected_pc:
            return
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT pc.session_start, pc.is_locked, pc.status, pc.current_user_id,
                       u.hourly_rate, u.account_balance, u.session_time_limit
                FROM pc_units pc
                JOIN users u ON pc.current_user_id = u.user_id
                WHERE pc.unit_name = %s AND pc.current_user_id = %s
            """, (self.selected_pc, self.current_user['user_id']))
            
            session_data = cursor.fetchone()
            
            if not session_data:
                print("⚠️ Session data not found - logging out user")
                cursor.close()
                self.logout()
                return
            
            # Check if PC has been locked by admin
            if session_data.get('is_locked', False):
                cursor.close()
                messagebox.showwarning("PC Locked by Administrator", 
                                     f"Your PC ({self.selected_pc}) has been locked by an administrator.\n\n"
                                     "Your session will be ended immediately.")
                self.logout()
                return
            
            # Check if PC status changed
            if session_data['status'] != 'Occupied':
                cursor.close()
                messagebox.showwarning("Session Interrupted", 
                                     f"Your PC session has been interrupted.\n\n"
                                     "You will be logged out.")
                self.logout()
                return
            
            # Check if session is still valid
            if session_data['current_user_id'] != self.current_user['user_id']:
                cursor.close()
                messagebox.showerror("Session Conflict", 
                                   "Your session has been taken over by another process.\n\n"
                                   "You will be logged out for security reasons.")
                self.logout()
                return
            
            if session_data and session_data['session_start']:
                from datetime import datetime
                
                duration = datetime.now() - session_data['session_start']
                elapsed_minutes = int(duration.total_seconds() / 60)
                
                cost_per_minute = float(session_data['hourly_rate']) / 60
                current_balance = float(session_data['account_balance'])
                
                # Check for insufficient balance
                if current_balance <= 0:
                    cursor.close()
                    messagebox.showwarning("Session Ended - Insufficient Balance", 
                                         "Your account balance has reached zero.\n\n"
                                         "Please add funds to continue using the system.")
                    self.logout()
                    return
                
                # Deduct usage cost
                new_balance = max(0, current_balance - cost_per_minute)
                
                cursor.execute(
                    "UPDATE users SET account_balance = %s WHERE user_id = %s",
                    (new_balance, self.current_user['user_id'])
                )
                
                self.current_user['account_balance'] = new_balance
                self.db_connection.commit()
                
                # Check time limit
                if elapsed_minutes >= session_data['session_time_limit']:
                    cursor.close()
                    messagebox.showinfo("Session Time Expired", 
                                      f"Your {session_data['session_time_limit']}-minute session has expired.\n\n"
                                      "Thank you for using Starbroke!")
                    self.logout()
                    return
                
                # Warn user when balance is low
                if new_balance <= 50 and new_balance > 0:  # Warn when balance is ₱50 or less
                    remaining_minutes = int(new_balance / cost_per_minute)
                    if remaining_minutes <= 10:  # Only show warning if less than 10 minutes left
                        messagebox.showwarning("Low Balance Warning", 
                                             f"Your balance is running low: ₱{new_balance:.2f}\n\n"
                                             f"Approximately {remaining_minutes} minutes remaining.\n"
                                             "Please add funds to avoid session interruption.")
            
            cursor.close()
            # Schedule next billing cycle
            self.root.after(60000, self.process_billing)
            
        except Error as e:
            print(f"Billing error: {e}")
            # Continue billing cycle even if there's an error
            self.root.after(60000, self.process_billing)
    
    def logout(self):
        """Secure logout with session cleanup and PC release"""
        session_summary_shown = False
        
        if self.current_user and self.selected_pc:
            try:
                cursor = self.db_connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT pc.session_start, u.hourly_rate, u.account_balance
                    FROM pc_units pc
                    JOIN users u ON pc.current_user_id = u.user_id
                    WHERE pc.unit_name = %s AND pc.current_user_id = %s
                """, (self.selected_pc, self.current_user['user_id']))
                
                session_data = cursor.fetchone()
                
                if session_data and session_data['session_start']:
                    from datetime import datetime
                    duration = datetime.now() - session_data['session_start']
                    elapsed_minutes = int(duration.total_seconds() / 60)
                    hourly_rate = float(session_data['hourly_rate'])
                    total_cost = elapsed_minutes * (hourly_rate / 60)
                    
                    hours, minutes = divmod(elapsed_minutes, 60)
                    
                    # Show session summary
                    summary_msg = f"Session Summary for {self.current_user['full_name']}\n"
                    summary_msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    summary_msg += f"PC Used: {self.selected_pc}\n"
                    summary_msg += f"Session Time: {hours}h {minutes}m\n"
                    summary_msg += f"Hourly Rate: ₱{hourly_rate:.2f}/hour\n"
                    summary_msg += f"Session Cost: ₱{total_cost:.2f}\n"
                    summary_msg += f"Final Balance: ₱{session_data['account_balance']:.2f}\n\n"
                    summary_msg += f"Thank you for using Starbroke!"
                    
                    messagebox.showinfo("Session Complete", summary_msg)
                    session_summary_shown = True
                
                # Release PC and clear session
                cursor.execute("""
                    UPDATE pc_units
                    SET status = 'Available', current_user_id = NULL, session_start = NULL
                    WHERE unit_name = %s
                """, (self.selected_pc,))
                
                self.db_connection.commit()
                cursor.close()
                
                print(f"✓ User {self.current_user['username']} logged out from {self.selected_pc}")
                
            except Error as e:
                print(f"Logout error: {e}")
                try:
                    # Attempt to release PC even if session data retrieval failed
                    cursor = self.db_connection.cursor()
                    cursor.execute("""
                        UPDATE pc_units
                        SET status = 'Available', current_user_id = NULL, session_start = NULL
                        WHERE unit_name = %s
                    """, (self.selected_pc,))
                    self.db_connection.commit()
                    cursor.close()
                except:
                    pass
        
        # Clear user session data
        user_name = self.current_user['full_name'] if self.current_user else "User"
        pc_name = self.selected_pc if self.selected_pc else "PC"
        
        self.current_user = None
        self.selected_pc = None
        
        # Show logout confirmation if session summary wasn't shown
        if not session_summary_shown:
            messagebox.showinfo("Logged Out", 
                              f"You have been successfully logged out.\n\n"
                              f"Thank you for using Starbroke!")
        
        # Return to PC selection screen and re-enable PC lock
        self.show_pc_selection()
        self.enable_pc_lock()
    
    def clear_window(self):
        """Clear all widgets from main window ONLY (don't touch Toplevel windows)"""
        for widget in self.root.winfo_children():
            # Skip Toplevel windows (like admin panel)
            if not isinstance(widget, tk.Toplevel):
                widget.destroy()
    
    def __del__(self):
        """Close database connection"""
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = CafeSystemApp(root)
    root.mainloop()