import tkinter as tk
from tkinter import ttk
from mysql.connector import Error

class HomeFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.bg_color)
        self.app = app
        
        # Main container with padding
        container = tk.Frame(self, bg=app.bg_color)
        container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Welcome section
        welcome_frame = tk.Frame(container, bg=app.secondary_bg, padx=40, pady=30,
                                relief='flat', bd=0)
        welcome_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(welcome_frame, text=f"Hello, {app.current_user['full_name']}! ☕",
                font=("Segoe UI", 28, "bold"), bg=app.secondary_bg, fg=app.dark_brown).pack(anchor='w')
        
        tk.Label(welcome_frame, text=f"Welcome back to Starbroke - {app.selected_pc}",
                font=("Segoe UI", 13), bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w', pady=(5, 0))
        
        # Dashboard cards
        cards_frame = tk.Frame(container, bg=app.bg_color)
        cards_frame.pack(fill='both', expand=True)
        
        # Account Balance Card
        balance_card = tk.Frame(cards_frame, bg=app.secondary_bg, padx=30, pady=30, relief='flat', bd=0)
        balance_card.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        
        balance_header = tk.Frame(balance_card, bg=app.secondary_bg)
        balance_header.pack(fill='x', anchor='w')
        
        tk.Label(balance_header, text="💰", font=("Segoe UI", 20),
                bg=app.secondary_bg).pack(side='left', padx=(0, 10))
        
        tk.Label(balance_header, text="Account Balance", font=("Segoe UI", 13),
                bg=app.secondary_bg, fg=app.text_secondary).pack(side='left')
        
        balance = app.current_user['account_balance']
        self.balance_label = tk.Label(balance_card, text=f"₱{balance:.2f}",
                                      font=("Segoe UI", 36, "bold"),
                                      bg=app.secondary_bg, fg=app.accent_color)
        self.balance_label.pack(anchor='w', pady=(15, 10))
        
        # Show hourly rate
        try:
            cursor = app.db_connection.cursor(dictionary=True)
            cursor.execute("SELECT hourly_rate FROM users WHERE user_id = %s", (app.current_user['user_id'],))
            rate_data = cursor.fetchone()
            cursor.close()
            hourly_rate = rate_data['hourly_rate'] if rate_data else 20.0
        except:
            hourly_rate = 20.0
        
        tk.Label(balance_card, text=f"Rate: ₱{hourly_rate:.2f}/hour", font=("Segoe UI", 11),
                bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w', pady=(5, 0))
        
        # Refresh balance button with sage green
        refresh_btn = tk.Button(balance_card, text="↻ Refresh Balance", font=("Segoe UI", 10),
                               bg=app.light_brown, fg=app.dark_brown, bd=0, cursor="hand2",
                               relief='flat',
                               activebackground=app.accent_color, activeforeground=app.secondary_bg,
                               command=self.refresh_balance, padx=15, pady=8)
        refresh_btn.pack(anchor='w', pady=(5, 0))
        
        # Session Info Card
        session_card = tk.Frame(cards_frame, bg=app.secondary_bg, padx=30, pady=30, relief='flat', bd=0)
        session_card.grid(row=0, column=1, sticky='nsew', padx=(12, 0))
        
        session_header = tk.Frame(session_card, bg=app.secondary_bg)
        session_header.pack(fill='x', anchor='w')
        
        tk.Label(session_header, text="⏱️", font=("Segoe UI", 20),
                bg=app.secondary_bg).pack(side='left', padx=(0, 10))
        
        tk.Label(session_header, text="Current Session", font=("Segoe UI", 13),
                bg=app.secondary_bg, fg=app.text_secondary).pack(side='left')
        
        # Get session info
        try:
            cursor = app.db_connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT pc.session_start, u.session_time_limit, u.hourly_rate
                FROM pc_units pc
                JOIN users u ON pc.current_user_id = u.user_id
                WHERE pc.unit_name = %s AND pc.current_user_id = %s
            """, (app.selected_pc, app.current_user['user_id']))
            session_data = cursor.fetchone()
            cursor.close()
            
            if session_data and session_data['session_start']:
                from datetime import datetime
                duration = datetime.now() - session_data['session_start']
                elapsed_minutes = int(duration.total_seconds() / 60)
                remaining_minutes = max(0, session_data['session_time_limit'] - elapsed_minutes)
                
                hours, minutes = divmod(elapsed_minutes, 60)
                rem_hours, rem_mins = divmod(remaining_minutes, 60)
                
                self.session_time_label = tk.Label(session_card, text=f"{hours:02d}:{minutes:02d}",
                                                  font=("Segoe UI", 36, "bold"),
                                                  bg=app.secondary_bg, fg=app.accent_color)
                self.session_time_label.pack(anchor='w', pady=(10, 0))
                
                time_color = "#FFA726" if remaining_minutes < 30 else app.text_secondary
                self.remaining_label = tk.Label(session_card, text=f"Left: {rem_hours:02d}:{rem_mins:02d}", 
                                               font=("Segoe UI", 11),
                                               bg=app.secondary_bg, fg=time_color)
                self.remaining_label.pack(anchor='w', pady=(5, 0))
            else:
                tk.Label(session_card, text="No Session", font=("Segoe UI", 36, "bold"),
                        bg=app.secondary_bg, fg=app.text_secondary).pack(anchor='w', pady=(10, 0))
        except Error:
            tk.Label(session_card, text="Error", font=("Segoe UI", 36, "bold"),
                    bg=app.secondary_bg, fg="#e74c3c").pack(anchor='w', pady=(10, 0))
        
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        
        # Recent Orders Card
        orders_card = tk.Frame(container, bg=app.secondary_bg, padx=40, pady=30, relief='flat', bd=0)
        orders_card.pack(fill='x', pady=(25, 0))
        
        orders_header = tk.Frame(orders_card, bg=app.secondary_bg)
        orders_header.pack(fill='x', anchor='w', pady=(0, 20))
        
        tk.Label(orders_header, text="📦", font=("Segoe UI", 20),
                bg=app.secondary_bg).pack(side='left', padx=(0, 10))
        
        tk.Label(orders_header, text="Recent Orders", font=("Segoe UI", 18, "bold"),
                bg=app.secondary_bg, fg=app.dark_brown).pack(side='left')
        
        try:
            cursor = app.db_connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM orders WHERE user_id = %s AND order_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)",
                (app.current_user['user_id'],)
            )
            order_count = cursor.fetchone()[0]
            cursor.close()
        except Error:
            order_count = 0
        
        tk.Label(orders_header, text=f"{order_count} orders this week", font=("Segoe UI", 12),
                bg=app.secondary_bg, fg=app.text_secondary).pack(side='right')
        
        # Cafe Promotions Section
        promo_frame = tk.Frame(container, bg=app.secondary_bg, padx=40, pady=35, relief='flat', bd=0)
        promo_frame.pack(fill='both', expand=True, pady=(25, 0))
        
        promo_header = tk.Frame(promo_frame, bg=app.secondary_bg)
        promo_header.pack(fill='x', pady=(0, 25))
        
        tk.Label(promo_header, text="Today's Special Offers ✨",
                font=("Segoe UI", 22, "bold"), bg=app.secondary_bg, fg=app.dark_brown).pack(side='left')
        
        # Promo cards
        promos = [
            {
                "emoji": "☕",
                "title": "Coffee Happy Hour",
                "description": "Get 20% off on all coffee drinks from 2PM to 4PM daily!",
                "tag": "20% OFF"
            },
            {
                "emoji": "🍔",
                "title": "Combo Meal Deal",
                "description": "Buy any burger and get free fries and drink of your choice!",
                "tag": "FREE SIDES"
            },
            {
                "emoji": "🎮",
                "title": "Gaming Special",
                "description": "4 hours gaming session + free pizza slice for only ₱200!",
                "tag": "₱200 ONLY"
            }
        ]
        
        promo_container = tk.Frame(promo_frame, bg=app.secondary_bg)
        promo_container.pack(fill='both', expand=True)
        
        for idx, promo in enumerate(promos):
            card = tk.Frame(promo_container, bg="#FAF5EF", padx=25, pady=25,
                          relief='flat', bd=0)
            card.grid(row=0, column=idx, sticky='nsew', padx=8)
            
            # Emoji icon
            tk.Label(card, text=promo['emoji'], font=("Segoe UI", 32),
                    bg="#FAF5EF").pack(anchor='w', pady=(0, 10))
            
            # Tag with sage green
            tag_label = tk.Label(card, text=promo['tag'], font=("Segoe UI", 11, "bold"),
                               bg=app.accent_color, fg=app.secondary_bg, padx=12, pady=6)
            tag_label.pack(anchor='w', pady=(0, 12))
            
            # Title
            tk.Label(card, text=promo['title'], font=("Segoe UI", 15, "bold"),
                    bg="#FAF5EF", fg=app.dark_brown).pack(anchor='w', pady=(0, 8))
            
            # Description
            tk.Label(card, text=promo['description'], font=("Segoe UI", 10),
                    bg="#FAF5EF", fg=app.text_secondary, wraplength=220, justify='left').pack(anchor='w')
            
            promo_container.columnconfigure(idx, weight=1)
        
        # Start auto-refresh for real-time updates
        self.start_auto_refresh()
    
    def refresh_balance(self):
        """Refresh account balance from database"""
        try:
            cursor = self.app.db_connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT account_balance FROM users WHERE user_id = %s",
                (self.app.current_user['user_id'],)
            )
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                self.app.current_user['account_balance'] = result['account_balance']
                self.balance_label.config(text=f"₱{result['account_balance']:.2f}")
                
        except Error as e:
            print(f"Error refreshing balance: {e}")
    
    def start_auto_refresh(self):
        """Start auto-refresh for real-time updates"""
        self.refresh_session_info()
        # Schedule next refresh in 30 seconds
        self.after(30000, self.start_auto_refresh)
    
    def refresh_session_info(self):
        """Refresh session information and balance"""
        try:
            # Refresh balance
            self.refresh_balance()
            
            # Refresh session info if labels exist
            if hasattr(self, 'session_time_label') and hasattr(self, 'remaining_label'):
                cursor = self.app.db_connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT pc.session_start, u.session_time_limit
                    FROM pc_units pc
                    JOIN users u ON pc.current_user_id = u.user_id
                    WHERE pc.unit_name = %s AND pc.current_user_id = %s
                """, (self.app.selected_pc, self.app.current_user['user_id']))
                session_data = cursor.fetchone()
                cursor.close()
                
                if session_data and session_data['session_start']:
                    from datetime import datetime
                    duration = datetime.now() - session_data['session_start']
                    elapsed_minutes = int(duration.total_seconds() / 60)
                    remaining_minutes = max(0, session_data['session_time_limit'] - elapsed_minutes)
                    
                    hours, minutes = divmod(elapsed_minutes, 60)
                    rem_hours, rem_mins = divmod(remaining_minutes, 60)
                    
                    self.session_time_label.config(text=f"{hours:02d}:{minutes:02d}")
                    
                    # Color coding for time warnings
                    if remaining_minutes <= 10:
                        time_color = "#e74c3c"  # Red
                    elif remaining_minutes < 30:
                        time_color = "#FFA726"  # Orange
                    else:
                        time_color = self.app.text_secondary
                    
                    self.remaining_label.config(text=f"Left: {rem_hours:02d}:{rem_mins:02d}", fg=time_color)
                    
        except Error as e:
            print(f"Error refreshing session info: {e}")


            