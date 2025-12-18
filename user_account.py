import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
import hashlib

class AccountsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.bg_color)
        self.app = app
        
        # Main container with padding
        container = tk.Frame(self, bg=app.bg_color)
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        tk.Label(container, text="Account Settings 👤", font=("Segoe UI", 28, "bold"),
                bg=app.bg_color, fg=app.dark_brown).pack(anchor='w', pady=(0, 25))
        
        # Content frame
        content = tk.Frame(container, bg=app.bg_color)
        content.pack(fill='both', expand=True)
        
        # Left column - Account Info
        left_column = tk.Frame(content, bg=app.bg_color)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Account Information Card
        info_card = tk.Frame(left_column, bg=app.secondary_bg, padx=35, pady=35, relief='flat', bd=0)
        info_card.pack(fill='both', expand=True)
        
        tk.Label(info_card, text="Account Information", font=("Segoe UI", 18, "bold"),
                bg=app.secondary_bg, fg=app.dark_brown).pack(anchor='w', pady=(0, 25))
        
        # User info fields with icons
        info_fields = [
            ("👤", "Username", app.current_user['username']),
            ("📝", "Full Name", app.current_user['full_name']),
            ("📱", "Phone Number", app.current_user['phone_number']),
            ("💰", "Account Balance", f"₱{app.current_user['account_balance']:.2f}"),
            ("⏱️", "Session Limit", f"{app.current_user.get('session_time_limit', 120)} minutes"),
            ("💵", "Hourly Rate", f"₱{app.current_user.get('hourly_rate', 20.00):.2f}/hour"),
            ("📅", "Member Since", app.current_user['created_at'].strftime("%B %d, %Y"))
        ]
        
        for icon, label, value in info_fields:
            field_frame = tk.Frame(info_card, bg=app.secondary_bg)
            field_frame.pack(fill='x', pady=(0, 20))
            
            # Icon and label container
            label_container = tk.Frame(field_frame, bg=app.secondary_bg)
            label_container.pack(fill='x', anchor='w')
            
            tk.Label(label_container, text=icon, font=("Segoe UI", 14),
                    bg=app.secondary_bg).pack(side='left', padx=(0, 8))
            
            tk.Label(label_container, text=label, font=("Segoe UI", 10),
                    bg=app.secondary_bg, fg=app.text_secondary).pack(side='left')
            
            # Value with background
            value_frame = tk.Frame(field_frame, bg="#FAF5EF", padx=15, pady=10,
                                  relief='flat', bd=0)
            value_frame.pack(fill='x', pady=(5, 0))
            
            tk.Label(value_frame, text=value, font=("Segoe UI", 12),
                    bg="#FAF5EF", fg=app.dark_brown).pack(anchor='w')
        
        # Right column - Actions
        right_column = tk.Frame(content, bg=app.bg_color)
        right_column.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Change Password Card
        password_card = tk.Frame(right_column, bg=app.secondary_bg, padx=35, pady=35, relief='flat', bd=0)
        password_card.pack(fill='x', pady=(0, 15))
        
        tk.Label(password_card, text="Change Password 🔒", font=("Segoe UI", 18, "bold"),
                bg=app.secondary_bg, fg=app.dark_brown).pack(anchor='w', pady=(0, 20))
        
        # Current password with toggle
        tk.Label(password_card, text="Current Password", font=("Segoe UI", 10),
                bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w', pady=(0, 5))
        
        current_pw_frame = tk.Frame(password_card, bg=app.secondary_bg)
        current_pw_frame.pack(fill='x', pady=(0, 15))
        
        current_pw_entry = tk.Entry(current_pw_frame, font=("Segoe UI", 11), show="●",
                                    bg="#FAF5EF", fg=app.text_color, 
                                    insertbackground=app.text_color, bd=0,
                                    relief='flat', highlightthickness=0)
        current_pw_entry.pack(side='left', fill='x', expand=True, ipady=10)
        
        def toggle_current_password():
            if current_pw_entry.cget('show') == '●':
                current_pw_entry.config(show='')
                current_show_btn.config(text='🙈')
            else:
                current_pw_entry.config(show='●')
                current_show_btn.config(text='👁')
        
        current_show_btn = tk.Button(current_pw_frame, text="👁", font=("Segoe UI", 10),
                                    bg="#FAF5EF", fg=app.text_color, bd=0, cursor="hand2",
                                    command=toggle_current_password, width=3)
        current_show_btn.pack(side='right', padx=(5, 0), ipady=10)
        
        # New password with toggle
        tk.Label(password_card, text="New Password", font=("Segoe UI", 10),
                bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w', pady=(0, 5))
        
        new_pw_frame = tk.Frame(password_card, bg=app.secondary_bg)
        new_pw_frame.pack(fill='x', pady=(0, 10))
        
        new_pw_entry = tk.Entry(new_pw_frame, font=("Segoe UI", 11), show="●",
                               bg="#FAF5EF", fg=app.text_color, 
                               insertbackground=app.text_color, bd=0,
                               relief='flat', highlightthickness=0)
        new_pw_entry.pack(side='left', fill='x', expand=True, ipady=10)
        
        def toggle_new_password():
            if new_pw_entry.cget('show') == '●':
                new_pw_entry.config(show='')
                new_show_btn.config(text='🙈')
            else:
                new_pw_entry.config(show='●')
                new_show_btn.config(text='👁')
        
        new_show_btn = tk.Button(new_pw_frame, text="👁", font=("Segoe UI", 10),
                                bg="#FAF5EF", fg=app.text_color, bd=0, cursor="hand2",
                                command=toggle_new_password, width=3)
        new_show_btn.pack(side='right', padx=(5, 0), ipady=10)
        
        # Password requirements
        req_frame = tk.Frame(password_card, bg=app.secondary_bg)
        req_frame.pack(fill='x', pady=(0, 10))
        
        requirements_text = ("Password Requirements: 8+ chars, 1-3 numbers, 1 special symbol (@#$%&*!)")
        req_label = tk.Label(req_frame, text=requirements_text, font=("Segoe UI", 9),
                           bg=app.secondary_bg, fg=app.accent_color, wraplength=400)
        req_label.pack(anchor='w')
        
        # Password strength indicator
        strength_frame = tk.Frame(password_card, bg=app.secondary_bg)
        strength_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(strength_frame, text="Password Strength:", font=("Segoe UI", 9, "bold"),
                bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w')
        
        strength_bar = tk.Frame(strength_frame, bg="#e0e0e0", height=6)
        strength_bar.pack(fill='x', pady=(5, 0))
        
        strength_fill = tk.Frame(strength_bar, bg="red", width=0, height=6)
        strength_fill.place(relx=0, rely=0, relwidth=0, height=6)
        
        strength_label = tk.Label(strength_frame, text="Weak", font=("Segoe UI", 9),
                                bg=app.secondary_bg, fg="red")
        strength_label.pack(anchor='w', pady=(3, 0))
        
        def check_password_strength(event=None):
            password = new_pw_entry.get()
            strength = 0
            width = 0
            
            # Check length
            if len(password) >= 8:
                strength += 25
                width += 0.25
            
            # Check for numbers
            num_count = sum(1 for c in password if c.isdigit())
            if 1 <= num_count <= 3:
                strength += 25
                width += 0.25
            
            # Check for special characters
            special_chars = set('@#$%&*!')
            if any(c in special_chars for c in password):
                strength += 25
                width += 0.25
            
            # Check for letters
            if any(c.isalpha() for c in password):
                strength += 25
                width += 0.25
            
            # Update strength bar
            strength_fill.place(relx=0, rely=0, relwidth=width, height=6)
            
            # Update color and label
            if strength >= 75:
                strength_fill.config(bg="green")
                strength_label.config(text="Strong", fg="green")
            elif strength >= 50:
                strength_fill.config(bg="orange")
                strength_label.config(text="Medium", fg="orange")
            else:
                strength_fill.config(bg="red")
                strength_label.config(text="Weak", fg="red")
        
        new_pw_entry.bind('<KeyRelease>', check_password_strength)
        
        # Confirm new password with toggle
        tk.Label(password_card, text="Confirm New Password", font=("Segoe UI", 10),
                bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w', pady=(0, 5))
        
        confirm_pw_frame = tk.Frame(password_card, bg=app.secondary_bg)
        confirm_pw_frame.pack(fill='x', pady=(0, 20))
        
        confirm_pw_entry = tk.Entry(confirm_pw_frame, font=("Segoe UI", 11), show="●",
                                    bg="#FAF5EF", fg=app.text_color, 
                                    insertbackground=app.text_color, bd=0,
                                    relief='flat', highlightthickness=0)
        confirm_pw_entry.pack(side='left', fill='x', expand=True, ipady=10)
        
        def toggle_confirm_password():
            if confirm_pw_entry.cget('show') == '●':
                confirm_pw_entry.config(show='')
                confirm_show_btn.config(text='🙈')
            else:
                confirm_pw_entry.config(show='●')
                confirm_show_btn.config(text='👁')
        
        confirm_show_btn = tk.Button(confirm_pw_frame, text="👁", font=("Segoe UI", 10),
                                    bg="#FAF5EF", fg=app.text_color, bd=0, cursor="hand2",
                                    command=toggle_confirm_password, width=3)
        confirm_show_btn.pack(side='right', padx=(5, 0), ipady=10)
        
        # Change password button with sage green
        change_pw_btn = tk.Button(password_card, text="Change Password",
                                 font=("Segoe UI", 11, "bold"),
                                 bg=app.primary_btn, fg=app.secondary_bg, bd=0,
                                 cursor="hand2", relief='flat',
                                 activebackground="#7A9977", activeforeground=app.secondary_bg,
                                 command=lambda: self.change_password(
                                     current_pw_entry.get(),
                                     new_pw_entry.get(),
                                     confirm_pw_entry.get(),
                                     current_pw_entry,
                                     new_pw_entry,
                                     confirm_pw_entry
                                 ))
        change_pw_btn.pack(fill='x', ipady=12)
        
        # Order History Card
        history_card = tk.Frame(right_column, bg=app.secondary_bg, padx=35, pady=35, relief='flat', bd=0)
        history_card.pack(fill='both', expand=True)
        
        tk.Label(history_card, text="Recent Orders 📦", font=("Segoe UI", 18, "bold"),
                bg=app.secondary_bg, fg=app.dark_brown).pack(anchor='w', pady=(0, 20))
        
        # Orders list with scrollbar
        orders_canvas = tk.Canvas(history_card, bg=app.secondary_bg, highlightthickness=0, height=300)
        orders_scrollbar = ttk.Scrollbar(history_card, orient="vertical", command=orders_canvas.yview)
        orders_frame = tk.Frame(orders_canvas, bg=app.secondary_bg)
        
        orders_frame.bind(
            "<Configure>",
            lambda e: orders_canvas.configure(scrollregion=orders_canvas.bbox("all"))
        )
        
        orders_canvas.create_window((0, 0), window=orders_frame, anchor="nw", width=420)
        orders_canvas.configure(yscrollcommand=orders_scrollbar.set)
        
        orders_canvas.pack(side="left", fill="both", expand=True)
        orders_scrollbar.pack(side="right", fill="y")
        
        # Load recent orders
        self.load_order_history(orders_frame)
    
    def change_password(self, current_pw, new_pw, confirm_pw, entry1, entry2, entry3):
        """Change user password with enhanced validation"""
        if not current_pw or not new_pw or not confirm_pw:
            messagebox.showerror("Error", "Please fill in all password fields")
            return
        
        if new_pw != confirm_pw:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        # Enhanced password validation
        if len(new_pw) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters long")
            return
        
        # Check for numbers (1-3 required)
        num_count = sum(1 for c in new_pw if c.isdigit())
        if not (1 <= num_count <= 3):
            messagebox.showerror("Error", "Password must contain 1-3 numbers")
            return
        
        # Check for special characters
        special_chars = set('@#$%&*!')
        if not any(c in special_chars for c in new_pw):
            messagebox.showerror("Error", "Password must contain at least one special symbol (@#$%&*!)")
            return
        
        # Check for letters
        if not any(c.isalpha() for c in new_pw):
            messagebox.showerror("Error", "Password must contain letters")
            return
        
        try:
            cursor = self.app.db_connection.cursor(dictionary=True)
            
            # Verify current password
            current_pw_hash = hashlib.sha256(current_pw.encode()).hexdigest()
            cursor.execute(
                "SELECT password FROM users WHERE user_id = %s",
                (self.app.current_user['user_id'],)
            )
            result = cursor.fetchone()
            
            if not result or result['password'] != current_pw_hash:
                messagebox.showerror("Error", "Current password is incorrect")
                cursor.close()
                return
            
            # Update password
            new_pw_hash = hashlib.sha256(new_pw.encode()).hexdigest()
            cursor.execute(
                "UPDATE users SET password = %s WHERE user_id = %s",
                (new_pw_hash, self.app.current_user['user_id'])
            )
            
            self.app.db_connection.commit()
            cursor.close()
            
            messagebox.showinfo("Success", "Password changed successfully!")
            
            # Clear entries
            entry1.delete(0, tk.END)
            entry2.delete(0, tk.END)
            entry3.delete(0, tk.END)
            
        except Error as e:
            messagebox.showerror("Database Error", f"Error changing password: {e}")
            self.app.db_connection.rollback()
    
    def load_order_history(self, parent_frame):
        """Load user's order history"""
        try:
            cursor = self.app.db_connection.cursor(dictionary=True)
            cursor.execute(
                """SELECT item_name, quantity, total_price, order_date, order_status
                   FROM orders
                   WHERE user_id = %s
                   ORDER BY order_date DESC
                   LIMIT 10""",
                (self.app.current_user['user_id'],)
            )
            
            orders = cursor.fetchall()
            cursor.close()
            
            if not orders:
                tk.Label(parent_frame, text="No orders yet\n\nStart ordering from the cafe!",
                        font=("Segoe UI", 11), bg=self.app.secondary_bg,
                        fg=self.app.text_secondary).pack(pady=40)
                return
            
            for order in orders:
                order_frame = tk.Frame(parent_frame, bg="#FAF5EF", padx=15, pady=15,
                                      relief='flat', bd=0)
                order_frame.pack(fill='x', pady=(0, 10))
                
                # Order header
                header = tk.Frame(order_frame, bg="#FAF5EF")
                header.pack(fill='x', pady=(0, 8))
                
                # Order item name
                tk.Label(header, text=order['item_name'], font=("Segoe UI", 12, "bold"),
                        bg="#FAF5EF", fg=self.app.dark_brown).pack(side='left')
                
                # Status with color coding
                status_colors = {
                    'Pending': '#FFA726',
                    'Approved': self.app.accent_color,
                    'Rejected': '#e74c3c',
                    'Completed': '#4CAF50'
                }
                status_color = status_colors.get(order['order_status'], self.app.primary_btn)
                
                status_label = tk.Label(header, text=order['order_status'].upper(),
                                       font=("Segoe UI", 8, "bold"),
                                       bg=status_color, fg=self.app.secondary_bg,
                                       padx=8, pady=3)
                status_label.pack(side='right')
                
                # Order details
                details = f"Qty: {order['quantity']} × ₱{order['total_price']/order['quantity']:.2f}"
                tk.Label(order_frame, text=details, font=("Segoe UI", 10),
                        bg="#FAF5EF", fg=self.app.text_secondary).pack(anchor='w')
                
                # Bottom row: date and price
                bottom = tk.Frame(order_frame, bg="#FAF5EF")
                bottom.pack(fill='x', pady=(8, 0))
                
                date_str = order['order_date'].strftime("%b %d, %Y")
                tk.Label(bottom, text=date_str, font=("Segoe UI", 9),
                        bg="#FAF5EF", fg=self.app.text_secondary).pack(side='left')
                
                tk.Label(bottom, text=f"₱{order['total_price']:.2f}",
                        font=("Segoe UI", 12, "bold"),
                        bg="#FAF5EF", fg=self.app.primary_btn).pack(side='right')
                
        except Error as e:
            tk.Label(parent_frame, text="Error loading orders", font=("Segoe UI", 11),
                    bg=self.app.secondary_bg, fg="#ff5252").pack(pady=40)
            print(f"Error loading order history: {e}")