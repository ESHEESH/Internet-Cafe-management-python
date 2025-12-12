import tkinter as tk

class UserDashboard:
    def __init__(self, parent, username):
        self.parent = parent
        self.username = username
        
        self.dashboard = tk.Toplevel(parent)
        self.dashboard.title(f"User Dashboard - {username}")
        self.dashboard.geometry("500x400")
        self.dashboard.configure(bg="#f0f0f0")
        
        self.setup_ui()
    
    def setup_ui(self):
        tk.Label(
            self.dashboard, 
            text=f"Welcome, {self.username}!", 
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        ).pack(pady=40)
        
        tk.Label(
            self.dashboard, 
            text="This is your user dashboard.", 
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#666666"
        ).pack(pady=10)
        
        tk.Label(
            self.dashboard, 
            text="Regular users can view their profile,\ncheck notifications, and access basic features.", 
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666666"
        ).pack(pady=20)
        
        # Features frame
        features_frame = tk.Frame(self.dashboard, bg="#e0e0e0", relief="solid", bd=1)
        features_frame.pack(padx=30, pady=20, fill="both", expand=True)
        
        tk.Label(
            features_frame, 
            text="Available Features", 
            font=("Arial", 14, "bold"),
            bg="#e0e0e0",
            fg="#333333"
        ).pack(pady=15)
        
        # List of user functions
        user_functions = [
            "View Profile",
            "Update Personal Information",
            "Check Notifications",
            "View Activity History",
            "Change Password",
            "Logout from all devices"
        ]
        
        for i, func in enumerate(user_functions):
            tk.Label(
                features_frame, 
                text=f"• {func}", 
                font=("Arial", 11),
                bg="#e0e0e0",
                fg="#444444",
                anchor="w"
            ).pack(fill="x", padx=20, pady=3)
        
        # Close button
        tk.Button(
            self.dashboard,
            text="Close Dashboard",
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=20,
            pady=10,
            command=self.dashboard.destroy
        ).pack(pady=30)