class UserRegistration:
    def __init__(self, window, main_root):
        self.window = window
        self.main_root = main_root
        self.db = Database()
        
        if not self.db.connect():
            messagebox.showerror("Database Error", "Could not connect to database")
            self.window.destroy()
            return
        
        self.setup_ui()
    
    def setup_ui(self):
        # ... (your UI setup code)
    
    def submit_request(self):
        """Submit account request to database"""
        # Get form data
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        birthday = self.birthday_entry.get().strip()
        
        # Validate
        if not all([username, password, full_name, phone, birthday]):
            messagebox.showwarning("Missing Information", "Please fill all fields")
            return
        
        # Submit to database
        if self.db.create_account_request(username, password, full_name, phone, birthday):
            messagebox.showinfo("Success", "Account request submitted for admin approval!")
            self.go_back()
        else:
            messagebox.showerror("Error", "Username might already exist or request failed")