import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
from datetime import datetime, timedelta
from database import Database

class AdminLogin:
    def __init__(self, window, main_root):
        self.window = window
        self.main_root = main_root
        
        self.window.title("Admin Login")
        self.window.geometry("500x400")
        self.window.configure(bg='#f0f0f0')
        self.window.resizable(False, False)
        
        # Center the window
        self.window.transient(main_root)
        
        # Admin credentials
        self.admin_user = "admin"
        self.admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        
        # Color definitions
        self.bg_color = '#f0f0f0'
        self.accent_color = '#2196F3'
        self.text_color = '#333333'
        self.card_color = '#ffffff'
        self.warning_color = '#ff9800'
        
        # Initialize database
        self.db = Database()
        if not self.db.connect():
            messagebox.showerror("Database Error", "Could not connect to database")
            self.window.destroy()
            return
        
        # Setup database if needed
        self.db.setup_database()
        
        # Load data from database
        self.load_data_from_db()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Admin Login",
            font=("Arial", 28, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 40))
        
        # Username
        username_frame = tk.Frame(main_frame, bg='#f0f0f0')
        username_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            username_frame,
            text="Admin Username:",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#333333"
        ).pack(anchor='w')
        
        self.username_entry = tk.Entry(
            username_frame,
            font=("Arial", 14),
            width=30
        )
        self.username_entry.pack(pady=(5, 0))
        self.username_entry.insert(0, "admin")  # Pre-fill
        
        # Password
        password_frame = tk.Frame(main_frame, bg='#f0f0f0')
        password_frame.pack(fill='x', pady=(0, 30))
        
        tk.Label(
            password_frame,
            text="Admin Password:",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#333333"
        ).pack(anchor='w')
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 14),
            width=30,
            show="•"
        )
        self.password_entry.pack(pady=(5, 0))
        
        # Login button
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=(10, 0))
        
        login_button = tk.Button(
            button_frame,
            text="Login as Admin",
            font=("Arial", 16, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            command=self.login
        )
        login_button.pack(pady=(0, 20))
        
        # Back button
        back_button = tk.Button(
            button_frame,
            text="← Back to Login Selector",
            font=("Arial", 12),
            bg="#cccccc",
            fg="black",
            command=self.go_back
        )
        back_button.pack()
        
        # Demo credentials label
        demo_label = tk.Label(
            main_frame,
            text="Demo: admin / admin123",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        demo_label.pack(side='bottom', pady=(20, 0))
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.login())
        
        # Focus on password field
        self.password_entry.focus_set()
    # In your database.py, add this method:

    def create_user_direct(self, username, password, full_name, phone, birthday, points=100, minutes=0):
        """Create a new user directly (admin creates user)"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, phone, birthday, 
                                points, remaining_minutes, is_approved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
            ''', (username, password_hash, full_name, phone, birthday, points, minutes))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error creating user: {err}")
            return False
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Missing Information", 
                                 "Please enter both username and password")
            return
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        if username == self.admin_user and password_hash == self.admin_password_hash:
            messagebox.showinfo("Login Successful", 
                              "Welcome, System Administrator!")
            
            # Clear fields
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            
            # Open admin dashboard
            self.open_admin_dashboard()
        else:
            messagebox.showerror("Login Failed", 
                               "Invalid admin credentials")
    
    def open_admin_dashboard(self):
        """Open main admin dashboard"""
        self.window.withdraw()  # Hide login window
        
        dashboard = tk.Toplevel(self.main_root)
        dashboard.title("Admin Dashboard")
        dashboard.geometry("1200x800")
        dashboard.configure(bg='#f5f5f5')
        
        # Store reference to dashboard
        self.dashboard = dashboard
        
        # Navigation bar
        self.create_navbar(dashboard)
        
        # Default view (PC Overview)
        self.show_pc_overview(dashboard)
        
        # Bind close event
        dashboard.protocol("WM_DELETE_WINDOW", lambda: self.on_dashboard_close(dashboard))
    
    def create_navbar(self, parent):
        """Create navigation bar with tabs"""
        navbar = tk.Frame(parent, bg='#2c3e50', height=60)
        navbar.pack(fill='x', side='top')
        navbar.pack_propagate(False)
        
        # Welcome label
        welcome_label = tk.Label(
            navbar,
            text="# Admin Dashboard\nWelcome, System Administrator",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white",
            justify='left'
        )
        welcome_label.pack(side='left', padx=20)
        
        # Navigation buttons frame
        nav_buttons = tk.Frame(navbar, bg="#2c3e50")
        nav_buttons.pack(side='right', padx=20)
        
        # Navigation buttons
        nav_items = [
            ("PC Overview", self.show_pc_overview),
            ("Account Requests", self.show_account_requests),
            ("User Management", self.show_user_management),
            ("Create User", self.show_create_user),  # NEW: Direct user creation
            ("Orders", self.show_orders),
            ("Inventory", self.show_inventory),
            ("Rewards", self.show_rewards),
            ("Analytics", self.show_analytics)
        ]
        
        for text, command in nav_items:
            btn = tk.Button(
                nav_buttons,
                text=text,
                font=("Arial", 11),
                bg="#34495e",
                fg="white",
                relief="flat",
                padx=15,
                pady=8,
                command=lambda c=command: c(parent)
            )
            btn.pack(side='left', padx=5)
        
        # Logout button
        logout_btn = tk.Button(
            navbar,
            text="Logout",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            command=lambda: self.on_dashboard_close(parent)
        )
        logout_btn.pack(side='right', padx=10)
    
    def show_pc_overview(self, parent):
        """Show PC Overview tab"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="PC Units Status",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))
        
        # PC Grid (2 rows of 5)
        pc_grid = tk.Frame(content, bg='white')
        pc_grid.pack()
        
        colors = {"Available": "#2ecc71", "Occupied": "#e74c3c", "Maintenance": "#f39c12"}
        
        for i, pc in enumerate(self.pc_units):
            row = i // 5
            col = i % 5
            
            pc_frame = tk.Frame(pc_grid, bg='#f8f9fa', relief='solid', bd=1)
            pc_frame.grid(row=row, column=col, padx=10, pady=10, ipadx=20, ipady=20)
            
            tk.Label(
                pc_frame,
                text=pc["name"],
                font=("Arial", 14, "bold"),
                bg='#f8f9fa',
                fg='#2c3e50'
            ).pack()
            
            status_color = colors.get(pc["status"], "#95a5a6")
            tk.Label(
                pc_frame,
                text=pc["status"],
                font=("Arial", 12),
                bg='#f8f9fa',
                fg=status_color
            ).pack()
        
        # Quick Stats
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=30)
        
        stats_frame = tk.Frame(content, bg='white')
        stats_frame.pack()
        
        available = len([pc for pc in self.pc_units if pc["status"] == "Available"])
        occupied = len([pc for pc in self.pc_units if pc["status"] == "Occupied"])
        maintenance = len([pc for pc in self.pc_units if pc["status"] == "Maintenance"])
        
        stats = [
            ("Available", str(available), "#2ecc71"),
            ("Occupied", str(occupied), "#e74c3c"),
            ("Maintenance", str(maintenance), "#f39c12")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg='white')
            stat_frame.grid(row=0, column=i, padx=40, pady=20)
            
            tk.Label(
                stat_frame,
                text=value,
                font=("Arial", 36, "bold"),
                bg="white",
                fg=color
            ).pack()
            
            tk.Label(
                stat_frame,
                text=label,
                font=("Arial", 14),
                bg="white",
                fg="#7f8c8d"
            ).pack()
    def show_create_user(self, parent):
        """Show direct user creation form (admin creates users directly)"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Create User  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="Create New User Account",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))
        
        # Create scrollable frame
        canvas = tk.Canvas(content, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Form container
        form_container = tk.Frame(scrollable_frame, bg='white')
        form_container.pack(fill='x', padx=50, pady=30)
        
        # --- Login Information ---
        login_section = tk.LabelFrame(form_container, text="Login Information", 
                                    font=("Arial", 14, "bold"), bg="white", fg="#333333", 
                                    padx=20, pady=20)
        login_section.pack(fill='x', pady=(0, 30))
        
        # Username
        tk.Label(
            login_section,
            text="Username*",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        username_entry = tk.Entry(
            login_section,
            font=("Arial", 14),
            width=40
        )
        username_entry.pack(pady=(0, 15))
        
        # Password
        tk.Label(
            login_section,
            text="Password*",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        password_entry = tk.Entry(
            login_section,
            font=("Arial", 14),
            width=40,
            show="•"
        )
        password_entry.pack(pady=(0, 15))
        
        # Confirm Password
        tk.Label(
            login_section,
            text="Confirm Password*",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        confirm_password_entry = tk.Entry(
            login_section,
            font=("Arial", 14),
            width=40,
            show="•"
        )
        confirm_password_entry.pack()
        
        # --- Personal Information ---
        personal_section = tk.LabelFrame(form_container, text="Personal Information", 
                                    font=("Arial", 14, "bold"), bg="white", fg="#333333", 
                                    padx=20, pady=20)
        personal_section.pack(fill='x', pady=(0, 30))
        
        # Full Name
        tk.Label(
            personal_section,
            text="Full Name*",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        full_name_entry = tk.Entry(
            personal_section,
            font=("Arial", 14),
            width=40
        )
        full_name_entry.pack(pady=(0, 15))
        
        # Phone Number
        tk.Label(
            personal_section,
            text="Phone Number*",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        phone_entry = tk.Entry(
            personal_section,
            font=("Arial", 14),
            width=40
        )
        phone_entry.pack(pady=(0, 15))
        
        # Birthday
        tk.Label(
            personal_section,
            text="Birthday (YYYY-MM-DD)*",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        birthday_entry = tk.Entry(
            personal_section,
            font=("Arial", 14),
            width=20
        )
        birthday_entry.pack(anchor='w')
        birthday_entry.insert(0, "2000-01-01")
        
        # --- Initial Settings ---
        settings_section = tk.LabelFrame(form_container, text="Initial Settings", 
                                    font=("Arial", 14, "bold"), bg="white", fg="#333333", 
                                    padx=20, pady=20)
        settings_section.pack(fill='x', pady=(0, 30))
        
        # Starting Points
        tk.Label(
            settings_section,
            text="Starting Points",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        points_entry = tk.Entry(
            settings_section,
            font=("Arial", 14),
            width=20
        )
        points_entry.pack(anchor='w', pady=(0, 15))
        points_entry.insert(0, "100")
        
        # Starting Minutes
        tk.Label(
            settings_section,
            text="Starting Minutes",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#333333"
        ).pack(anchor='w', pady=(0, 5))
        
        minutes_entry = tk.Entry(
            settings_section,
            font=("Arial", 14),
            width=20
        )
        minutes_entry.pack(anchor='w')
        minutes_entry.insert(0, "0")
        
        # --- Submit Button ---
        button_frame = tk.Frame(form_container, bg='white')
        button_frame.pack(pady=30)
        
        def create_user():
            # Get all values
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            confirm_pass = confirm_password_entry.get().strip()
            full_name = full_name_entry.get().strip()
            phone = phone_entry.get().strip()
            birthday = birthday_entry.get().strip()
            
            try:
                points = int(points_entry.get().strip())
                minutes = int(minutes_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Points and minutes must be numbers")
                return
            
            # Validation
            errors = []
            
            if not username:
                errors.append("Username is required")
            elif len(username) < 3:
                errors.append("Username must be at least 3 characters")
            
            if not password:
                errors.append("Password is required")
            elif len(password) < 6:
                errors.append("Password must be at least 6 characters")
            
            if password != confirm_pass:
                errors.append("Passwords do not match")
            
            if not full_name:
                errors.append("Full name is required")
            
            if not phone:
                errors.append("Phone number is required")
            
            if not birthday:
                errors.append("Birthday is required")
            
            if errors:
                error_msg = "\n".join(f"• {error}" for error in errors)
                messagebox.showerror("Validation Error", f"Please fix the following errors:\n\n{error_msg}")
                return
            
            # Create user directly (approved immediately)
            if self.db.create_user_direct(username, password, full_name, phone, birthday, points, minutes):
                messagebox.showinfo("Success", 
                                f"User '{username}' created successfully!\n\n"
                                f"• Full Name: {full_name}\n"
                                f"• Phone: {phone}\n"
                                f"• Starting Points: {points}\n"
                                f"• Starting Minutes: {minutes}")
                
                # Clear form
                username_entry.delete(0, tk.END)
                password_entry.delete(0, tk.END)
                confirm_password_entry.delete(0, tk.END)
                full_name_entry.delete(0, tk.END)
                phone_entry.delete(0, tk.END)
                birthday_entry.delete(0, tk.END)
                birthday_entry.insert(0, "2000-01-01")
                points_entry.delete(0, tk.END)
                points_entry.insert(0, "100")
                minutes_entry.delete(0, tk.END)
                minutes_entry.insert(0, "0")
                
                # Refresh users list
                self.load_data_from_db()
            else:
                messagebox.showerror("Error", 
                                "Failed to create user. Username might already exist.")
        
        # Create and Reset buttons
        action_frame = tk.Frame(button_frame, bg='white')
        action_frame.pack()
        
        tk.Button(
            action_frame,
            text="Create User",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            command=create_user
        ).pack(side='left', padx=(0, 20))
        
        tk.Button(
            action_frame,
            text="Reset Form",
            font=("Arial", 14),
            bg="#FF9800",
            fg="white",
            width=12,
            command=lambda: [
                username_entry.delete(0, tk.END),
                password_entry.delete(0, tk.END),
                confirm_password_entry.delete(0, tk.END),
                full_name_entry.delete(0, tk.END),
                phone_entry.delete(0, tk.END),
                birthday_entry.delete(0, tk.END),
                birthday_entry.insert(0, "2000-01-01"),
                points_entry.delete(0, tk.END),
                points_entry.insert(0, "100"),
                minutes_entry.delete(0, tk.END),
                minutes_entry.insert(0, "0"),
                username_entry.focus_set()
            ]
        ).pack(side='left')
        
        # Back button
        tk.Button(
            button_frame,
            text="Back to User Management",
            font=("Arial", 12),
            bg="#cccccc",
            fg="#333333",
            command=lambda: self.show_user_management(parent)
        ).pack(pady=(20, 0))
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Set focus to first field
        username_entry.focus_set()
    
    def show_account_requests(self, parent):
        """Show Account Requests tab"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="Pending Account Requests",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))


        # Refresh button
        refresh_frame = tk.Frame(content, bg='white')
        refresh_frame.pack(anchor='e', pady=(0, 20))
        
        tk.Button(
            refresh_frame,
            text="Refresh List",
            bg="#3498db",
            fg="white",
            font=("Arial", 10),
            padx=15,
            pady=5,
            command=lambda: [self.load_data_from_db(), self.show_account_requests(parent)]
        ).pack()
        
        # Display pending requests
        if self.account_requests:
            for req in self.account_requests:
                if req.get("status") == "Pending":
                    request_frame = tk.Frame(content, bg='#f8f9fa', relief='solid', bd=1)
                    request_frame.pack(fill='x', pady=10, padx=20, ipady=20)
                    
                    # Header
                    header_frame = tk.Frame(request_frame, bg='#f8f9fa')
                    header_frame.pack(fill='x', padx=20, pady=(10, 0))
                    
                    tk.Label(
                        header_frame,
                        text=f"• {req.get('full_name', 'N/A')} (@{req.get('username', 'N/A')})",
                        font=("Arial", 14, "bold"),
                        bg='#f8f9fa',
                        fg='#2c3e50'
                    ).pack(side='left')
                    
                    # Details
                    details_frame = tk.Frame(request_frame, bg='#f8f9fa')
                    details_frame.pack(fill='x', padx=40, pady=10)
                    
                    details = [
                        ("Full Name:", req.get('full_name', 'N/A')),
                        ("Username:", req.get('username', 'N/A')),
                        ("Phone:", req.get('phone', 'N/A')),
                        ("Birthday:", req.get('birthday', 'N/A')),
                        ("Requested:", req.get('requested_at', 'N/A'))
                    ]
                    
                    for label, value in details:
                        detail_frame = tk.Frame(details_frame, bg='#f8f9fa')
                        detail_frame.pack(anchor='w', pady=2)
                        
                        tk.Label(
                            detail_frame,
                            text=label,
                            font=("Arial", 11, "bold"),
                            bg='#f8f9fa',
                            fg='#34495e',
                            width=12,
                            anchor='w'
                        ).pack(side='left')
                        
                        tk.Label(
                            detail_frame,
                            text=value,
                            font=("Arial", 11),
                            bg='#f8f9fa',
                            fg='#2c3e50'
                        ).pack(side='left')
                    
                    # Action buttons
                    action_frame = tk.Frame(request_frame, bg='#f8f9fa')
                    action_frame.pack(pady=(10, 10))
                    
                    tk.Button(
                        action_frame,
                        text="Approve",
                        bg="#2ecc71",
                        fg="white",
                        font=("Arial", 11, "bold"),
                        padx=20,
                        pady=5,
                        command=lambda r=req: self.approve_request(r)
                    ).pack(side='left', padx=5)
                    
                    tk.Button(
                        action_frame,
                        text="Decline",
                        bg="#e74c3c",
                        fg="white",
                        font=("Arial", 11, "bold"),
                        padx=20,
                        pady=5,
                        command=lambda r=req: self.decline_request(r)
                    ).pack(side='left', padx=5)
        else:
            tk.Label(
                content,
                text="No pending account requests",
                font=("Arial", 14),
                bg="white",
                fg="#7f8c8d"
            ).pack(pady=50)
    
    def show_user_management(self, parent):
        """Show User Management tab"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="User Management",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))
        
        # Search bar
        search_frame = tk.Frame(content, bg='white')
        search_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            search_frame,
            text="Search by username or name",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(side='left', padx=(0, 10))
        
        search_entry = tk.Entry(
            search_frame,
            font=("Arial", 12),
            width=30
        )
        search_entry.pack(side='left')
        
        # Users list
        for user in self.users:
            user_frame = tk.Frame(content, bg='#f8f9fa', relief='solid', bd=1)
            user_frame.pack(fill='x', pady=10, padx=20, ipady=20)
            
            # User info
            info_frame = tk.Frame(user_frame, bg='#f8f9fa')
            info_frame.pack(fill='x', padx=20, pady=10)
            
            # Left column
            left_frame = tk.Frame(info_frame, bg='#f8f9fa')
            left_frame.pack(side='left', fill='y')
            
            tk.Label(
                left_frame,
                text=f"• {user.get('full_name', 'N/A')} (@{user.get('username', 'N/A')}) - {user.get('remaining_minutes', 0)} min remaining",
                font=("Arial", 12, "bold"),
                bg='#f8f9fa',
                fg='#2c3e50'
            ).pack(anchor='w', pady=2)
            
            details_left = [
                ("Full Name:", user.get('full_name', 'N/A')),
                ("Username:", user.get('username', 'N/A')),
                ("Phone:", user.get('phone', 'N/A')),
                ("Birthday:", user.get('birthday', 'N/A')),
                ("Member Since:", user.get('created_at', 'N/A')[:10] if user.get('created_at') else 'N/A')
            ]
            
            for i in range(0, len(details_left), 2):
                row_frame = tk.Frame(left_frame, bg='#f8f9fa')
                row_frame.pack(anchor='w', pady=2)
                
                tk.Label(
                    row_frame,
                    text=details_left[i][0],
                    font=("Arial", 10, "bold"),
                    bg='#f8f9fa',
                    fg='#34495e',
                    width=15,
                    anchor='w'
                ).pack(side='left')
                
                tk.Label(
                    row_frame,
                    text=details_left[i][1],
                    font=("Arial", 10),
                    bg='#f8f9fa',
                    fg='#2c3e50'
                ).pack(side='left')
                
                if i+1 < len(details_left):
                    tk.Label(
                        row_frame,
                        text=details_left[i+1][0],
                        font=("Arial", 10, "bold"),
                        bg='#f8f9fa',
                        fg='#34495e',
                        width=15,
                        anchor='w'
                    ).pack(side='left', padx=(20, 0))
                    
                    if details_left[i+1][1]:
                        tk.Label(
                            row_frame,
                            text=details_left[i+1][1],
                            font=("Arial", 10),
                            bg='#f8f9fa',
                            fg='#2c3e50'
                        ).pack(side='left')
            
            # Right column (points and actions)
            right_frame = tk.Frame(info_frame, bg='#f8f9fa')
            right_frame.pack(side='right', fill='y')
            
            tk.Label(
                right_frame,
                text=f"Points: {user.get('points', 0)}",
                font=("Arial", 12, "bold"),
                bg='#f8f9fa',
                fg='#2c3e50'
            ).pack(anchor='e', pady=2)
            
            tk.Label(
                right_frame,
                text=f"Current Streak: {user.get('streak', 0)} days",
                font=("Arial", 10),
                bg='#f8f9fa',
                fg='#7f8c8d'
            ).pack(anchor='e', pady=(0, 10))
            
            # Reset password section
            tk.Label(
                right_frame,
                text="Reset Password",
                font=("Arial", 11, "bold"),
                bg='#f8f9fa',
                fg='#34495e'
            ).pack(anchor='e', pady=(10, 5))
            
            pass_frame = tk.Frame(right_frame, bg='#f8f9fa')
            pass_frame.pack(anchor='e', pady=5)
            
            tk.Label(
                pass_frame,
                text="New password",
                font=("Arial", 10),
                bg='#f8f9fa',
                fg='#7f8c8d'
            ).pack(anchor='e')
            
            new_pass = tk.Entry(pass_frame, font=("Arial", 10), width=20)
            new_pass.pack(anchor='e', pady=2)
            
            tk.Button(
                pass_frame,
                text="Reset",
                bg="#3498db",
                fg="white",
                font=("Arial", 10),
                padx=10,
                pady=2,
                command=lambda u=user, p=new_pass: self.reset_password(u, p)
            ).pack(anchor='e')
    
    def show_inventory(self, parent):
        """Show Inventory Management tab"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="Inventory Management",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))
        
        # Create table using Treeview
        columns = ("ID", "Name", "Category", "Price", "Stock")
        tree = ttk.Treeview(content, columns=columns, show="headings", height=10)
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')
        
        # Add data
        for item in self.inventory:
            tree.insert("", "end", values=(
                item["id"],
                item["name"],
                item["category"],
                f"${item['price']:.2f}",
                item["stock"]
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree.pack(side='left', fill='both', expand=True, padx=(0, 10))
        scrollbar.pack(side='right', fill='y')
        
        # Action buttons frame
        action_frame = tk.Frame(content, bg='white')
        action_frame.pack(fill='x', pady=20)
        
        tk.Button(
            action_frame,
            text="Update Stock",
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10,
            command=self.show_update_stock
        ).pack(side='left', padx=10)
        
        tk.Button(
            action_frame,
            text="Add Product",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10,
            command=self.show_add_product
        ).pack(side='left', padx=10)
    
    def show_analytics(self, parent):
        """Show Analytics tab"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="Usage Analytics & Reports",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))
        
        # Quick stats
        stats_frame = tk.Frame(content, bg='white')
        stats_frame.pack(fill='x', pady=(0, 30))
        
        total_users = len(self.users)
        total_sessions = len(self.recent_sessions)
        total_orders = len(self.orders)
        total_revenue = sum(order.get("amount", 0) for order in self.orders)
        
        quick_stats = [
            ("Total Users", str(total_users)),
            ("Total Sessions", str(total_sessions)),
            ("Total Orders", str(total_orders)),
            ("Total Revenue", f"${total_revenue:.2f}")
        ]
        
        for i, (label, value) in enumerate(quick_stats):
            stat_frame = tk.Frame(stats_frame, bg='white')
            stat_frame.grid(row=0, column=i, padx=20, pady=10)
            
            tk.Label(
                stat_frame,
                text=value,
                font=("Arial", 24, "bold"),
                bg="white",
                fg="#3498db"
            ).pack()
            
            tk.Label(
                stat_frame,
                text=label,
                font=("Arial", 12),
                bg="white",
                fg="#7f8c8d"
            ).pack()
        
        # Top Users by Points
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=30)
        
        tk.Label(
            content,
            text="Top Users by Points",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        # Create table for top users
        user_columns = ("Username", "Full Name", "Points", "Streak")
        user_tree = ttk.Treeview(content, columns=user_columns, show="headings", height=5)
        
        for col in user_columns:
            user_tree.heading(col, text=col)
            user_tree.column(col, width=150, anchor='center')
        
        # Sort users by points (descending)
        sorted_users = sorted(self.users, key=lambda x: x.get("points", 0), reverse=True)
        for i, user in enumerate(sorted_users):
            user_tree.insert("", "end", values=(
                user.get("username", ""),
                user.get("full_name", ""),
                user.get("points", 0),
                user.get("streak", 0)
            ))
        
        user_tree.pack(fill='x', pady=10)
        
        # Recent Sessions
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=30)
        
        tk.Label(
            content,
            text="Recent Sessions",
            font=("Arial", 16, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        # Create table for recent sessions
        session_columns = ("User", "PC", "Start", "Min")
        session_tree = ttk.Treeview(content, columns=session_columns, show="headings", height=5)
        
        for col in session_columns:
            session_tree.heading(col, text=col)
            session_tree.column(col, width=150, anchor='center')
        
        for session in self.recent_sessions:
            session_tree.insert("", "end", values=(
                session.get("user", ""),
                session.get("pc", ""),
                session.get("start", ""),
                session.get("minutes", 0)
            ))
        
        session_tree.pack(fill='x', pady=10)
    
    def show_orders(self, parent):
        """Show Orders Management tab"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            content,
            text="# Admin Dashboard",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 10))
        
        tk.Label(
            content,
            text="PC Overview  Account Requests  User Management  Orders  Inventory  Rewards  Analytics",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack(anchor='w', pady=(0, 20))
        
        # Separator
        tk.Frame(content, height=2, bg='#ecf0f1').pack(fill='x', pady=20)
        
        # Title
        tk.Label(
            content,
            text="Orders Management",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(anchor='w', pady=(0, 20))
        
        # Filter
        filter_frame = tk.Frame(content, bg='white')
        filter_frame.pack(anchor='w', pady=(0, 20))
        
        tk.Label(
            filter_frame,
            text="Filter by status",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(side='left', padx=(0, 10))
        
        status_var = tk.StringVar(value="All")
        status_options = ["All", "Pending", "Completed", "Cancelled"]
        
        for status in status_options:
            tk.Radiobutton(
                filter_frame,
                text=status,
                variable=status_var,
                value=status,
                bg="white",
                font=("Arial", 10)
            ).pack(side='left', padx=5)
        
        # Orders display
        if self.orders:
            # Create table for orders
            pass
        else:
            tk.Label(
                content,
                text="No orders found",
                font=("Arial", 14),
                bg="white",
                fg="#7f8c8d"
            ).pack(pady=50)
    
    def show_rewards(self, parent):
        """Show Rewards tab (placeholder)"""
        self.clear_content(parent)
        
        content = tk.Frame(parent, bg='white')
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            content,
            text="Rewards Management",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=50)
        
        tk.Label(
            content,
            text="Rewards system coming soon...",
            font=("Arial", 14),
            bg="white",
            fg="#7f8c8d"
        ).pack()
    
    def show_update_stock(self):
        """Show Update Stock popup"""
        popup = tk.Toplevel(self.dashboard)
        popup.title("Update Stock")
        popup.geometry("400x300")
        popup.configure(bg='white')
        popup.resizable(False, False)
        
        tk.Label(
            popup,
            text="# Update Stock",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=20)
        
        # Product selection
        tk.Label(
            popup,
            text="Select Product",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor='w', padx=40, pady=(10, 5))
        
        product_var = tk.StringVar()
        product_names = [item["name"] for item in self.inventory]
        product_dropdown = ttk.Combobox(popup, textvariable=product_var, values=product_names, width=30)
        product_dropdown.pack(padx=40, pady=(0, 20))
        if product_names:
            product_dropdown.set(product_names[0])
        
        # Add to stock
        tk.Label(
            popup,
            text="Add to Stock",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
            
        ).pack(anchor='w', padx=40, pady=(10, 5))
        
        stock_entry = tk.Entry(popup, font=("Arial", 12), width=10)
        stock_entry.pack(anchor='w', padx=40, pady=(0, 20))
        stock_entry.insert(0, "0")
        
        # Update button
        tk.Button(
            popup,
            text="Update Stock",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            command=lambda: self.update_stock(product_var.get(), stock_entry.get(), popup)
        ).pack(pady=20)
    
    def show_add_product(self):
        """Show Add Product popup"""
        popup = tk.Toplevel(self.dashboard)
        popup.title("Add/Update Product")
        popup.geometry("400x500")
        popup.configure(bg='white')
        popup.resizable(False, False)
        
        tk.Label(
            popup,
            text="# Add/Update Product",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=20)
        
        # Product Name
        tk.Label(
            popup,
            text="Product Name",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor='w', padx=40, pady=(10, 5))
        
        name_entry = tk.Entry(popup, font=("Arial", 12), width=30)
        name_entry.pack(padx=40, pady=(0, 15))
        
        # Price
        tk.Label(
            popup,
            text="Price",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor='w', padx=40, pady=(10, 5))
        
        price_entry = tk.Entry(popup, font=("Arial", 12), width=15)
        price_entry.pack(anchor='w', padx=40, pady=(0, 15))
        price_entry.insert(0, "0.00")
        
        # Category
        tk.Label(
            popup,
            text="Category",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor='w', padx=40, pady=(10, 5))
        
        category_entry = tk.Entry(popup, font=("Arial", 12), width=20)
        category_entry.pack(anchor='w', padx=40, pady=(0, 15))
        
        # Stock
        tk.Label(
            popup,
            text="Stock",
            font=("Arial", 12),
            bg="white",
            fg="#34495e"
        ).pack(anchor='w', padx=40, pady=(10, 5))
        
        stock_entry = tk.Entry(popup, font=("Arial", 12), width=10)
        stock_entry.pack(anchor='w', padx=40, pady=(0, 20))
        stock_entry.insert(0, "0")
        
        # Add button
        tk.Button(
            popup,
            text="Add Product",
            bg="#2ecc71",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
            command=lambda: self.add_product(name_entry.get(), price_entry.get(), 
                                           category_entry.get(), stock_entry.get(), popup)
        ).pack(pady=20)
    
    # ===== Action Methods =====
    
    def load_data_from_db(self):
        """Load data from database"""
        # Load users
        self.users = self.db.get_all_users()
        
        # Load pending requests
        self.account_requests = self.db.get_pending_requests()
        
        # Load inventory
        self.inventory = self.db.get_inventory()
        
        # Load PC units
        self.pc_units = self.db.get_pc_units()
        
        # Initialize default PC units if none exist
        if not self.pc_units:
            self.initialize_default_pcs()
        
        # Load recent sessions (placeholder)
        self.recent_sessions = []
        
        # Load orders (placeholder)
        self.orders = []

    def initialize_default_pcs(self):
        """Initialize default PC units"""
        default_pcs = [
            {"name": "PC-01", "status": "Available"},
            {"name": "PC-02", "status": "Available"},
            {"name": "PC-03", "status": "Available"},
            {"name": "PC-04", "status": "Available"},
            {"name": "PC-05", "status": "Available"},
            {"name": "PC-06", "status": "Available"},
            {"name": "PC-07", "status": "Available"},
            {"name": "PC-08", "status": "Available"},
            {"name": "PC-09", "status": "Available"},
            {"name": "PC-10", "status": "Available"}
        ]
        for pc in default_pcs:
            try:
                self.db.cursor.execute('''
                    INSERT INTO pc_units (name, status) VALUES (%s, %s)
                ''', (pc["name"], pc["status"]))
                self.db.conn.commit()
            except:
                pass
        self.pc_units = self.db.get_pc_units()
    
    def add_user_minutes(self, user, minutes_entry):
        """Add minutes to user account"""
        try:
            minutes = int(minutes_entry.get())
            if self.db.add_user_minutes(user["id"], minutes):
                messagebox.showinfo("Success", 
                    f"Added {minutes} minutes to {user.get('username')}'s account!")
                minutes_entry.delete(0, tk.END)
                # Refresh data
                self.load_data_from_db()
                self.show_user_management(self.dashboard)
            else:
                messagebox.showerror("Error", "Failed to add minutes")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add minutes: {str(e)}")
    
    def approve_request(self, request):
        """Approve an account request"""
        try:
            if self.db.approve_account_request(request["id"]):
                messagebox.showinfo("Approved", 
                    f"Account request for {request.get('username')} has been approved!")
                # Refresh data from database
                self.load_data_from_db()
                self.show_account_requests(self.dashboard)
            else:
                messagebox.showerror("Error", "Failed to approve request")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve request: {str(e)}")

    def decline_request(self, request):
        """Decline an account request"""
        try:
            if self.db.decline_account_request(request["id"]):
                messagebox.showinfo("Declined", 
                    f"Account request for {request.get('username')} has been declined!")
            # Refresh data from database
                self.load_data_from_db()
                self.show_account_requests(self.dashboard)
            else:
                messagebox.showerror("Error", "Failed to decline request")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decline request: {str(e)}")
    def reset_password(self, user, password_entry):
        """Reset user password"""
        new_pass = password_entry.get()
        if new_pass:
            if self.db.update_user_password(user["id"], new_pass):
                messagebox.showinfo("Password Reset", 
                    f"Password for {user.get('username')} has been reset!")
                password_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to reset password")
        else:
            messagebox.showwarning("Error", "Please enter a new password")
    
    def update_stock(self, product_name, stock_change, popup):
        """Update product stock"""
        try:
            stock_change = int(stock_change)
            # Find product ID
            product_id = None
            for item in self.inventory:
                if item["name"] == product_name:
                    product_id = item["id"]
                    break
            
            if product_id and self.db.update_inventory_stock(product_id, stock_change):
                messagebox.showinfo("Success", f"Updated {product_name} stock by {stock_change}")
                # Refresh data
                self.load_data_from_db()
                popup.destroy()
                self.show_inventory(self.dashboard)
            else:
                messagebox.showerror("Error", "Product not found or update failed")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")
    
    def add_product(self, name, price, category, stock, popup):
        """Add new product"""
        try:
            if self.db.add_inventory_item(name, category, float(price), int(stock)):
                messagebox.showinfo("Success", f"Added product: {name}")
                # Refresh data
                self.load_data_from_db()
                popup.destroy()
                self.show_inventory(self.dashboard)
            else:
                messagebox.showerror("Error", "Failed to add product")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and stock values")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")
    
    def clear_content(self, parent):
        """Clear all widgets from content area"""
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.dashboard.winfo_children()[0]:
                widget.destroy()
    
    def on_dashboard_close(self, dashboard):
        """Handle dashboard close"""
        if hasattr(self, 'db'):
            self.db.close()
        dashboard.destroy()
        self.window.destroy()
        self.main_root.deiconify()
    
    def go_back(self):
        """Return to login selector"""
        if hasattr(self, 'db'):
            self.db.close()
        self.window.destroy()
        self.main_root.deiconify()