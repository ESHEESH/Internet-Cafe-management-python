import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import hashlib
import os
import shutil
from PIL import Image, ImageTk
from datetime import datetime

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Starbroke - Admin Panel")
        
        # Only maximize and set minsize if it's a standalone window
        # Check if root is a Toplevel (separate window) or main Tk window
        if isinstance(self.root, tk.Tk):
            self.root.state('zoomed')
            self.root.minsize(1024, 768)
        else:
            # It's a Toplevel window - make sure it appears above kiosk mode
            self.root.geometry("1200x800")
            self.root.minsize(1024, 768)
            self.root.attributes('-topmost', True)
            self.root.overrideredirect(False)
        
        # Color scheme (darker for admin)
        self.bg_color = "#1a1a1a"
        self.secondary_bg = "#2d2d2d"
        self.accent_color = "#8BA888"  # Sage green
        self.text_color = "#ffffff"
        self.text_secondary = "#a0a0a0"
        self.success_color = "#4CAF50"
        self.warning_color = "#FFA726"
        self.danger_color = "#e74c3c"
        
        self.root.configure(bg=self.bg_color)
        
        self.current_admin = None
        self.db_connection = None
        self.admin_pc_frames_data = {}
        
        # Create images directory if it doesn't exist
        self.images_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
            print(f"✅ Created images directory at: {self.images_dir}")
        
        self.setup_database()
        self.show_admin_login()
    
    def setup_database(self):
        """Setup database connection"""
        try:
            self.db_connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='internet_cafe',
                use_pure=True  # Fix for authentication plugin issue
            )
            
            if self.db_connection.is_connected():
                cursor = self.db_connection.cursor()
                
                # Create admins table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admins (
                        admin_id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        full_name VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create default admin if none exists
                cursor.execute("SELECT COUNT(*) FROM admins")
                if cursor.fetchone()[0] == 0:
                    default_password = hashlib.sha256("admin123".encode()).hexdigest()
                    cursor.execute(
                        "INSERT INTO admins (username, password, full_name) VALUES (%s, %s, %s)",
                        ('admin', default_password, 'System Administrator')
                    )
                    print("Default admin created - Username: admin, Password: admin123")
                
                # Check if image_path column exists
                cursor.execute("SHOW COLUMNS FROM cafe_items LIKE 'image_path'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE cafe_items ADD COLUMN image_path VARCHAR(255) DEFAULT NULL")
                    print("✓ Added image_path column to cafe_items")
                
                # Create inventory_items table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS inventory_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) DEFAULT NULL,
                        quantity INT DEFAULT 0,
                        unit_price DECIMAL(10,2) DEFAULT 0.00,
                        min_stock_level INT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                print("✓ Inventory table created/verified")
                
                self.db_connection.commit()
                cursor.close()
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
    
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
            entry.config(show="*")
            var.set(True)
    
    def refresh_db_connection(self):
        """Refresh database connection to ensure fresh data"""
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
    
    def clear_window(self):
        """Clear all widgets from root window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def clear_content(self, parent):
        """Clear content from a specific parent widget"""
        for widget in parent.winfo_children():
            widget.destroy()
    
    def show_admin_login(self):
        """Display admin login screen"""
        self.clear_window()
        
        container = tk.Frame(self.root, bg=self.bg_color)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        title = tk.Label(container, text="Starbroke Admin", font=("Segoe UI", 48, "bold"),
                        bg=self.bg_color, fg=self.accent_color)
        title.pack(pady=(0, 10))
        
        subtitle = tk.Label(container, text="Administration Panel", font=("Segoe UI", 14),
                           bg=self.bg_color, fg=self.text_secondary)
        subtitle.pack(pady=(0, 40))
        
        login_frame = tk.Frame(container, bg=self.secondary_bg, padx=50, pady=40)
        login_frame.pack()
        
        tk.Label(login_frame, text="Admin Username", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        username_entry = tk.Entry(login_frame, font=("Segoe UI", 12), width=30, bg="#3d3d3d",
                                 fg=self.text_color, insertbackground=self.text_color, bd=0)
        username_entry.grid(row=1, column=0, pady=(0, 20), ipady=8)
        
        tk.Label(login_frame, text="Password", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).grid(row=2, column=0, sticky='w', pady=(0, 5))
        
        password_entry = tk.Entry(login_frame, font=("Segoe UI", 12), width=30, show="*",
                                 bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        password_entry.grid(row=3, column=0, pady=(0, 30), ipady=8)
        
        login_btn = tk.Button(login_frame, text="LOGIN AS ADMIN", font=("Segoe UI", 12, "bold"),
                             bg=self.accent_color, fg=self.secondary_bg, bd=0, cursor="hand2",
                             command=lambda: self.admin_login(username_entry.get(), password_entry.get()))
        login_btn.grid(row=4, column=0, sticky='ew', ipady=10)
        
        info_label = tk.Label(login_frame, text="Default: admin / admin123", 
                            font=("Segoe UI", 9), bg=self.secondary_bg, fg=self.text_secondary)
        info_label.grid(row=5, column=0, pady=(15, 0))
        
        password_entry.bind('<Return>', lambda e: self.admin_login(username_entry.get(), password_entry.get()))
    
    def admin_login(self, username, password):
        """Authenticate admin"""
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
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
                self.current_admin = admin
                self.show_admin_dashboard()
            else:
                messagebox.showerror("Error", "Invalid admin credentials")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error during login: {e}")
    
    def show_admin_dashboard(self):
        """Display admin dashboard"""
        self.clear_window()
        
        # Top bar
        top_bar = tk.Frame(self.root, bg=self.secondary_bg, height=70)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)
        
        tk.Label(top_bar, text="Starbroke Admin", font=("Segoe UI", 24, "bold"),
                bg=self.secondary_bg, fg=self.accent_color).pack(side='left', padx=30)
        
        tk.Label(top_bar, text=f"Admin: {self.current_admin['full_name']}",
                font=("Segoe UI", 14), bg=self.secondary_bg, fg=self.text_color).pack(side='right', padx=30)
        
        # Sidebar
        sidebar = tk.Frame(self.root, bg=self.secondary_bg, width=220)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # Content area
        content = tk.Frame(self.root, bg=self.bg_color)
        content.pack(side='left', fill='both', expand=True)
        
        # Navigation buttons
        nav_buttons = [
            ("🖥️ PC Overview", lambda: self.show_pc_overview(content)),
            ("📦 Order Management", lambda: self.show_order_management(content)),
            ("📊 Inventory", lambda: self.show_inventory_management(content)),
            ("☕ Manage Menu", lambda: self.show_menu_items(content)),
            ("➕ Create Account", lambda: self.show_account_creation(content)),
            ("⏳ Pending Accounts", lambda: self.show_pending_accounts(content)),
            ("👥 All Users", lambda: self.show_all_users(content)),
            ("📋 All Orders", lambda: self.show_all_orders(content)),
            ("🔒 Kiosk Mode Control", lambda: self.show_kiosk_control(content)),
            ("🚪 Logout", self.show_admin_login)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(sidebar, text=text, font=("Segoe UI", 11), bg=self.secondary_bg,
                          fg=self.text_color, bd=0, cursor="hand2", anchor='w', padx=25,
                          activebackground="#3d3d3d", activeforeground=self.text_color,
                          command=command)
            btn.pack(fill='x', ipady=12, pady=1)
        
        self.show_pc_overview(content)
    
    def show_pc_overview(self, parent):
        """Display PC Unit Overview with real-time updates"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(fill='x', pady=(0, 20))

        tk.Label(header, text="PC Unit Overview", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side='left')

        # Right side buttons
        btn_frame = tk.Frame(header, bg=self.bg_color)
        btn_frame.pack(side='right')

        # How to Use button
        help_btn = tk.Button(btn_frame, text="❓ How to Use", font=("Segoe UI", 11),
                        bg="#6c757d", fg=self.text_color, bd=0,
                        cursor="hand2", padx=15, pady=8,
                        command=self.show_pc_instructions)
        help_btn.pack(side='left', padx=(0, 10))

        # Refresh button
        refresh_btn = tk.Button(btn_frame, text="↻ Refresh", font=("Segoe UI", 11),
                            bg=self.accent_color, fg=self.secondary_bg, bd=0,
                            cursor="hand2", padx=15, pady=8,
                            command=lambda: self.show_pc_overview(parent))
        refresh_btn.pack(side='left')
        
        # Status summary
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT status, COUNT(*) as count FROM pc_units GROUP BY status")
            status_counts = cursor.fetchall()
            cursor.close()
            
            summary_frame = tk.Frame(container, bg=self.bg_color)
            summary_frame.pack(fill='x', pady=(0, 20))
            
            summary_text = " | ".join([f"{s['status']}: {s['count']}" for s in status_counts])
            tk.Label(summary_frame, text=f"Status Summary: {summary_text}", font=("Segoe UI", 14),
                    bg=self.bg_color, fg=self.text_secondary).pack()
        except:
            pass
        
        # PC Units grid
        grid_frame = tk.Frame(container, bg=self.bg_color)
        grid_frame.pack(fill='both', expand=True)
        
        try:
            self.refresh_db_connection()
            
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM pc_units ORDER BY unit_name")
            pc_units = cursor.fetchall()
            cursor.close()
            
            if not pc_units:
                cursor = self.db_connection.cursor()
                for i in range(1, 11):
                    cursor.execute("""
                        INSERT IGNORE INTO pc_units (unit_name, status, current_user_id, session_start) 
                        VALUES (%s, %s, %s, %s)
                    """, (f'PC-{i:02d}', 'Available', None, None))
                self.db_connection.commit()
                cursor.close()
                
                cursor = self.db_connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pc_units ORDER BY unit_name")
                pc_units = cursor.fetchall()
                cursor.close()
            
            for i, pc in enumerate(pc_units[:10]):
                row = i // 2
                col = i % 2
                
                pc_frame = tk.Frame(grid_frame, bg=self.secondary_bg, relief='raised', bd=2, 
                                   width=450, height=180)
                pc_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
                pc_frame.pack_propagate(False)
                
                # PC name
                name_label = tk.Label(pc_frame, text=pc['unit_name'], font=("Segoe UI", 18, "bold"),
                        bg=self.secondary_bg, fg=self.text_color)
                name_label.pack(pady=8)
                
                # Status with color
                status_color = self.get_pc_status_color(pc['status'])
                status_label = tk.Label(pc_frame, text=f"Status: {pc['status']}", font=("Segoe UI", 13),
                        bg=self.secondary_bg, fg=status_color)
                status_label.pack()
                
                # Store frame references
                frame_data = {
                    'frame': pc_frame,
                    'name_label': name_label,
                    'status_label': status_label,
                    'pc_data': pc,
                    'user_label': None,
                    'time_label': None,
                    'remaining_label': None,
                    'end_button': None
                }
                
                # Current user if occupied
                if pc['status'] == 'Occupied' and pc['current_user_id']:
                    try:
                        user_cursor = self.db_connection.cursor(dictionary=True)
                        user_cursor.execute("""
                            SELECT username, session_time_limit FROM users WHERE user_id = %s
                        """, (pc['current_user_id'],))
                        user = user_cursor.fetchone()
                        user_cursor.close()
                        
                        if user:
                            user_label = tk.Label(pc_frame, text=f"User: {user['username']}", 
                                                 font=("Segoe UI", 11, "bold"),
                                    bg=self.secondary_bg, fg=self.text_color)
                            user_label.pack(pady=(8, 0))
                            frame_data['user_label'] = user_label
                            
                            # Session time
                            if pc['session_start']:
                                duration = datetime.now() - pc['session_start']
                                elapsed_minutes = int(duration.total_seconds() / 60)
                                time_limit = user['session_time_limit']
                                remaining_minutes = max(0, time_limit - elapsed_minutes)
                                
                                hours, minutes = divmod(elapsed_minutes, 60)
                                rem_hours, rem_mins = divmod(remaining_minutes, 60)
                                
                                time_label = tk.Label(pc_frame, text=f"Used: {hours:02d}:{minutes:02d}", 
                                                     font=("Segoe UI", 10),
                                        bg=self.secondary_bg, fg=self.text_secondary)
                                time_label.pack()
                                frame_data['time_label'] = time_label
                                
                                rem_color = self.danger_color if remaining_minutes <= 10 else (
                                    self.warning_color if remaining_minutes < 30 else self.text_secondary
                                )
                                
                                remaining_label = tk.Label(pc_frame, text=f"Left: {rem_hours:02d}:{rem_mins:02d}", 
                                                          font=("Segoe UI", 10, "bold" if remaining_minutes < 30 else "normal"),
                                        bg=self.secondary_bg, fg=rem_color)
                                remaining_label.pack()
                                frame_data['remaining_label'] = remaining_label
                                
                                # Auto-logout if expired
                                if remaining_minutes <= 0:
                                    self.auto_logout_expired_session(pc['id'])
                    except:
                        pass
                
                # Force logout button
                if pc['status'] == 'Occupied':
                    end_btn = tk.Button(pc_frame, text="⚡", font=("Segoe UI", 11, "bold"),
                                       bg=self.danger_color, fg=self.text_color, bd=0, cursor="hand2",
                                       width=3, height=1,
                                       command=lambda pc_id=pc['id']: self.end_pc_session(pc_id, parent))
                    end_btn.place(x=405, y=5)
                else:
                    end_btn = tk.Button(pc_frame, text="⚡", font=("Segoe UI", 11, "bold"),
                                       bg="#6c757d", fg=self.text_color, bd=0, cursor="arrow",
                                       width=3, height=1, state='disabled')
                    end_btn.place(x=405, y=5)
                
                frame_data['end_button'] = end_btn
                self.admin_pc_frames_data[pc['unit_name']] = frame_data

                frame_data['end_button'] = end_btn
                
            
                if pc['status'] != 'Occupied':
                    is_locked = pc.get('is_locked', False)
                    lock_text = "🔓" if is_locked else "🔒"
                    lock_color = self.success_color if is_locked else "#6c757d"
                    
                    lock_btn = tk.Button(pc_frame, text=lock_text, font=("Segoe UI", 11, "bold"),
                                        bg=lock_color, fg=self.text_color, bd=0, cursor="hand2",
                                        width=3, height=1,
                                        command=lambda pc_id=pc['id'], locked=is_locked: self.toggle_pc_lock(pc_id, locked, parent))
                    lock_btn.place(x=360, y=5)
                    frame_data['lock_button'] = lock_btn
                else:
                    # Can't lock occupied PC
                    lock_btn = tk.Button(pc_frame, text="🔒", font=("Segoe UI", 11, "bold"),
                                        bg="#3d3d3d", fg=self.text_color, bd=0, cursor="arrow",
                                        width=3, height=1, state='disabled')
                    lock_btn.place(x=360, y=5)
                    frame_data['lock_button'] = lock_btn
                
                
                self.admin_pc_frames_data[pc['unit_name']] = frame_data
            
            for i in range(5):
                grid_frame.grid_rowconfigure(i, weight=1)
            for i in range(2):
                grid_frame.grid_columnconfigure(i, weight=1)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading PC units: {e}")
        
        self.root.after(5000, lambda: self.refresh_admin_pc_data(parent))
    
    def get_pc_status_color(self, status):
        """Get color for PC status"""
        colors = {
            'Available': self.success_color,
            'Occupied': self.warning_color,
            'Offline': self.danger_color,
            'Maintenance': '#6c757d'
        }
        return colors.get(status, self.text_color)
    
    def refresh_admin_pc_data(self, parent):
        """Refresh PC data without redrawing"""
        try:
            if hasattr(self, 'admin_pc_frames_data') and self.admin_pc_frames_data:
                self.refresh_db_connection()
                
                cursor = self.db_connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pc_units ORDER BY unit_name")
                pc_units = cursor.fetchall()
                cursor.close()
                
                for pc in pc_units[:10]:
                    pc_name = pc['unit_name']
                    if pc_name in self.admin_pc_frames_data:
                        frame_data = self.admin_pc_frames_data[pc_name]
                        old_pc_data = frame_data['pc_data']
                        
                        if (old_pc_data['status'] != pc['status'] or 
                            old_pc_data['current_user_id'] != pc['current_user_id'] or
                            old_pc_data['session_start'] != pc['session_start']):
                            
                            # Update will be handled on next full refresh
                            pass
                
                self.root.after(5000, lambda: self.refresh_admin_pc_data(parent))
                
        except Exception as e:
            print(f"Error refreshing admin PC data: {e}")
            self.root.after(10000, lambda: self.refresh_admin_pc_data(parent))
    
    def end_pc_session(self, pc_id, parent):
        """Force logout user from PC"""
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT pc.unit_name, pc.current_user_id, u.username, u.full_name
                FROM pc_units pc
                LEFT JOIN users u ON pc.current_user_id = u.user_id
                WHERE pc.id = %s
            """, (pc_id,))
            pc_info = cursor.fetchone()
            cursor.close()
            
            if not pc_info:
                messagebox.showerror("Error", "PC not found")
                return
            
            user_info = f"User: {pc_info['full_name']} ({pc_info['username']})" if pc_info['username'] else "No user logged in"
            confirm_msg = f"Force logout from {pc_info['unit_name']}?\n\n{user_info}\n\nThis will immediately end their session."
            
            if messagebox.askyesno("Force Logout Confirmation", confirm_msg):
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE pc_units 
                    SET status = 'Available', current_user_id = NULL, session_start = NULL 
                    WHERE id = %s
                """, (pc_id,))
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"User logged out from {pc_info['unit_name']}")
                self.show_pc_overview(parent)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error during force logout: {e}")
            if 'cursor' in locals():
                self.db_connection.rollback()

    def toggle_pc_lock(self, pc_id, current_locked_status, parent):
        """Lock or unlock a PC"""
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT unit_name, status FROM pc_units WHERE id = %s
            """, (pc_id,))
            pc_info = cursor.fetchone()
            cursor.close()
            
            if not pc_info:
                messagebox.showerror("Error", "PC not found")
                return
            
            # Can't lock occupied PC
            if pc_info['status'] == 'Occupied':
                messagebox.showwarning("Cannot Lock", 
                                    f"{pc_info['unit_name']} is currently occupied.\n\n"
                                    "End the session first before locking.")
                return
            
            new_status = not current_locked_status
            action = "lock" if new_status else "unlock"
            
            if messagebox.askyesno("Confirm", 
                                f"{action.capitalize()} {pc_info['unit_name']}?\n\n"
                                f"{'Users will not be able to login to this PC.' if new_status else 'Users will be able to login to this PC.'}"):
                
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE pc_units 
                    SET is_locked = %s 
                    WHERE id = %s
                """, (new_status, pc_id))
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"{pc_info['unit_name']} has been {action}ed!")
                self.show_pc_overview(parent)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error toggling lock: {e}")
            if 'cursor' in locals():
                self.db_connection.rollback()
    
    def auto_logout_expired_session(self, pc_id):
        """Auto logout when session expires"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE pc_units 
                SET status = 'Available', current_user_id = NULL, session_start = NULL 
                WHERE id = %s
            """, (pc_id,))
            self.db_connection.commit()
            cursor.close()
        except:
            pass
    
    def show_inventory_management(self, parent):
        """Display Inventory Management"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        tk.Label(container, text="Inventory Management", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', pady=(0, 20))
        
        # Main frame
        main_frame = tk.Frame(container, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, pady=10)
        
        # Left frame for form
        left_frame = tk.Frame(main_frame, bg=self.bg_color, width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        left_frame.pack_propagate(False)
        
                # Title - anchor to west
        tk.Label(left_frame, text="Add/Edit Item", font=("Segoe UI", 18, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', pady=(0, 15), padx=20)
        # Item form
                        # Frame to center the label and entry
       # Item Name
        tk.Label(left_frame, text="Item Name:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', padx=20)  # ← ADD padx=20
        self.inv_name_entry = tk.Entry(left_frame, font=("Segoe UI", 11), width=25,
                                    bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.inv_name_entry.pack(anchor='w', pady=(5, 15), ipady=5, padx=20)  # ← ADD padx=20

        # Category
        tk.Label(left_frame, text="Category:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', padx=20)  # ← ADD padx=20
        self.inv_category_var = tk.StringVar()
        self.inv_category_combo = ttk.Combobox(left_frame, textvariable=self.inv_category_var, 
                                            font=("Segoe UI", 11), width=23, state='readonly')
        self.inv_category_combo['values'] = ('Coffee', 'Food', 'Drinks', 'Snack', 'Dessert')
        self.inv_category_combo.pack(anchor='w', pady=(5, 15), ipady=5, padx=20)  # ← ADD padx=20

        # Quantity
        tk.Label(left_frame, text="Quantity:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', padx=20)  # ← ADD padx=20
        self.inv_quantity_entry = tk.Entry(left_frame, font=("Segoe UI", 11), width=25,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.inv_quantity_entry.pack(anchor='w', pady=(5, 15), ipady=5, padx=20)  # ← ADD padx=20

        # Unit Price
        tk.Label(left_frame, text="Unit Price (₱):", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', padx=20)  # ← ADD padx=20
        self.inv_price_entry = tk.Entry(left_frame, font=("Segoe UI", 11), width=25,
                                    bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.inv_price_entry.pack(anchor='w', pady=(5, 15), ipady=5, padx=20)  # ← ADD padx=20

        # Min Stock Level
        tk.Label(left_frame, text="Min Stock Level:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', padx=20)  # ← ADD padx=20
        self.inv_min_stock_entry = tk.Entry(left_frame, font=("Segoe UI", 11), width=25,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.inv_min_stock_entry.pack(anchor='w', pady=(5, 15), ipady=5, padx=20)  # ← ADD padx=20

        # Buttons - positioned at bottom right
        buttons_frame = tk.Frame(left_frame, bg=self.bg_color)
        buttons_frame.pack(side='bottom', anchor='w', pady=10, padx=20)  # Already has padx=20

        clear_button = tk.Button(buttons_frame, text="Clear", font=("Segoe UI", 11),
                                bg="#6c757d", fg=self.text_color, bd=0,
                                cursor="hand2", width=12, command=self.clear_inventory_form)
        clear_button.pack(side='left', padx=(0, 10))

        self.inv_add_button = tk.Button(buttons_frame, text="Add Item", font=("Segoe UI", 11),
                                    bg=self.accent_color, fg=self.text_color, bd=0,
                                    cursor="hand2", width=12, command=lambda: self.add_inventory_item(parent))
        self.inv_add_button.pack(side='left')
        
        # Right frame for inventory list
        right_frame = tk.Frame(main_frame, bg=self.bg_color)
        right_frame.pack(side='right', fill='both', expand=True)
        
        top_frame = tk.Frame(right_frame, bg=self.bg_color)
        top_frame.pack(fill='x', pady=10)

        # Refresh button on left
        tk.Button(top_frame, text="Refresh", font=("Segoe UI", 11),
        bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
        width=12, command=self.refresh_inventory).pack(side='left', padx=(0, 10))

        # Search frame in the middle
        search_frame = tk.Frame(top_frame, bg=self.bg_color)
        search_frame.pack(side='left', fill='x', expand=True)

        tk.Label(search_frame, text="Search:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(side='left')

        self.inv_search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), width=30,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.inv_search_entry.pack(side='left', padx=(10, 10), ipady=5)
        self.inv_search_entry.bind('<KeyRelease>', lambda e: self.search_inventory())

        search_button = tk.Button(search_frame, text="Search", font=("Segoe UI", 11),
                                bg=self.accent_color, fg=self.text_color, bd=0,
                                cursor="hand2", width=10, command=self.search_inventory)
        search_button.pack(side='left')
        
        # Inventory treeview
        columns = ('ID', 'Name', 'Category', 'Quantity', 'Price', 'Min Stock', 'Status')
        self.inventory_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.inventory_tree.heading(col, text=col)
            if col == 'ID':
                self.inventory_tree.column(col, width=50)
            elif col == 'Name':
                self.inventory_tree.column(col, width=150)
            elif col == 'Category':
                self.inventory_tree.column(col, width=100)
            elif col in ['Quantity', 'Price', 'Min Stock']:
                self.inventory_tree.column(col, width=80)
            else:
                self.inventory_tree.column(col, width=100)
        
        # Scrollbars
        inv_v_scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=inv_v_scrollbar.set)
        
        self.inventory_tree.pack(side='left', fill='both', expand=True)
        inv_v_scrollbar.pack(side='right', fill='y')
        
        # Bind double-click to edit
        self.inventory_tree.bind('<Double-1>', lambda e: self.edit_inventory_item())
        
        # Action buttons frame
        action_frame = tk.Frame(top_frame, bg=self.bg_color)
        action_frame.pack(side='right')

        tk.Button(action_frame, text="Edit Selected", font=("Segoe UI", 11),
                bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                width=14, command=self.edit_inventory_item).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="Delete Selected", font=("Segoe UI", 11),
                bg=self.danger_color, fg=self.text_color, bd=0, cursor="hand2",
                width=14, command=self.delete_inventory_item).pack(side='left')

        self.selected_inventory_id = None
        
        # Initialize variables
        self.selected_inventory_id = None
        
        # Load inventory data
        self.refresh_inventory()

    def add_inventory_item(self, parent):
        """Add or update inventory item"""
        try:
            name = self.inv_name_entry.get().strip()
            category = self.inv_category_var.get().strip()
            quantity = self.inv_quantity_entry.get().strip()
            price = self.inv_price_entry.get().strip()
            min_stock = self.inv_min_stock_entry.get().strip()
            
            if not all([name, category, quantity, price, min_stock]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            try:
                quantity = int(quantity)
                price = float(price)
                min_stock = int(min_stock)
                if quantity < 0 or price < 0 or min_stock < 0:
                    raise ValueError("Values cannot be negative")
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
                return
            
            cursor = self.db_connection.cursor()
            
            if hasattr(self, 'selected_inventory_id') and self.selected_inventory_id:
                cursor.execute("""
                    UPDATE inventory_items 
                    SET name = %s, category = %s, quantity = %s, unit_price = %s, min_stock_level = %s
                    WHERE id = %s
                """, (name, category, quantity, price, min_stock, self.selected_inventory_id))
                message = "Item updated successfully!"
            else:
                cursor.execute("""
                    INSERT INTO inventory_items (name, category, quantity, unit_price, min_stock_level)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, category, quantity, price, min_stock))
                message = "Item added successfully!"
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", message)
            self.clear_inventory_form()
            self.refresh_inventory()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving item: {e}")
            self.db_connection.rollback()

    def edit_inventory_item(self):
        """Edit selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM inventory_items WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            cursor.close()
            
            if item:
                self.inv_name_entry.delete(0, tk.END)
                self.inv_name_entry.insert(0, item['name'])
                
                self.inv_category_var.set(item['category'])
                
                self.inv_quantity_entry.delete(0, tk.END)
                self.inv_quantity_entry.insert(0, str(item['quantity']))
                
                self.inv_price_entry.delete(0, tk.END)
                self.inv_price_entry.insert(0, str(item['unit_price']))
                
                self.inv_min_stock_entry.delete(0, tk.END)
                self.inv_min_stock_entry.insert(0, str(item.get('min_stock_level', 0)))
                
                self.selected_inventory_id = item_id
                self.inv_add_button.config(text="Update Item")
            else:
                messagebox.showerror("Error", "Item not found")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading item: {e}")

    def delete_inventory_item(self):
        """Delete selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_id = self.inventory_tree.item(selection[0])['values'][0]
        item_name = self.inventory_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM inventory_items WHERE id = %s", (item_id,))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.refresh_inventory()
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting item: {e}")
                self.db_connection.rollback()

    def clear_inventory_form(self):
        """Clear all inventory form fields"""
        self.inv_name_entry.delete(0, tk.END)
        self.inv_category_var.set('')
        self.inv_quantity_entry.delete(0, tk.END)
        self.inv_price_entry.delete(0, tk.END)
        self.inv_min_stock_entry.delete(0, tk.END)
        self.selected_inventory_id = None
        self.inv_add_button.config(text="Add Item")

    def refresh_inventory(self):
        """Refresh inventory list"""
        try:
            for item in self.inventory_tree.get_children():
                self.inventory_tree.delete(item)
            
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM inventory_items ORDER BY name")
            items = cursor.fetchall()
            cursor.close()
            
            for item in items:
                min_stock = item.get('min_stock_level', 0)
                if item['quantity'] == 0:
                    status = "Out of Stock"
                elif item['quantity'] <= min_stock:
                    status = "Low Stock"
                else:
                    status = "In Stock"
                
                self.inventory_tree.insert('', tk.END, values=(
                    item['id'],
                    item['name'],
                    item.get('category', 'N/A'),
                    item['quantity'],
                    f"₱{item['unit_price']:.2f}",
                    min_stock,
                    status
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error refreshing inventory: {e}")

    def search_inventory(self):
        """Search inventory items"""
        search_term = self.inv_search_entry.get().strip().lower()
        
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            if search_term:
                cursor.execute("""
                    SELECT * FROM inventory_items 
                    WHERE LOWER(name) LIKE %s OR LOWER(category) LIKE %s
                    ORDER BY name
                """, (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute("SELECT * FROM inventory_items ORDER BY name")
            
            items = cursor.fetchall()
            cursor.close()
            
            for item in items:
                min_stock = item.get('min_stock_level', 0)
                if item['quantity'] == 0:
                    status = "Out of Stock"
                elif item['quantity'] <= min_stock:
                    status = "Low Stock"
                else:
                    status = "In Stock"
                
                self.inventory_tree.insert('', tk.END, values=(
                    item['id'],
                    item['name'],
                    item.get('category', 'N/A'),
                    item['quantity'],
                    f"₱{item['unit_price']:.2f}",
                    min_stock,
                    status
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error searching inventory: {e}")

    def show_order_management(self, parent):
        """Display order management with inventory integration"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        tk.Label(container, text="Order Management", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', pady=(0, 20))
        # Top control frame (filters and actions in one row)
        top_control_frame = tk.Frame(container, bg=self.bg_color)
        top_control_frame.pack(fill='x', pady=(0, 15))
        # Filter buttons
        filter_frame = tk.Frame(container, bg=self.bg_color)
        filter_frame.pack(fill='x', pady=(0, 15))
        
        self.order_filter = tk.StringVar(value="Pending")
        
        for status in ["Pending", "Approved", "All"]:
            btn = tk.Button(filter_frame, text=status, font=("Segoe UI", 11),
                          bg=self.accent_color if status == "Pending" else self.secondary_bg,
                          fg=self.text_color, bd=0, cursor="hand2", padx=15, pady=8,
                          command=lambda s=status: self.filter_orders(s, parent))
            btn.pack(side='left', padx=(0, 10))
        
        # Orders treeview
        columns = ('ID', 'User', 'Item', 'Qty', 'Price', 'Total', 'Status', 'Date')
        self.orders_tree = ttk.Treeview(container, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.orders_tree.heading(col, text=col)
            if col == 'ID':
                self.orders_tree.column(col, width=50)
            elif col in ['User', 'Item']:
                self.orders_tree.column(col, width=150)
            elif col in ['Qty', 'Price', 'Total']:
                self.orders_tree.column(col, width=80)
            elif col == 'Status':
                self.orders_tree.column(col, width=100)
            else:
                self.orders_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.orders_tree.pack(side='left', fill='both', expand=True, pady=(0, 15))
        scrollbar.pack(side='right', fill='y', pady=(0, 15))
        
        # Right side: Action buttons
        action_frame = tk.Frame(top_control_frame, bg=self.bg_color)
        action_frame.pack(side='right')

        tk.Button(action_frame, text="✓ Approve Order", font=("Segoe UI", 11, "bold"),
                bg=self.success_color, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.approve_order).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="✗ Reject Order", font=("Segoe UI", 11),
                bg=self.danger_color, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.reject_order).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="↻ Refresh", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=lambda: self.load_orders("Pending")).pack(side='left')

        self.load_orders("Pending")
    
    def filter_orders(self, status, parent):
        """Filter orders by status"""
        self.order_filter.set(status)
        self.load_orders(status)
    
    def load_orders(self, status_filter):
        """Load orders based on filter"""
        try:
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            if status_filter == "All":
                cursor.execute("""
                    SELECT o.*, u.username 
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    ORDER BY o.order_date DESC
                """)
            else:
                cursor.execute("""
                    SELECT o.*, u.username 
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    WHERE o.order_status = %s
                    ORDER BY o.order_date DESC
                """, (status_filter,))
            
            orders = cursor.fetchall()
            cursor.close()
            
            for order in orders:
                self.orders_tree.insert('', tk.END, values=(
                    order['order_id'],
                    order['username'],
                    order['item_name'],
                    order['quantity'],
                    f"₱{order['price']:.2f}",
                    f"₱{order['total_price']:.2f}",
                    order['order_status'],
                    order['order_date'].strftime("%Y-%m-%d %H:%M")
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading orders: {e}")
    
    def approve_order(self):
        """Approve order with inventory check"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order to approve")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm", "Approve this order?\n\nThis will deduct items from inventory."):
            try:
                cursor = self.db_connection.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT item_name, quantity FROM orders 
                    WHERE order_id = %s
                """, (order_id,))
                order_details = cursor.fetchone()
                
                if order_details:
                    cursor.execute("""
                        SELECT quantity FROM inventory_items 
                        WHERE name = %s
                    """, (order_details['item_name'],))
                    inventory_item = cursor.fetchone()
                    
                    if inventory_item:
                        if inventory_item['quantity'] >= order_details['quantity']:
                            cursor.execute(
                                "UPDATE orders SET order_status = 'Approved' WHERE order_id = %s",
                                (order_id,)
                            )
                            
                            cursor.execute("""
                                UPDATE inventory_items 
                                SET quantity = GREATEST(0, quantity - %s)
                                WHERE name = %s
                            """, (order_details['quantity'], order_details['item_name']))
                            
                            self.db_connection.commit()
                            
                            messagebox.showinfo("Success", 
                                              f"Order approved!\n"
                                              f"Deducted {order_details['quantity']} x {order_details['item_name']}")
                        else:
                            messagebox.showwarning("Insufficient Stock", 
                                                 f"Cannot approve order!\n"
                                                 f"Requested: {order_details['quantity']} x {order_details['item_name']}\n"
                                                 f"Available: {inventory_item['quantity']}")
                            cursor.close()
                            return
                    else:
                        cursor.execute(
                            "UPDATE orders SET order_status = 'Approved' WHERE order_id = %s",
                            (order_id,)
                        )
                        self.db_connection.commit()
                        
                        messagebox.showwarning("Item Not in Inventory", 
                                             f"Order approved, but '{order_details['item_name']}' not found in inventory.\n"
                                             f"Please add this item to inventory management.")
                
                cursor.close()
                self.load_orders(self.order_filter.get())
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error approving order: {e}")
                self.db_connection.rollback()
    
    def reject_order(self):
        """Reject selected order"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order to reject")
            return
        
        order_id = self.orders_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm", "Reject this order?"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "UPDATE orders SET order_status = 'Rejected' WHERE order_id = %s",
                    (order_id,)
                )
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Order rejected")
                self.load_orders(self.order_filter.get())
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error rejecting order: {e}")
                self.db_connection.rollback()

    # COMPLETE IMPLEMENTATIONS FOR ALL ADMIN FEATURES
# Add these methods to your AdminApp class in admin_panel.py
# Replace the stub methods with these complete implementations

    def show_menu_items(self, parent):
        """Display and manage cafe menu items"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        tk.Label(container, text="Cafe Menu Management", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', pady=(0, 20))
        
        # Main frame
        main_frame = tk.Frame(container, bg=self.bg_color)
        main_frame.pack(fill='both', expand=True, pady=10)
        
        # Left frame - Form
        left_frame = tk.Frame(main_frame, bg=self.bg_color, width=320)
        left_frame.pack(side='left', fill='y', padx=(0, 20))
        left_frame.pack_propagate(False)
        
        form_container = tk.Frame(left_frame, bg=self.bg_color)
        form_container.pack(pady=20, anchor='w', padx=20)  # ← anchor='w' and padx for spacing

        # Title - still centered but within the left-aligned container
        tk.Label(form_container, text="Add/Edit Menu Item", font=("Segoe UI", 18, "bold"),
                bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, pady=(0, 15), sticky='w')
        
                # Create a container frame for all menu items
        menu_form_frame = tk.Frame(left_frame, bg=self.bg_color)
        menu_form_frame.pack(pady=20, padx=20, anchor='w')

        # Item Name
        tk.Label(menu_form_frame, text="Item Name:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w')
        self.menu_name_entry = tk.Entry(menu_form_frame, font=("Segoe UI", 11), width=28,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.menu_name_entry.pack(anchor='w', pady=(5, 15), ipady=5)

        # Category
        tk.Label(menu_form_frame, text="Category:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w')
        self.menu_category_var = tk.StringVar()
        menu_category_combo = ttk.Combobox(menu_form_frame, textvariable=self.menu_category_var,
                                        font=("Segoe UI", 11), width=26, state='readonly')
        menu_category_combo['values'] = ('Coffee', 'Food', 'Drinks', 'Snack', 'Dessert')
        menu_category_combo.pack(anchor='w', pady=(5, 15), ipady=5)

        # Price
        tk.Label(menu_form_frame, text="Price (₱):", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w')
        self.menu_price_entry = tk.Entry(menu_form_frame, font=("Segoe UI", 11), width=28,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.menu_price_entry.pack(anchor='w', pady=(5, 15), ipady=5)
                
                # Create container frame for all menu form elements
        menu_form_container = tk.Frame(left_frame, bg=self.bg_color)
        menu_form_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Available checkbox
        self.menu_available_var = tk.BooleanVar(value=True)
        tk.Checkbutton(menu_form_container, text="Available for ordering", variable=self.menu_available_var,
                    font=("Segoe UI", 11), bg=self.bg_color, fg=self.text_color,
                    selectcolor="#3d3d3d", activebackground=self.bg_color).pack(anchor='w', pady=(0, 15))

        # Image selection
        tk.Label(menu_form_container, text="Image (Optional):", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w')

        image_frame = tk.Frame(menu_form_container, bg=self.bg_color)
        image_frame.pack(fill='x', pady=(5, 15), anchor='w')

        self.menu_image_path = tk.StringVar()
        tk.Entry(image_frame, textvariable=self.menu_image_path, font=("Segoe UI", 9),
                width=20, bg="#3d3d3d", fg=self.text_color, state='readonly').pack(side='left', ipady=5)

        tk.Button(image_frame, text="Browse", font=("Segoe UI", 9),
                bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                command=self.browse_menu_image).pack(side='left', padx=(5, 0))

        # Buttons at bottom of container
        btn_frame = tk.Frame(menu_form_container, bg=self.bg_color)
        btn_frame.pack(side='bottom', anchor='w', pady=(20, 0))  # Changed 'e' to 'w'

        tk.Button(btn_frame, text="Clear", font=("Segoe UI", 11),
                bg="#6c757d", fg=self.text_color, bd=0,
                cursor="hand2", width=13, command=self.clear_menu_form).pack(side='left', padx=(0, 10))

        self.menu_add_btn = tk.Button(btn_frame, text="Add Item", font=("Segoe UI", 11, "bold"),
                                    bg=self.accent_color, fg=self.text_color, bd=0,
                                    cursor="hand2", width=13, command=self.add_menu_item)
        self.menu_add_btn.pack(side='left')
        
        # Right frame - Menu items list
        right_frame = tk.Frame(main_frame, bg=self.bg_color)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Top control frame
        control_frame = tk.Frame(right_frame, bg=self.bg_color)
        control_frame.pack(fill='x', pady=10)

        # Refresh button on left
        tk.Button(control_frame, text="Refresh", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                width=12, command=self.refresh_menu_items).pack(side='left', padx=(0, 10))

        # Search frame in the middle
        search_frame = tk.Frame(control_frame, bg=self.bg_color)
        search_frame.pack(side='left', fill='x', expand=True)

        tk.Label(search_frame, text="Search:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(side='left')

        self.menu_search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), width=30,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.menu_search_entry.pack(side='left', padx=(10, 10), ipady=5)
        self.menu_search_entry.bind('<KeyRelease>', lambda e: self.search_menu_items())

        # Search button
        tk.Button(search_frame, text="Search", font=("Segoe UI", 11),
                bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                width=10, command=self.search_menu_items).pack(side='left')

        
        # Treeview
        columns = ('ID', 'Name', 'Category', 'Price', 'Available', 'Image')
        self.menu_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.menu_tree.heading(col, text=col)
            if col == 'ID':
                self.menu_tree.column(col, width=50)
            elif col == 'Name':
                self.menu_tree.column(col, width=200)
            elif col in ['Category', 'Available']:
                self.menu_tree.column(col, width=100)
            elif col == 'Price':
                self.menu_tree.column(col, width=80)
            else:
                self.menu_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(right_frame, orient='vertical', command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=scrollbar.set)
        
        self.menu_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.menu_tree.bind('<Double-1>', lambda e: self.edit_menu_item())
        
        # Action buttons on right
        tk.Button(control_frame, text="Edit Selected", font=("Segoe UI", 11),
                bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                width=13, command=self.edit_menu_item).pack(side='right', padx=(10, 10))

        tk.Button(control_frame, text="Delete Selected", font=("Segoe UI", 11),
                bg=self.danger_color, fg=self.text_color, bd=0, cursor="hand2",
                width=13, command=self.delete_menu_item).pack(side='right')

        self.selected_menu_id = None
        self.refresh_menu_items()
    
    def browse_menu_image(self):
        """Browse for menu item image"""
        filename = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")]
        )
        if filename:
            self.menu_image_path.set(filename)
    
    def add_menu_item(self):
        """Add or update menu item"""
        try:
            name = self.menu_name_entry.get().strip()
            category = self.menu_category_var.get().strip()
            price = self.menu_price_entry.get().strip()
            available = self.menu_available_var.get()
            image_path = self.menu_image_path.get().strip()
            
            if not all([name, category, price]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            try:
                price = float(price)
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except ValueError:
                messagebox.showerror("Error", "Invalid price format")
                return
            
            cursor = self.db_connection.cursor()
            
            if self.selected_menu_id:
                cursor.execute("""
                    UPDATE cafe_items 
                    SET item_name = %s, category = %s, price = %s, available = %s, image_path = %s
                    WHERE item_id = %s
                """, (name, category, price, available, image_path if image_path else None, self.selected_menu_id))
                message = "Menu item updated successfully!"
            else:
                cursor.execute("""
                    INSERT INTO cafe_items (item_name, category, price, available, image_path)
                    VALUES (%s, %s, %s, %s, %s)
                """, (name, category, price, available, image_path if image_path else None))
                message = "Menu item added successfully!"
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", message)
            self.clear_menu_form()
            self.refresh_menu_items()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving menu item: {e}")
            self.db_connection.rollback()
    
    def edit_menu_item(self):
        """Edit selected menu item"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a menu item to edit")
            return
        
        item_id = self.menu_tree.item(selection[0])['values'][0]
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cafe_items WHERE item_id = %s", (item_id,))
            item = cursor.fetchone()
            cursor.close()
            
            if item:
                self.menu_name_entry.delete(0, tk.END)
                self.menu_name_entry.insert(0, item['item_name'])
                
                self.menu_category_var.set(item['category'])
                
                self.menu_price_entry.delete(0, tk.END)
                self.menu_price_entry.insert(0, str(item['price']))
                
                self.menu_available_var.set(item['available'])
                
                self.menu_image_path.set(item.get('image_path', '') or '')
                
                self.selected_menu_id = item_id
                self.menu_add_btn.config(text="Update Item")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading menu item: {e}")
    
    def delete_menu_item(self):
        """Delete selected menu item"""
        selection = self.menu_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a menu item to delete")
            return
        
        item_id = self.menu_tree.item(selection[0])['values'][0]
        item_name = self.menu_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Delete '{item_name}' from menu?"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM cafe_items WHERE item_id = %s", (item_id,))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", "Menu item deleted!")
                self.refresh_menu_items()
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting item: {e}")
                self.db_connection.rollback()
    
    def clear_menu_form(self):
        """Clear menu form"""
        self.menu_name_entry.delete(0, tk.END)
        self.menu_category_var.set('')
        self.menu_price_entry.delete(0, tk.END)
        self.menu_available_var.set(True)
        self.menu_image_path.set('')
        self.selected_menu_id = None
        self.menu_add_btn.config(text="Add Item")
    
    def refresh_menu_items(self):
        """Refresh menu items list"""
        try:
            for item in self.menu_tree.get_children():
                self.menu_tree.delete(item)
            
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cafe_items ORDER BY category, item_name")
            items = cursor.fetchall()
            cursor.close()
            
            for item in items:
                self.menu_tree.insert('', tk.END, values=(
                    item['item_id'],
                    item['item_name'],
                    item['category'],
                    f"₱{item['price']:.2f}",
                    "Yes" if item['available'] else "No",
                    "✓" if item.get('image_path') else "✗"
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading menu items: {e}")
    
    def search_menu_items(self):
        """Search menu items"""
        search_term = self.menu_search_entry.get().strip().lower()
        
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            if search_term:
                cursor.execute("""
                    SELECT * FROM cafe_items 
                    WHERE LOWER(item_name) LIKE %s OR LOWER(category) LIKE %s
                    ORDER BY category, item_name
                """, (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute("SELECT * FROM cafe_items ORDER BY category, item_name")
            
            items = cursor.fetchall()
            cursor.close()
            
            for item in items:
                self.menu_tree.insert('', tk.END, values=(
                    item['item_id'],
                    item['item_name'],
                    item['category'],
                    f"₱{item['price']:.2f}",
                    "Yes" if item['available'] else "No",
                    "✓" if item.get('image_path') else "✗"
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error searching menu: {e}")

    def show_account_creation(self, parent):
        """Create new user account"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        tk.Label(container, text="Create User Account", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', pady=(0, 30))
        
        # Form container
        form_frame = tk.Frame(container, bg=self.secondary_bg, padx=60, pady=50)
        form_frame.pack(fill='both', expand=True)
        
        # Left and right columns
        left_col = tk.Frame(form_frame, bg=self.secondary_bg)
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 30))
        
        right_col = tk.Frame(form_frame, bg=self.secondary_bg)
        right_col.pack(side='right', fill='both', expand=True, padx=(30, 0))
        
        # Left column fields - aligned
        tk.Label(left_col, text="Username*", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        username_entry = tk.Entry(left_col, font=("Segoe UI", 11), width=35,
                                  bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        username_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Password with show/hide button
        tk.Label(left_col, text="Password* (8+ chars, 1 number, 1 symbol)", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        
        password_frame = tk.Frame(left_col, bg=self.secondary_bg)
        password_frame.pack(fill='x', pady=(0, 5))
        
        password_entry = tk.Entry(password_frame, font=("Segoe UI", 11), show="*",
                                  bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        password_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        show_password_var = tk.BooleanVar()
        show_btn = tk.Button(password_frame, text="👁", font=("Segoe UI", 10),
                            bg="#3d3d3d", fg=self.text_color, bd=0, cursor="hand2",
                            command=lambda: self.toggle_password_visibility(password_entry, show_password_var))
        show_btn.pack(side='right', padx=(5, 0), ipady=8)
        
        # Password strength indicator
        password_strength_label = tk.Label(left_col, text="", font=("Segoe UI", 9),
                                          bg=self.secondary_bg, fg=self.text_secondary)
        password_strength_label.pack(anchor='w', pady=(0, 15))
        
        # Bind password validation
        password_entry.bind('<KeyRelease>', lambda e: self.check_password_strength(password_entry.get(), password_strength_label))
        
        tk.Label(left_col, text="Full Name*", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        fullname_entry = tk.Entry(left_col, font=("Segoe UI", 11), width=35,
                                  bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        fullname_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        tk.Label(left_col, text="Phone Number", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        phone_entry = tk.Entry(left_col, font=("Segoe UI", 11), width=35,
                              bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        phone_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Right column fields - aligned
        tk.Label(right_col, text="Initial Balance (₱)", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        balance_entry = tk.Entry(right_col, font=("Segoe UI", 11), width=35,
                                bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        balance_entry.insert(0, "0.00")
        balance_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        tk.Label(right_col, text="Session Time Limit (minutes)", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        time_limit_entry = tk.Entry(right_col, font=("Segoe UI", 11), width=35,
                                    bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        time_limit_entry.insert(0, "120")
        time_limit_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        tk.Label(right_col, text="Hourly Rate (₱)", font=("Segoe UI", 12),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w', pady=(0, 5))
        rate_entry = tk.Entry(right_col, font=("Segoe UI", 11), width=35,
                             bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        rate_entry.insert(0, "20.00")
        rate_entry.pack(fill='x', pady=(0, 20), ipady=8)
        
        # Auto-approve checkbox
        auto_approve_var = tk.BooleanVar(value=True)
        tk.Checkbutton(right_col, text="Auto-approve account", variable=auto_approve_var,
                      font=("Segoe UI", 11), bg=self.secondary_bg, fg=self.text_color,
                      selectcolor="#3d3d3d", activebackground=self.secondary_bg).pack(anchor='w', pady=(10, 40))
        
        # Buttons - positioned at bottom right
        btn_frame = tk.Frame(right_col, bg=self.secondary_bg)
        btn_frame.pack(side='bottom', anchor='e', pady=(20, 0))
        
        tk.Button(btn_frame, text="Clear Form", font=("Segoe UI", 11),
                 bg="#6c757d", fg=self.text_color, bd=0, cursor="hand2",
                 padx=25, pady=12,
                 command=lambda: self.clear_account_form(
                     username_entry, password_entry, fullname_entry, phone_entry,
                     balance_entry, time_limit_entry, rate_entry, password_strength_label
                 )).pack(side='left', padx=(0, 15))
        
        tk.Button(btn_frame, text="✓ CREATE ACCOUNT", font=("Segoe UI", 12, "bold"),
                 bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=30, pady=12,
                 command=lambda: self.create_user_account(
                     username_entry.get(), password_entry.get(), fullname_entry.get(),
                     phone_entry.get(), balance_entry.get(), time_limit_entry.get(),
                     rate_entry.get(), auto_approve_var.get()
                 )).pack(side='left')
    
    def check_password_strength(self, password, label):
        """Check and display password strength"""
        if not password:
            label.config(text="", fg=self.text_secondary)
            return
            
        is_valid, message = self.validate_password(password)
        if is_valid:
            label.config(text="✓ Strong password", fg=self.success_color)
        else:
            label.config(text=f"✗ {message}", fg=self.danger_color)
    
    def create_user_account(self, username, password, fullname, phone, balance, time_limit, rate, auto_approve):
        """Create new user account with password validation"""
        if not all([username, password, fullname]):
            messagebox.showerror("Error", "Please fill in all required fields (username, password, full name)")
            return
        
        # Validate password strength
        is_valid, message = self.validate_password(password)
        if not is_valid:
            messagebox.showerror("Weak Password", f"Password requirements not met:\n\n{message}")
            return
        
        try:
            balance = float(balance) if balance else 0.00
            time_limit = int(time_limit) if time_limit else 120
            rate = float(rate) if rate else 20.00
            
            if balance < 0 or time_limit < 0 or rate < 0:
                messagebox.showerror("Error", "Balance, time limit, and rate cannot be negative")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric values")
            return
        
        try:
            cursor = self.db_connection.cursor()
            hashed_pw = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO users (username, password, full_name, phone_number, account_balance, 
                                  session_time_limit, hourly_rate, is_approved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, hashed_pw, fullname, phone, balance, time_limit, rate, auto_approve))
            
            self.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", 
                              f"Account created successfully!\n\n"
                              f"Username: {username}\n"
                              f"Status: {'Approved' if auto_approve else 'Pending Approval'}")
            
        except Error as e:
            if "Duplicate entry" in str(e):
                messagebox.showerror("Error", "Username already exists!")
            else:
                messagebox.showerror("Database Error", f"Error creating account: {e}")
            self.db_connection.rollback()
    
    def clear_account_form(self, *entries):
        """Clear account creation form"""
        for i, entry in enumerate(entries[:-1]):  # Exclude the label
            entry.delete(0, tk.END)
        entries[4].insert(0, "0.00")  # balance
        entries[5].insert(0, "120")   # time limit
        entries[6].insert(0, "20.00") # rate
        entries[-1].config(text="")   # Clear password strength label

    def show_pending_accounts(self, parent):
        """Display and manage pending accounts"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(header, text="Pending Account Approvals", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side='left')
        
        tk.Button(header, text="↻ Refresh", font=("Segoe UI", 11),
                 bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=15, pady=8, command=lambda: self.load_pending_accounts()).pack(side='right')
        
        # Treeview
        columns = ('ID', 'Username', 'Full Name', 'Phone', 'Balance', 'Created')
        self.pending_tree = ttk.Treeview(container, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.pending_tree.heading(col, text=col)
            if col == 'ID':
                self.pending_tree.column(col, width=50)
            elif col in ['Username', 'Full Name']:
                self.pending_tree.column(col, width=150)
            elif col == 'Phone':
                self.pending_tree.column(col, width=120)
            elif col == 'Balance':
                self.pending_tree.column(col, width=100)
            else:
                self.pending_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=scrollbar.set)
        
        self.pending_tree.pack(side='left', fill='both', expand=True, pady=(0, 15))
        scrollbar.pack(side='right', fill='y', pady=(0, 15))
        
        # Action buttons
        action_frame = tk.Frame(container, bg=self.bg_color)
        action_frame.pack(fill='x')
        
        tk.Button(action_frame, text="✓ Approve Account", font=("Segoe UI", 11, "bold"),
                 bg=self.success_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=20, pady=10, command=self.approve_account).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="✗ Reject Account", font=("Segoe UI", 11),
                 bg=self.danger_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=20, pady=10, command=self.reject_account).pack(side='left')
        
        self.load_pending_accounts()
    
    def load_pending_accounts(self):
        """Load pending accounts"""
        try:
            for item in self.pending_tree.get_children():
                self.pending_tree.delete(item)
            
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT user_id, username, full_name, phone_number, account_balance, created_at
                FROM users 
                WHERE is_approved = FALSE
                ORDER BY created_at DESC
            """)
            accounts = cursor.fetchall()
            cursor.close()
            
            for acc in accounts:
                self.pending_tree.insert('', tk.END, values=(
                    acc['user_id'],
                    acc['username'],
                    acc['full_name'],
                    acc['phone_number'] or 'N/A',
                    f"₱{acc['account_balance']:.2f}",
                    acc['created_at'].strftime("%Y-%m-%d %H:%M")
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading pending accounts: {e}")
    
    def approve_account(self):
        """Approve selected account"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to approve")
            return
        
        user_id = self.pending_tree.item(selection[0])['values'][0]
        username = self.pending_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Approval", f"Approve account for '{username}'?"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("UPDATE users SET is_approved = TRUE WHERE user_id = %s", (user_id,))
                self.db_connection.commit()
                cursor.close()
                # FINAL METHODS - Add these to complete the AdminApp class

                messagebox.showinfo("Success", f"Account approved for '{username}'")
                self.load_pending_accounts()
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error approving account: {e}")
                self.db_connection.rollback()
    
    def reject_account(self):
        """Reject and delete selected account"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to reject")
            return
        
        user_id = self.pending_tree.item(selection[0])['values'][0]
        username = self.pending_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Rejection", 
                              f"Reject and DELETE account for '{username}'?\n\nThis action cannot be undone!"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"Account rejected and deleted")
                self.load_pending_accounts()
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error rejecting account: {e}")
                self.db_connection.rollback()

    def show_all_users(self, parent):
        """Display all users with management options"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title and filters
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(header, text="All Users Management", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side='left')
        
        # Filter buttons
        filter_frame = tk.Frame(header, bg=self.bg_color)
        filter_frame.pack(side='right')
        
        self.users_filter = tk.StringVar(value="All")
        
        for status in ["All", "Approved", "Pending"]:
            btn = tk.Button(filter_frame, text=status, font=("Segoe UI", 10),
                          bg=self.accent_color if status == "All" else self.secondary_bg,
                          fg=self.text_color, bd=0, cursor="hand2", padx=12, pady=6,
                          command=lambda s=status: self.filter_users(s))
            btn.pack(side='left', padx=(5, 0))
        
        # Search and action buttons in one frame
        top_control_frame = tk.Frame(container, bg=self.bg_color)
        top_control_frame.pack(fill='x', pady=(0, 15))

        # Left side: Search
        search_frame = tk.Frame(top_control_frame, bg=self.bg_color)
        search_frame.pack(side='left')

        tk.Label(search_frame, text="Search:", font=("Segoe UI", 12),
                bg=self.bg_color, fg=self.text_color).pack(side='left')

        self.users_search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), width=40,
                                        bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        self.users_search_entry.pack(side='left', padx=(10, 10), ipady=5)
        self.users_search_entry.bind('<KeyRelease>', lambda e: self.search_users())

        # Refresh button (after search)
        tk.Button(search_frame, text="↻ Refresh", font=("Segoe UI", 10),
                bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=6, command=lambda: self.load_all_users("All")).pack(side='left')
        
        # Treeview
        columns = ('ID', 'Username', 'Full Name', 'Phone', 'Balance', 'Rate', 'Time Limit', 'Status', 'Created')
        self.users_tree = ttk.Treeview(container, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            if col == 'ID':
                self.users_tree.column(col, width=50)
            elif col in ['Username', 'Full Name']:
                self.users_tree.column(col, width=150)
            elif col == 'Phone':
                self.users_tree.column(col, width=120)
            elif col in ['Balance', 'Rate']:
                self.users_tree.column(col, width=100)
            elif col == 'Time Limit':
                self.users_tree.column(col, width=90)
            elif col == 'Status':
                self.users_tree.column(col, width=80)
            else:
                self.users_tree.column(col, width=130)
        
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side='left', fill='both', expand=True, pady=(0, 15))
        scrollbar.pack(side='right', fill='y', pady=(0, 15))
        
        # Action buttons
        action_frame = tk.Frame(top_control_frame, bg=self.bg_color)
        action_frame.pack(side='right')

        tk.Button(action_frame, text="💰 Add Balance", font=("Segoe UI", 11),
                bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.add_user_balance).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="⏱️ Set Time Limit", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.set_time_limit).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="💵 Set Rate", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.set_hourly_rate).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="🔄 Toggle Status", font=("Segoe UI", 11),
                bg=self.warning_color, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.toggle_user_status).pack(side='left', padx=(0, 10))

        tk.Button(action_frame, text="🗑️ Delete User", font=("Segoe UI", 11),
                bg=self.danger_color, fg=self.text_color, bd=0, cursor="hand2",
                padx=15, pady=10, command=self.delete_user).pack(side='left')

        self.load_all_users("All")
    
    def filter_users(self, status):
        """Filter users by status"""
        self.users_filter.set(status)
        self.load_all_users(status)
    
    def load_all_users(self, status_filter):
        """Load all users"""
        try:
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            if status_filter == "All":
                cursor.execute("""
                    SELECT user_id, username, full_name, phone_number, account_balance,
                           hourly_rate, session_time_limit, is_approved, created_at
                    FROM users 
                    ORDER BY created_at DESC
                """)
            elif status_filter == "Approved":
                cursor.execute("""
                    SELECT user_id, username, full_name, phone_number, account_balance,
                           hourly_rate, session_time_limit, is_approved, created_at
                    FROM users 
                    WHERE is_approved = TRUE
                    ORDER BY created_at DESC
                """)
            else:  # Pending
                cursor.execute("""
                    SELECT user_id, username, full_name, phone_number, account_balance,
                           hourly_rate, session_time_limit, is_approved, created_at
                    FROM users 
                    WHERE is_approved = FALSE
                    ORDER BY created_at DESC
                """)
            
            users = cursor.fetchall()
            cursor.close()
            
            for user in users:
                self.users_tree.insert('', tk.END, values=(
                    user['user_id'],
                    user['username'],
                    user['full_name'],
                    user['phone_number'] or 'N/A',
                    f"₱{user['account_balance']:.2f}",
                    f"₱{user['hourly_rate']:.2f}",
                    f"{user['session_time_limit']} min",
                    "Active" if user['is_approved'] else "Pending",
                    user['created_at'].strftime("%Y-%m-%d")
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading users: {e}")
    
    def search_users(self):
        """Search users"""
        search_term = self.users_search_entry.get().strip().lower()
        
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            if search_term:
                cursor.execute("""
                    SELECT user_id, username, full_name, phone_number, account_balance,
                           hourly_rate, session_time_limit, is_approved, created_at
                    FROM users 
                    WHERE LOWER(username) LIKE %s OR LOWER(full_name) LIKE %s
                    ORDER BY created_at DESC
                """, (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute("""
                    SELECT user_id, username, full_name, phone_number, account_balance,
                           hourly_rate, session_time_limit, is_approved, created_at
                    FROM users 
                    ORDER BY created_at DESC
                """)
            
            users = cursor.fetchall()
            cursor.close()
            
            for user in users:
                self.users_tree.insert('', tk.END, values=(
                    user['user_id'],
                    user['username'],
                    user['full_name'],
                    user['phone_number'] or 'N/A',
                    f"₱{user['account_balance']:.2f}",
                    f"₱{user['hourly_rate']:.2f}",
                    f"{user['session_time_limit']} min",
                    "Active" if user['is_approved'] else "Pending",
                    user['created_at'].strftime("%Y-%m-%d")
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error searching users: {e}")
    
    def add_user_balance(self):
        """Add balance to selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Balance")
        dialog.geometry("350x200")
        dialog.configure(bg=self.secondary_bg)
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Add balance for: {username}", font=("Segoe UI", 12, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=(20, 10))
        
        tk.Label(dialog, text="Amount to add (₱):", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=(10, 5))
        
        amount_entry = tk.Entry(dialog, font=("Segoe UI", 12), width=20,
                               bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        amount_entry.pack(pady=(0, 20), ipady=8)
        amount_entry.focus()
        
        def confirm_add():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be positive")
                    return
                
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET account_balance = account_balance + %s 
                    WHERE user_id = %s
                """, (amount, user_id))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"Added ₱{amount:.2f} to {username}'s account")
                dialog.destroy()
                self.load_all_users(self.users_filter.get())
                
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
            except Error as e:
                messagebox.showerror("Database Error", f"Error adding balance: {e}")
                self.db_connection.rollback()
        
        tk.Button(dialog, text="Add Balance", font=("Segoe UI", 11, "bold"),
                 bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=20, pady=10, command=confirm_add).pack()
        
        amount_entry.bind('<Return>', lambda e: confirm_add())
    
    def set_time_limit(self):
        """Set time limit for selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Time Limit")
        dialog.geometry("350x200")
        dialog.configure(bg=self.secondary_bg)
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Set time limit for: {username}", font=("Segoe UI", 12, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=(20, 10))
        
        tk.Label(dialog, text="Time limit (minutes):", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=(10, 5))
        
        limit_entry = tk.Entry(dialog, font=("Segoe UI", 12), width=20,
                              bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        limit_entry.pack(pady=(0, 20), ipady=8)
        limit_entry.focus()
        
        def confirm_set():
            try:
                limit = int(limit_entry.get())
                if limit <= 0:
                    messagebox.showerror("Error", "Time limit must be positive")
                    return
                
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET session_time_limit = %s 
                    WHERE user_id = %s
                """, (limit, user_id))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"Set time limit to {limit} minutes for {username}")
                dialog.destroy()
                self.load_all_users(self.users_filter.get())
                
            except ValueError:
                messagebox.showerror("Error", "Invalid time limit")
            except Error as e:
                messagebox.showerror("Database Error", f"Error setting time limit: {e}")
                self.db_connection.rollback()
        
        tk.Button(dialog, text="Set Time Limit", font=("Segoe UI", 11, "bold"),
                 bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=20, pady=10, command=confirm_set).pack()
        
        limit_entry.bind('<Return>', lambda e: confirm_set())
    
    def set_hourly_rate(self):
        """Set hourly rate for selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Hourly Rate")
        dialog.geometry("350x200")
        dialog.configure(bg=self.secondary_bg)
        dialog.resizable(False, False)
        
        tk.Label(dialog, text=f"Set hourly rate for: {username}", font=("Segoe UI", 12, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=(20, 10))
        
        tk.Label(dialog, text="Hourly rate (₱):", font=("Segoe UI", 11),
                bg=self.secondary_bg, fg=self.text_color).pack(pady=(10, 5))
        
        rate_entry = tk.Entry(dialog, font=("Segoe UI", 12), width=20,
                             bg="#3d3d3d", fg=self.text_color, insertbackground=self.text_color, bd=0)
        rate_entry.pack(pady=(0, 20), ipady=8)
        rate_entry.focus()
        
        def confirm_set():
            try:
                rate = float(rate_entry.get())
                if rate <= 0:
                    messagebox.showerror("Error", "Rate must be positive")
                    return
                
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET hourly_rate = %s 
                    WHERE user_id = %s
                """, (rate, user_id))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"Set hourly rate to ₱{rate:.2f} for {username}")
                dialog.destroy()
                self.load_all_users(self.users_filter.get())
                
            except ValueError:
                messagebox.showerror("Error", "Invalid rate")
            except Error as e:
                messagebox.showerror("Database Error", f"Error setting rate: {e}")
                self.db_connection.rollback()
        
        tk.Button(dialog, text="Set Rate", font=("Segoe UI", 11, "bold"),
                 bg=self.accent_color, fg=self.text_color, bd=0, cursor="hand2",
                 padx=20, pady=10, command=confirm_set).pack()
        
        rate_entry.bind('<Return>', lambda e: confirm_set())
    
    def toggle_user_status(self):
        """Toggle user approval status"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        current_status = self.users_tree.item(selection[0])['values'][7]
        
        new_status = "Pending" if current_status == "Active" else "Active"
        
        if messagebox.askyesno("Confirm", f"Change {username}'s status to {new_status}?"):
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET is_approved = %s 
                    WHERE user_id = %s
                """, (new_status == "Active", user_id))
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"Status changed to {new_status}")
                self.load_all_users(self.users_filter.get())
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error updating status: {e}")
                self.db_connection.rollback()
    
    def delete_user(self):
        """Delete selected user"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user_id = self.users_tree.item(selection[0])['values'][0]
        username = self.users_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Permanently delete user '{username}'?\n\nThis will also delete all their orders!"):
            try:
                cursor = self.db_connection.cursor()
                
                # Delete orders first (foreign key constraint)
                cursor.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
                
                # Delete user
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Success", f"User '{username}' deleted")
                self.load_all_users(self.users_filter.get())
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error deleting user: {e}")
                self.db_connection.rollback()

    def show_all_orders(self, parent):
        """Display all orders history"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title and filters
        header = tk.Frame(container, bg=self.bg_color)
        header.pack(fill='x', pady=(0, 20))
        
        tk.Label(header, text="All Orders History", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(side='left')
        
        # Stats
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total, SUM(total_price) as revenue FROM orders")
            stats = cursor.fetchone()
            cursor.close()
            
            stats_frame = tk.Frame(header, bg=self.bg_color)
            stats_frame.pack(side='right')
            
            tk.Label(stats_frame, text=f"Total Orders: {stats['total']} | Revenue: ₱{stats['revenue'] or 0:.2f}",
                    font=("Segoe UI", 12), bg=self.bg_color, fg=self.accent_color).pack()
        except:
            pass
        
        # Filter frame
        filter_frame = tk.Frame(container, bg=self.bg_color)
        filter_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(filter_frame, text="Status:", font=("Segoe UI", 11),
                bg=self.bg_color, fg=self.text_color).pack(side='left', padx=(0, 10))
        
        self.all_orders_filter = tk.StringVar(value="All")
        
        for status in ["All", "Pending", "Approved", "Rejected"]:
            btn = tk.Button(filter_frame, text=status, font=("Segoe UI", 10),
                          bg=self.accent_color if status == "All" else self.secondary_bg,
                          fg=self.text_color, bd=0, cursor="hand2", padx=12, pady=6,
                          command=lambda s=status: self.filter_all_orders(s))
            btn.pack(side='left', padx=(0, 5))
        
        tk.Button(filter_frame, text="↻ Refresh", font=("Segoe UI", 10),
                 bg=self.secondary_bg, fg=self.text_color, bd=0, cursor="hand2",
                 padx=15, pady=6, command=lambda: self.load_all_orders_history("All")).pack(side='right')
        
        # Treeview
        columns = ('Order ID', 'User', 'Item', 'Qty', 'Price', 'Total', 'Status', 'Date')
        self.all_orders_tree = ttk.Treeview(container, columns=columns, show='headings', height=18)
        
        for col in columns:
            self.all_orders_tree.heading(col, text=col)
            if col == 'Order ID':
                self.all_orders_tree.column(col, width=80)
            elif col in ['User', 'Item']:
                self.all_orders_tree.column(col, width=150)
            elif col in ['Qty', 'Price', 'Total']:
                self.all_orders_tree.column(col, width=80)
            elif col == 'Status':
                self.all_orders_tree.column(col, width=100)
            else:
                self.all_orders_tree.column(col, width=130)
        
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.all_orders_tree.yview)
        self.all_orders_tree.configure(yscrollcommand=scrollbar.set)
        
        self.all_orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.load_all_orders_history("All")
    
    def filter_all_orders(self, status):
        """Filter all orders"""
        self.all_orders_filter.set(status)
        self.load_all_orders_history(status)
    def show_pc_instructions(self):
        """Show comprehensive instructions in a non-blocking popup"""
        # Dictionary of all instructions
        instructions_dict = {
            "PC Overview": """📖 PC UNIT OVERVIEW - HOW TO USE

    This panel shows all PC units in your internet cafe.

    STATUS COLORS:
    • 🟢 GREEN = Available
    • 🟡 YELLOW = Occupied  
    • 🔴 RED = Offline
    • ⚪ GRAY = Maintenance

    PC CARD BUTTONS:
    • ⚡ = Force Logout (end session)
    • 🔒 = Lock PC (prevent logins)
    • 🔓 = Unlock PC (allow logins)

    MANAGEMENT:
    • Auto-refreshes every 5 seconds
    • Monitor remaining session time
    • Force logout overstaying users
    • Lock PCs for maintenance""",

            "Inventory": """📦 INVENTORY MANAGEMENT

    ADDING/EDITING ITEMS:
    1. Fill in Item Name, Category, Quantity, Price, Min Stock
    2. Click "Add Item" to add new items
    3. Double-click items in list to edit
    4. Click "Update Item" to save changes

    INVENTORY STATUS:
    • 🟢 IN STOCK = Quantity > Minimum
    • 🟡 LOW STOCK = Quantity ≤ Minimum  
    • 🔴 OUT OF STOCK = Quantity = 0

    INTEGRATION:
    • Menu items check inventory stock
    • Orders deduct from inventory when approved
    • Real-time stock updates""",

            "Cafe Menu": """☕ CAFE MENU MANAGEMENT

    ADDING MENU ITEMS:
    1. Enter Item Name, Category, Price
    2. Check "Available for ordering"
    3. Optional: Upload image
    4. Click "Add Item" to save

    CATEGORIES:
    • Coffee, Food, Drinks, Snack, Dessert

    INVENTORY CHECK:
    • Menu items automatically check stock
    • Consider marking unavailable during low stock
    • Price updates reflect immediately""",

            "Account Creation": """➕ ACCOUNT CREATION

    VERIFICATION REQUIREMENTS:
    📋 MANDATORY ID CHECK:
    • Valid government ID required
    • Verify name matches ID exactly
    • Check age - NO MINORS AFTER 10PM
    • Record ID number

    SECURITY:
    • Password: 8+ chars, 1 number, 1 symbol
    • Unique username required
    • Full name must match ID

    AGE RESTRICTIONS:
    • STRICTLY NO MINORS (under 18) after 10PM
    • Verify age from valid ID
    • Keep ID records for compliance

    SETTINGS:
    • Initial Balance: Starting amount
    • Time Limit: Session minutes
    • Hourly Rate: Charging rate""",

            "Pending Accounts": """⏳ PENDING ACCOUNTS

    VERIFICATION PROCESS:
    1. Review application details
    2. Check ID verification status
    3. Verify age compliance
    4. Click "Approve" or "Reject"

    TOGGLE FEATURE:
    • Accounts can be toggled back to Pending
    • Use when additional verification needed
    • Example: User forgot ID

    REJECTION REASONS:
    • No valid ID presented
    • Age verification failed
    • Suspicious information
    • Duplicate account""",

            "All Users": """👥 ALL USERS MANAGEMENT

    USER ACTIONS:
    💰 ADD BALANCE - Add funds to account
    ⏱️ SET TIME LIMIT - Adjust session duration
    💵 SET RATE - Change hourly rate
    🔄 TOGGLE STATUS - Activate/deactivate
    🗑️ DELETE USER - Remove permanently

    FILTERS:
    • All: Show all users
    • Approved: Active accounts
    • Pending: Awaiting approval

    SEARCH:
    • Search by username or name
    • Real-time filtering""",

            "Order Management": """📋 ORDER MANAGEMENT

    WORKFLOW:
    1. User order → Shows as Pending
    2. Check inventory → Approve/Reject
    3. Approved → Deducts from inventory
    4. Rejected → Notify user

    APPROVAL:
    ✓ APPROVE ORDER:
    • Checks inventory first
    • Deducts quantity automatically
    • Updates inventory real-time

    ✗ REJECT ORDER:
    • Insufficient stock
    • Invalid order details
    • User notified

    FILTERS:
    • Pending: Need approval
    • Approved: Completed
    • All: All orders""",

            "All Orders": """📊 ALL ORDERS HISTORY

    COMPLETE HISTORY:
    • View all orders placed
    • Filter by status
    • Revenue statistics

    DETAILS SHOWN:
    • Order ID, User, Item, Qty
    • Price, Total Amount
    • Status, Date/Time

    REVENUE:
    • Total orders count
    • Total revenue generated
    • Sales trends

    REPORTING:
    • Export for accounting
    • Monitor sales trends
    • Identify popular items""",

            "General Guide": """🏢 GENERAL ADMIN GUIDE

    NAVIGATION:
    • Use sidebar to switch sections
    • Refresh buttons update data
    • Search functions available

    SECURITY:
    • Only authorized admins
    • Log out when leaving
    • Secure passwords

    COMPLIANCE:
    • Age verification mandatory
    • ID records maintenance
    • Operating hour compliance

    SUPPORT:
    • Help users with issues
    • Manage PC sessions
    • Handle order complaints"""
        }
        
        # Create a Toplevel window for the help center
        dialog = tk.Toplevel(self.root)
        dialog.title("Admin Help Center")
        dialog.geometry("800x650")
        dialog.configure(bg=self.bg_color)
        dialog.resizable(True, True)
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 400
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 325
        dialog.geometry(f"800x650+{x}+{y}")
        
        # Make it stay on top initially
        dialog.attributes('-topmost', True)
        dialog.after(100, lambda: dialog.attributes('-topmost', False))
        
        # Main container
        main_container = tk.Frame(dialog, bg=self.bg_color)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(main_container, text="ADMIN HELP CENTER", 
                font=("Segoe UI", 20, "bold"), bg=self.bg_color, 
                fg=self.accent_color).pack(pady=(0, 15))
        
        # Left frame for navigation
        nav_frame = tk.Frame(main_container, bg=self.secondary_bg, width=180)
        nav_frame.pack(side='left', fill='y')
        nav_frame.pack_propagate(False)
        
        # Right frame for content
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(side='right', fill='both', expand=True, padx=(20, 0))
        
        # Create text widget for content
        text_widget = tk.Text(content_frame, wrap='word', bg=self.secondary_bg,
                            fg=self.text_color, font=("Segoe UI", 10),
                            padx=15, pady=15, spacing2=5)
        text_widget.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for content
        scrollbar = tk.Scrollbar(content_frame, command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Navigation header
        tk.Label(nav_frame, text="📚 SECTIONS", font=("Segoe UI", 12, "bold"),
                bg=self.secondary_bg, fg=self.accent_color).pack(pady=(15, 10))
        
        # Create navigation buttons
        for section_name in instructions_dict.keys():
            btn = tk.Button(nav_frame, text=section_name, font=("Segoe UI", 10),
                        bg=self.secondary_bg, fg=self.text_color, bd=0,
                        cursor="hand2", anchor='w', padx=15, pady=8,
                        activebackground="#3d3d3d", activeforeground=self.text_color,
                        command=lambda s=section_name, tw=text_widget: 
                        self.update_help_content(s, tw, instructions_dict))
            btn.pack(fill='x', pady=2)
        
        # Add spacer
        tk.Frame(nav_frame, bg=self.secondary_bg, height=20).pack(fill='x')
        
        # Close button
        close_btn = tk.Button(nav_frame, text="✕ Close", font=("Segoe UI", 10, "bold"),
                            bg=self.danger_color, fg=self.text_color, bd=0,
                            cursor="hand2", padx=10, pady=10,
                            command=dialog.destroy)
        close_btn.pack(side='bottom', fill='x', pady=(0, 10))
        
        # Load initial content (PC Overview)
        self.update_help_content("PC Overview", text_widget, instructions_dict)
        
        # Focus on dialog
        dialog.focus_set()
        
        return dialog

    def update_help_content(self, section_name, text_widget, instructions_dict):
        """Update the help content based on selected section"""
        content = instructions_dict.get(section_name, "Content not available.")
        
        # Clear and update content
        text_widget.configure(state='normal')
        text_widget.delete('1.0', tk.END)
        
        # Insert content with formatting
        text_widget.insert('1.0', content)
        
        # Apply basic formatting
        text_widget.tag_configure("title", font=("Segoe UI", 12, "bold"),
                                foreground=self.accent_color, spacing3=10)
        text_widget.tag_configure("bullet", lmargin1=20, lmargin2=40)
        
        # Apply tags
        lines = content.split('\n')
        for i, line in enumerate(lines, start=1):
            if line.strip() and ':' in line and not line.startswith(' '):
                # This is a title line
                text_widget.tag_add("title", f"{i}.0", f"{i}.end")
            elif line.strip().startswith('•'):
                text_widget.tag_add("bullet", f"{i}.0", f"{i}.end")
        
        text_widget.configure(state='disabled')
        text_widget.see('1.0')  # Scroll to top
    
    def load_all_orders_history(self, status_filter):
        """Load all orders"""
        try:
            for item in self.all_orders_tree.get_children():
                self.all_orders_tree.delete(item)
            
            cursor = self.db_connection.cursor(dictionary=True)
            
            if status_filter == "All":
                cursor.execute("""
                    SELECT o.order_id, u.username, o.item_name, o.quantity, 
                           o.price, o.total_price, o.order_status, o.order_date
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    ORDER BY o.order_date DESC
                """)
            else:
                cursor.execute("""
                    SELECT o.order_id, u.username, o.item_name, o.quantity, 
                           o.price, o.total_price, o.order_status, o.order_date
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    WHERE o.order_status = %s
                    ORDER BY o.order_date DESC
                """, (status_filter,))
            
            orders = cursor.fetchall()
            cursor.close()
            
            for order in orders:
                self.all_orders_tree.insert('', tk.END, values=(
                    order['order_id'],
                    order['username'],
                    order['item_name'],
                    order['quantity'],
                    f"₱{order['price']:.2f}",
                    f"₱{order['total_price']:.2f}",
                    order['order_status'],
                    order['order_date'].strftime("%Y-%m-%d %H:%M")
                ))
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading orders: {e}")
    
    def show_kiosk_control(self, parent):
        """Display kiosk mode control panel"""
        self.clear_content(parent)
        
        container = tk.Frame(parent, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        tk.Label(container, text="Kiosk Mode Control", font=("Segoe UI", 32, "bold"),
                bg=self.bg_color, fg=self.text_color).pack(anchor='w', pady=(0, 30))
        
        # Main control frame
        control_frame = tk.Frame(container, bg=self.secondary_bg, padx=50, pady=40)
        control_frame.pack(fill='x', pady=(0, 30))
        
        # Current status
        status_frame = tk.Frame(control_frame, bg=self.secondary_bg)
        status_frame.pack(fill='x', pady=(0, 30))
        
        tk.Label(status_frame, text="Current Kiosk Mode Status:", font=("Segoe UI", 16, "bold"),
                bg=self.secondary_bg, fg=self.text_color).pack(anchor='w')
        
        # Get current kiosk mode status from database
        kiosk_status = self.get_kiosk_mode_status()
        status_color = self.success_color if kiosk_status else self.danger_color
        status_text = "🔒 ENABLED" if kiosk_status else "🔓 DISABLED"
        
        self.kiosk_status_label = tk.Label(status_frame, text=status_text, 
                                          font=("Segoe UI", 20, "bold"),
                                          bg=self.secondary_bg, fg=status_color)
        self.kiosk_status_label.pack(anchor='w', pady=(10, 0))
        
        # Description
        desc_frame = tk.Frame(control_frame, bg=self.secondary_bg)
        desc_frame.pack(fill='x', pady=(0, 30))
        
        if kiosk_status:
            desc_text = ("Kiosk Mode is currently ENABLED:\n"
                        "• Users cannot Alt+Tab or switch windows\n"
                        "• Task Manager and system keys are blocked\n"
                        "• Full-screen lock is active\n"
                        "• Enhanced security is in effect")
        else:
            desc_text = ("Kiosk Mode is currently DISABLED:\n"
                        "• Users can switch between applications\n"
                        "• System keys are functional\n"
                        "• Normal window behavior\n"
                        "• Reduced security mode")
        
        self.kiosk_desc_label = tk.Label(desc_frame, text=desc_text, 
                                        font=("Segoe UI", 12),
                                        bg=self.secondary_bg, fg=self.text_secondary,
                                        justify='left')
        self.kiosk_desc_label.pack(anchor='w')
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg=self.secondary_bg)
        button_frame.pack(fill='x', pady=(30, 0))
        
        # Toggle button
        if kiosk_status:
            toggle_text = "🔓 DISABLE Kiosk Mode"
            toggle_color = self.danger_color
            toggle_command = self.disable_global_kiosk_mode
        else:
            toggle_text = "🔒 ENABLE Kiosk Mode"
            toggle_color = self.success_color
            toggle_command = self.enable_global_kiosk_mode
        
        self.kiosk_toggle_btn = tk.Button(button_frame, text=toggle_text, 
                                         font=("Segoe UI", 14, "bold"),
                                         bg=toggle_color, fg="white", bd=0, cursor="hand2",
                                         padx=30, pady=15, command=toggle_command)
        self.kiosk_toggle_btn.pack(side='left', padx=(0, 20))
        
        # Refresh button
        tk.Button(button_frame, text="↻ Refresh Status", font=("Segoe UI", 12),
                 bg=self.accent_color, fg="white", bd=0, cursor="hand2",
                 padx=25, pady=15, 
                 command=lambda: self.show_kiosk_control(parent)).pack(side='left')
        
        # Warning section
        warning_frame = tk.Frame(container, bg="#2d1810", relief='solid', bd=2)
        warning_frame.pack(fill='x', pady=(20, 0))
        
        tk.Label(warning_frame, text="⚠️ IMPORTANT NOTES", font=("Segoe UI", 14, "bold"),
                bg="#2d1810", fg="#FFA726").pack(pady=(15, 10))
        
        warning_text = ("• Kiosk Mode affects ALL user sessions system-wide\n"
                       "• Changes take effect immediately for new logins\n"
                       "• Existing user sessions may need to be restarted\n"
                       "• Admin panels are not affected by kiosk mode\n"
                       "• Emergency exit is always available regardless of mode")
        
        tk.Label(warning_frame, text=warning_text, font=("Segoe UI", 11),
                bg="#2d1810", fg="white", justify='left').pack(padx=20, pady=(0, 15))
    
    def get_kiosk_mode_status(self):
        """Get kiosk mode status from database"""
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_name = 'kiosk_mode_enabled'")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result['setting_value'].lower() == 'true'
            else:
                # Default to enabled for security
                return True
                
        except Error:
            # Default to enabled for security
            return True
    
    def enable_global_kiosk_mode(self):
        """Enable kiosk mode globally"""
        if messagebox.askyesno("Enable Kiosk Mode", 
                              "Enable Kiosk Mode for all user sessions?\n\n"
                              "This will:\n"
                              "• Block Alt+Tab and system keys\n"
                              "• Enable full-screen lock for users\n"
                              "• Enhance security system-wide\n\n"
                              "Changes take effect for new user logins."):
            
            try:
                # Store kiosk mode preference in database
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        setting_name VARCHAR(50) PRIMARY KEY,
                        setting_value VARCHAR(100),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO system_settings (setting_name, setting_value) 
                    VALUES ('kiosk_mode_enabled', 'true')
                    ON DUPLICATE KEY UPDATE setting_value = 'true'
                """)
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Kiosk Mode Enabled", 
                                  "Kiosk Mode has been ENABLED system-wide.\n\n"
                                  "New user logins will have enhanced security features.")
                
                # Try to enable kiosk mode on main app if it exists
                self.notify_main_app_kiosk_change(True)
                
                # Refresh the control panel
                parent = None
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Frame):
                        parent = widget
                        break
                if parent:
                    self.show_kiosk_control(parent)
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error enabling kiosk mode: {e}")
    
    def disable_global_kiosk_mode(self):
        """Disable kiosk mode globally"""
        if messagebox.askyesno("Disable Kiosk Mode", 
                              "Disable Kiosk Mode for all user sessions?\n\n"
                              "⚠️ WARNING: This will reduce security!\n\n"
                              "This will:\n"
                              "• Allow Alt+Tab and system keys\n"
                              "• Disable full-screen lock\n"
                              "• Reduce security system-wide\n\n"
                              "Are you sure you want to continue?"):
            
            try:
                # Store kiosk mode preference in database
                cursor = self.db_connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_settings (
                        setting_name VARCHAR(50) PRIMARY KEY,
                        setting_value VARCHAR(100),
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    INSERT INTO system_settings (setting_name, setting_value) 
                    VALUES ('kiosk_mode_enabled', 'false')
                    ON DUPLICATE KEY UPDATE setting_value = 'false'
                """)
                
                self.db_connection.commit()
                cursor.close()
                
                messagebox.showinfo("Kiosk Mode Disabled", 
                                  "Kiosk Mode has been DISABLED system-wide.\n\n"
                                  "⚠️ Security features are now reduced.\n"
                                  "New user logins will have normal window behavior.")
                
                # Try to disable kiosk mode on main app if it exists
                self.notify_main_app_kiosk_change(False)
                
                # Refresh the control panel
                parent = None
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Frame):
                        parent = widget
                        break
                if parent:
                    self.show_kiosk_control(parent)
                
            except Error as e:
                messagebox.showerror("Database Error", f"Error disabling kiosk mode: {e}")
    
    def notify_main_app_kiosk_change(self, enable_kiosk):
        """Notify main application about kiosk mode changes"""
        try:
            # Try to find the main application window
            main_window = None
            
            # Look through all top-level windows
            for widget in self.root.winfo_toplevel().winfo_children():
                # Check if this widget has the methods we need (main app)
                if hasattr(widget, 'enable_pc_lock') and hasattr(widget, 'disable_pc_lock'):
                    main_window = widget
                    break
            
            if main_window:
                if enable_kiosk:
                    main_window.enable_pc_lock()
                    print("🔧 Notified main app to enable kiosk mode")
                else:
                    main_window.disable_pc_lock()
                    print("🔧 Notified main app to disable kiosk mode")
            else:
                print("🔧 Could not find main app to notify about kiosk mode change")
                
        except Exception as e:
            print(f"🔧 Error notifying main app about kiosk mode change: {e}")


# Don't forget to keep the __main__ section at the end of admin_panel.py
if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()