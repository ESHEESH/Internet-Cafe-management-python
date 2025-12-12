import tkinter as tk
from tkinter import messagebox
import hashlib
from database import Database

class UserLogin:
    def __init__(self, window, main_root):
        self.window = window
        self.main_root = main_root
        self.db = Database()
        
        self.window.title("User Login")
        
        # Make fullscreen
        self.window.attributes('-fullscreen', True)
        self.window.configure(bg='white')
        
        if not self.db.connect():
            messagebox.showerror("Database Error", "Could not connect to database")
            self.window.destroy()
            return
        
        # Setup UI to match your image
        self.setup_ui()
    
    def setup_ui(self):
        # Main container with centered content
        main_frame = tk.Frame(self.window, bg='white')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title - EXACTLY like your image
        title_label = tk.Label(
            main_frame,
            text="# User Login",
            font=("Arial", 36, "bold"),
            bg="white",
            fg="black"
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle - SIMPLIFIED (no "Request Account")
        subtitle_label = tk.Label(
            main_frame,
            text="Login",
            font=("Arial", 18),
            bg="white",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Username field - SIMPLE like your image
        username_frame = tk.Frame(main_frame, bg='white')
        username_frame.pack(pady=(0, 30))
        
        username_label = tk.Label(
            username_frame,
            text="Username",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="black"
        )
        username_label.pack(anchor='w')
        
        self.username_entry = tk.Entry(
            username_frame,
            font=("Arial", 18),
            width=30,
            bd=2,
            relief="solid"
        )
        self.username_entry.pack(pady=(10, 0))
        
        # Password field - SIMPLE like your image
        password_frame = tk.Frame(main_frame, bg='white')
        password_frame.pack(pady=(0, 40))
        
        password_label = tk.Label(
            password_frame,
            text="Password",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="black"
        )
        password_label.pack(anchor='w')
        
        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 18),
            width=30,
            bd=2,
            relief="solid",
            show="•"
        )
        self.password_entry.pack(pady=(10, 0))
        
        # Buttons Frame
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=(0, 20))
        
        # Login Button - CENTERED like your image
        login_button = tk.Button(
            buttons_frame,
            text="Login",
            font=("Arial", 20, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            command=self.login
        )
        login_button.pack()
        
        # Note for users
        note_frame = tk.Frame(main_frame, bg='white')
        note_frame.pack(pady=(20, 0))
        
        tk.Label(
            note_frame,
            text="Note: Accounts must be created by an administrator",
            font=("Arial", 12, "italic"),
            bg="white",
            fg="#666666"
        ).pack()
        
        # Back button (to return to selector)
        back_frame = tk.Frame(self.window, bg='white')
        back_frame.pack(side='bottom', pady=20)
        
        back_button = tk.Button(
            back_frame,
            text="← Back to Login Selector",
            font=("Arial", 14),
            bg="#cccccc",
            fg="black",
            command=self.go_back
        )
        back_button.pack()
        
        # Exit fullscreen button
        exit_fullscreen_button = tk.Button(
            back_frame,
            text="Exit Fullscreen (Esc)",
            font=("Arial", 12),
            bg="#999999",
            fg="white",
            command=lambda: self.window.attributes('-fullscreen', False)
        )
        exit_fullscreen_button.pack(pady=(10, 0))
        
        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.login())
        # Bind Escape to exit fullscreen
        self.window.bind('<Escape>', lambda e: self.window.attributes('-fullscreen', False))
        
        # Focus on username field
        self.username_entry.focus_set()
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Missing Information", 
                                 "Please enter both username and password")
            return
        
        # Check against database
        user = self.db.get_user_by_username(username)
        
        if user and user['is_approved']:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if password_hash == user['password_hash']:
                messagebox.showinfo("Login Successful", 
                                  f"Welcome back, {user['full_name']}!")
                
                # Clear fields
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                
                # Open user dashboard
                self.open_user_dashboard(user)
            else:
                messagebox.showerror("Login Failed", "Invalid password")
        else:
            messagebox.showerror("Login Failed", 
                               "Account not found or not approved by admin")
    
    def open_user_dashboard(self, user):
        """Open user dashboard in fullscreen"""
        dashboard = tk.Toplevel(self.window)
        dashboard.attributes('-fullscreen', True)
        dashboard.configure(bg='white')
        dashboard.title(f"User Dashboard - {user['username']}")
        
        # Welcome message
        welcome_frame = tk.Frame(dashboard, bg='white')
        welcome_frame.place(relx=0.5, rely=0.4, anchor='center')
        
        tk.Label(
            welcome_frame,
            text=f"Welcome, {user['full_name']}!",
            font=("Arial", 36, "bold"),
            bg="white",
            fg="#333333"
        ).pack(pady=(0, 20))
        
        tk.Label(
            welcome_frame,
            text="User Dashboard",
            font=("Arial", 24),
            bg="white",
            fg="#666666"
        ).pack(pady=(0, 50))
        
        # User info
        info_frame = tk.Frame(dashboard, bg='white')
        info_frame.place(relx=0.5, rely=0.6, anchor='center')
        
        user_info = [
            f"• Username: {user['username']}",
            f"• Phone: {user['phone']}",
            f"• Points: {user.get('points', 0)}",
            f"• Minutes Remaining: {user.get('remaining_minutes', 0)}",
            f"• Streak: {user.get('streak', 0)} days"
        ]
        
        for info in user_info:
            tk.Label(
                info_frame,
                text=info,
                font=("Arial", 18),
                bg="white",
                fg="#444444",
                anchor='w'
            ).pack(pady=5)
        
        # Logout button
        logout_frame = tk.Frame(dashboard, bg='white')
        logout_frame.pack(side='bottom', pady=30)
        
        tk.Button(
            logout_frame,
            text="Logout",
            font=("Arial", 16),
            bg="#ff4444",
            fg="white",
            width=15,
            command=lambda: [dashboard.destroy(), self.go_back()]
        ).pack()
        
        tk.Button(
            logout_frame,
            text="Close Dashboard",
            font=("Arial", 14),
            bg="#999999",
            fg="white",
            command=dashboard.destroy
        ).pack(pady=(10, 0))
        
        # Bind Escape to exit fullscreen
        dashboard.bind('<Escape>', lambda e: dashboard.attributes('-fullscreen', False))
    
    def go_back(self):
        """Return to login selector"""
        self.db.close()
        self.window.destroy()
        self.main_root.deiconify()  # Show the selector window again