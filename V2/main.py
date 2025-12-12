import tkinter as tk
from user_login import UserLogin  
from admin_login import AdminLogin

class LoginSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Login System")
        
        # Make window fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#f0f0f0')
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Login System",
            font=("Arial", 36, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title_label.pack(pady=(0, 100))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Select Login Type",
            font=("Arial", 20),
            bg="#f0f0f0",
            fg="#666666"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack()
        
        # User Login Button
        user_button = tk.Button(
            button_frame,
            text="USER LOGIN",
            font=("Arial", 24, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=3,
            command=self.open_user_login
        )
        user_button.pack(pady=20)
        
        # Admin Login Button
        admin_button = tk.Button(
            button_frame,
            text="ADMIN LOGIN",
            font=("Arial", 24, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=3,
            command=self.open_admin_login
        )
        admin_button.pack(pady=20)
        
        # Exit button
        exit_button = tk.Button(
            main_frame,
            text="Exit",
            font=("Arial", 14),
            bg="#ff4444",
            fg="white",
            command=self.root.quit,
            width=10
        )
        exit_button.pack(pady=50)
        
        # Bind Escape key to exit fullscreen
        self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', 
                                                              not self.root.attributes('-fullscreen')))
    
    def open_user_login(self):
        """Open user login in fullscreen"""
        self.root.withdraw()  # Hide selector window
        user_window = tk.Toplevel(self.root)
        UserLogin(user_window, self.root)
    
    def open_admin_login(self):
        """Open admin login in normal window"""
        # DON'T hide the main window - just create admin window
        admin_window = tk.Toplevel(self.root)
        AdminLogin(admin_window, self.root)

def main():
    root = tk.Tk()
    app = LoginSelector(root)
    root.mainloop()

if __name__ == "__main__":
    main()