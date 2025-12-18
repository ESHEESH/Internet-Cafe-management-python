import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
import os
from PIL import Image, ImageTk

class CafeFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.bg_color)
        self.app = app
        self.cart = []
        self.selected_category = "Coffee"
        
        # Main container
        main_container = tk.Frame(self, bg=app.bg_color)
        main_container.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        header_frame = tk.Frame(main_container, bg=app.bg_color)
        header_frame.pack(fill='x', pady=(0, 25))
        
        tk.Label(header_frame, text="Cafe Menu ☕", font=("Segoe UI", 28, "bold"),
                bg=app.bg_color, fg=app.dark_brown).pack(side='left')
        
        # View Orders button
        tk.Button(header_frame, text="📋 My Orders", font=("Segoe UI", 11),
                 bg=app.accent_color, fg=app.secondary_bg, bd=0, cursor="hand2",
                 padx=20, pady=10, command=self.view_my_orders).pack(side='right')
        
        # Content split: Menu on left, Cart on right
        content_frame = tk.Frame(main_container, bg=app.bg_color)
        content_frame.pack(fill='both', expand=True)
        
        # Menu Section (Left)
        menu_frame = tk.Frame(content_frame, bg=app.bg_color)
        menu_frame.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        # Category tabs
        categories = ["Coffee", "Food", "Drinks", "Snack", "Dessert"]
        
        tab_frame = tk.Frame(menu_frame, bg=app.bg_color)
        tab_frame.pack(fill='x', pady=(0, 20))
        
        self.category_buttons = {}
        for category in categories:
            btn = tk.Button(tab_frame, text=category, font=("Segoe UI", 11),
                          bg=app.primary_btn if category == "Coffee" else app.secondary_bg,
                          fg=app.secondary_bg if category == "Coffee" else app.text_color,
                          bd=0, cursor="hand2", padx=20, pady=10, relief='flat',
                          activebackground="#7A9977", activeforeground=app.secondary_bg,
                          command=lambda c=category: self.filter_category(c))
            btn.pack(side='left', padx=(0, 8))
            self.category_buttons[category] = btn
        
        # Menu items scrollable frame
        menu_canvas = tk.Canvas(menu_frame, bg=app.bg_color, highlightthickness=0)
        menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=menu_canvas.yview)
        self.menu_items_frame = tk.Frame(menu_canvas, bg=app.bg_color)
        
        self.menu_items_frame.bind(
            "<Configure>",
            lambda e: menu_canvas.configure(scrollregion=menu_canvas.bbox("all"))
        )
        
        menu_canvas.create_window((0, 0), window=self.menu_items_frame, anchor="nw")
        menu_canvas.configure(yscrollcommand=menu_scrollbar.set)
        
        menu_canvas.pack(side="left", fill="both", expand=True)
        menu_scrollbar.pack(side="right", fill="y")
        
        # Cart Section (Right) - FIXED HEIGHT
        cart_container = tk.Frame(content_frame, bg=app.secondary_bg, width=380,
                                 relief='flat', bd=0)
        cart_container.pack(side='right', fill='y')
        cart_container.pack_propagate(False)
        
        # Cart header
        cart_header = tk.Frame(cart_container, bg=app.secondary_bg, padx=25, pady=20)
        cart_header.pack(fill='x')
        
        tk.Label(cart_header, text="Cart 🛒", font=("Segoe UI", 20, "bold"),
                bg=app.secondary_bg, fg=app.dark_brown).pack(anchor='w')
        
        # Order type options (Delivery/Pickup)
        options_frame = tk.Frame(cart_header, bg=app.secondary_bg)
        options_frame.pack(fill='x', pady=(15, 0))
        
        self.order_type = tk.StringVar(value="Deliver to PC")
        
        self.option_buttons = {}
        for option in ["Deliver to PC", "Counter Pickup"]:
            btn = tk.Button(options_frame, text=option, font=("Segoe UI", 9),
                          bg=app.primary_btn if option == "Deliver to PC" else "#F5EFE7",
                          fg=app.secondary_bg if option == "Deliver to PC" else app.dark_brown,
                          bd=0, cursor="hand2", padx=15, pady=6, relief='flat',
                          command=lambda o=option: self.set_order_type(o))
            btn.pack(side='left', padx=(0, 8))
            self.option_buttons[option] = btn
        
        # Cart items frame - REDUCED HEIGHT to show button
        cart_items_container = tk.Frame(cart_container, bg=app.secondary_bg, height=200)
        cart_items_container.pack(fill='x', padx=0, pady=0)
        cart_items_container.pack_propagate(False)
        
        cart_canvas = tk.Canvas(cart_items_container, bg=app.secondary_bg, highlightthickness=0)
        cart_scrollbar = ttk.Scrollbar(cart_items_container, orient="vertical", command=cart_canvas.yview)
        self.cart_items_frame = tk.Frame(cart_canvas, bg=app.secondary_bg)
        
        self.cart_items_frame.bind(
            "<Configure>",
            lambda e: cart_canvas.configure(scrollregion=cart_canvas.bbox("all"))
        )
        
        cart_canvas.create_window((0, 0), window=self.cart_items_frame, anchor="nw", width=350)
        cart_canvas.configure(yscrollcommand=cart_scrollbar.set)
        
        cart_canvas.pack(side="left", fill="both", expand=True, padx=(25, 0))
        cart_scrollbar.pack(side="right", fill="y", padx=(0, 5))
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            cart_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        cart_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.cart_items_frame.bind("<MouseWheel>", _on_mousewheel)
        
        def _bind_mousewheel(event):
            cart_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            cart_canvas.unbind_all("<MouseWheel>")
        
        cart_canvas.bind('<Enter>', _bind_mousewheel)
        cart_canvas.bind('<Leave>', _unbind_mousewheel)
        
        # ===== CART FOOTER - ALWAYS VISIBLE AT BOTTOM =====
        cart_footer = tk.Frame(cart_container, bg=app.secondary_bg, padx=25, pady=15)
        cart_footer.pack(fill='x', side='bottom')
        
        # Separator line
        tk.Frame(cart_footer, bg=app.light_brown, height=2).pack(fill='x', pady=(0, 10))
        
        # Subtotal
        totals_frame = tk.Frame(cart_footer, bg=app.secondary_bg)
        totals_frame.pack(fill='x', pady=(0, 8))
        
        tk.Label(totals_frame, text="Subtotal", font=("Segoe UI", 11),
                bg=app.secondary_bg, fg=app.text_secondary).pack(side='left')
        self.items_label = tk.Label(totals_frame, text="₱0.00", font=("Segoe UI", 11, "bold"),
                                    bg=app.secondary_bg, fg=app.text_color)
        self.items_label.pack(side='right')
        
        # Total
        total_frame = tk.Frame(cart_footer, bg=app.secondary_bg)
        total_frame.pack(fill='x', pady=(0, 12))
        
        tk.Label(total_frame, text="Total", font=("Segoe UI", 13, "bold"),
                bg=app.secondary_bg, fg=app.text_color).pack(side='left')
        
        self.total_label = tk.Label(total_frame, text="₱0.00", font=("Segoe UI", 16, "bold"),
                                    bg=app.secondary_bg, fg=app.dark_brown)
        self.total_label.pack(side='right')
        
        # ===== CONFIRM ORDER BUTTON - BIG AND VISIBLE =====
        self.confirm_order_btn = tk.Button(
            cart_footer, 
            text="✓ CONFIRM ORDER", 
            font=("Segoe UI", 13, "bold"),
            bg="#CCCCCC",  # Gray when disabled
            fg=app.secondary_bg, 
            bd=0, 
            cursor="arrow",
            relief='flat',
            state='disabled',
            command=self.confirm_order
        )
        self.confirm_order_btn.pack(fill='x', ipady=15, pady=(0, 8))
        
        # Clear cart button
        clear_btn = tk.Button(cart_footer, text="🗑️ Clear Cart", font=("Segoe UI", 9),
                            bg=app.secondary_bg, fg=app.text_secondary, bd=0, cursor="hand2",
                            command=self.clear_cart)
        clear_btn.pack()
        
        # Load menu items
        self.load_menu_items()
        self.update_cart_display()
        
        print("✓ CafeFrame initialized - Confirm button created")
    
    def set_order_type(self, order_type):
        """Set order type and update button styles"""
        self.order_type.set(order_type)
        
        for option, btn in self.option_buttons.items():
            if option == order_type:
                btn.config(bg=self.app.primary_btn, fg=self.app.secondary_bg)
            else:
                btn.config(bg="#F5EFE7", fg=self.app.dark_brown)
    
    def load_menu_items(self, category="Coffee"):
        """Load menu items from database with images"""
        for widget in self.menu_items_frame.winfo_children():
            widget.destroy()
        
        try:
            cursor = self.app.db_connection.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM cafe_items WHERE category = %s AND available = TRUE ORDER BY item_name",
                (category,)
            )
            items = cursor.fetchall()
            cursor.close()
            
            if not items:
                tk.Label(self.menu_items_frame, 
                        text=f"No {category.lower()} items available",
                        font=("Segoe UI", 12), bg=self.app.bg_color,
                        fg=self.app.text_secondary).pack(pady=50)
                return
            
            for idx, item in enumerate(items):
                self.create_menu_item_card(item, idx)
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading menu: {e}")
    
    def create_menu_item_card(self, item, index):
        """Create a menu item card with image"""
        card = tk.Frame(self.menu_items_frame, bg=self.app.secondary_bg, padx=20, pady=20,
                       relief='flat', bd=0)
        card.grid(row=index//2, column=index%2, padx=10, pady=10, sticky='nsew')
        
        # Image at the top
        image_frame = tk.Frame(card, bg=self.app.secondary_bg)
        image_frame.pack(fill='x', pady=(0, 10))
        
        if item.get('image_path') and os.path.exists(item['image_path']):
            try:
                img = Image.open(item['image_path'])
                img = img.resize((200, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(image_frame, image=photo, bg=self.app.secondary_bg)
                img_label.image = photo
                img_label.pack()
            except Exception:
                tk.Label(image_frame, text="🍽️", font=("Segoe UI", 60),
                        bg=self.app.secondary_bg, fg=self.app.text_secondary).pack()
        else:
            tk.Label(image_frame, text="🍽️", font=("Segoe UI", 60),
                    bg=self.app.secondary_bg, fg=self.app.text_secondary).pack()
        
        # Item info
        tk.Label(card, text=item['item_name'], font=("Segoe UI", 14, "bold"),
                bg=self.app.secondary_bg, fg=self.app.dark_brown).pack(anchor='w')
        
        tk.Label(card, text=item['category'], font=("Segoe UI", 9),
                bg=self.app.secondary_bg, fg=self.app.text_secondary).pack(anchor='w', pady=(3, 15))
        
        # Bottom row: price and add button
        bottom_frame = tk.Frame(card, bg=self.app.secondary_bg)
        bottom_frame.pack(fill='x')
        
        tk.Label(bottom_frame, text=f"₱{item['price']:.2f}", font=("Segoe UI", 16, "bold"),
                bg=self.app.secondary_bg, fg=self.app.dark_brown).pack(side='left')
        
        # Add to cart button
        add_btn = tk.Button(bottom_frame, text="+ Add to Cart", font=("Segoe UI", 10, "bold"),
                          bg=self.app.primary_btn, fg=self.app.secondary_bg, bd=0,
                          cursor="hand2", padx=15, pady=8, relief='flat',
                          activebackground="#7A9977", activeforeground=self.app.secondary_bg,
                          command=lambda i=item: self.add_to_cart(i))
        add_btn.pack(side='right')
        
        self.menu_items_frame.columnconfigure(0, weight=1)
        self.menu_items_frame.columnconfigure(1, weight=1)
    
    def filter_category(self, category):
        """Filter menu items by category"""
        self.selected_category = category
        self.load_menu_items(category)
        
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.config(bg=self.app.primary_btn, fg=self.app.secondary_bg)
            else:
                btn.config(bg=self.app.secondary_bg, fg=self.app.text_color)
    
    def add_to_cart(self, item):
        """Add item to cart"""
        for cart_item in self.cart:
            if cart_item['item_id'] == item['item_id']:
                cart_item['quantity'] += 1
                self.update_cart_display()
                print(f"✓ Added {item['item_name']} to cart (quantity: {cart_item['quantity']})")
                return
        
        self.cart.append({
            'item_id': item['item_id'],
            'item_name': item['item_name'],
            'price': float(item['price']),
            'quantity': 1
        })
        
        print(f"✓ Added {item['item_name']} to cart (new item)")
        self.update_cart_display()
    
    def update_cart_display(self):
        """Update cart display"""
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        if not self.cart:
            tk.Label(self.cart_items_frame, text="Cart is empty\n\nAdd items from the menu",
                    font=("Segoe UI", 11), bg=self.app.secondary_bg,
                    fg=self.app.text_secondary).pack(pady=60)
            self.total_label.config(text="₱0.00")
            self.items_label.config(text="₱0.00")
            # Disable button when cart is empty
            self.confirm_order_btn.config(state='disabled', bg="#CCCCCC", cursor="arrow")
            print("Cart is empty - button disabled")
            return
        
        total = 0
        for item in self.cart:
            item_frame = tk.Frame(self.cart_items_frame, bg="#FAF5EF", padx=15, pady=15,
                                 relief='flat', bd=0)
            item_frame.pack(fill='x', pady=(0, 10))
            
            # Item name and remove button
            header = tk.Frame(item_frame, bg="#FAF5EF")
            header.pack(fill='x', pady=(0, 10))
            
            tk.Label(header, text=item['item_name'], font=("Segoe UI", 11, "bold"),
                    bg="#FAF5EF", fg=self.app.dark_brown).pack(side='left')
            
            tk.Button(header, text="✕", font=("Segoe UI", 10),
                     bg="#FAF5EF", fg="#e74c3c", bd=0,
                     cursor="hand2", command=lambda i=item: self.remove_from_cart(i)).pack(side='right')
            
            # Quantity controls and price
            controls = tk.Frame(item_frame, bg="#FAF5EF")
            controls.pack(fill='x')
            
            tk.Button(controls, text="−", font=("Segoe UI", 9),
                     bg=self.app.secondary_bg, fg=self.app.text_color, bd=0,
                     cursor="hand2", width=2, relief='flat',
                     command=lambda i=item: self.decrease_quantity(i)).pack(side='left')
            
            tk.Label(controls, text=str(item['quantity']), font=("Segoe UI", 10),
                    bg="#FAF5EF", fg=self.app.text_color, width=3).pack(side='left', padx=5)
            
            tk.Button(controls, text="+", font=("Segoe UI", 9),
                     bg=self.app.secondary_bg, fg=self.app.text_color, bd=0,
                     cursor="hand2", width=2, relief='flat',
                     command=lambda i=item: self.increase_quantity(i)).pack(side='left')
            
            item_total = item['price'] * item['quantity']
            tk.Label(controls, text=f"₱{item_total:.2f}", font=("Segoe UI", 11, "bold"),
                    bg="#FAF5EF", fg=self.app.primary_btn).pack(side='right')
            
            total += item_total
        
        self.items_label.config(text=f"₱{total:.2f}")
        self.total_label.config(text=f"₱{total:.2f}")
        # Enable button when cart has items
        self.confirm_order_btn.config(state='normal', bg=self.app.primary_btn, cursor="hand2")
        print(f"Cart updated - {len(self.cart)} items, Total: ₱{total:.2f} - Button ENABLED")
        
        self.cart_items_frame.update_idletasks()
        canvas = self.cart_items_frame.master
        if hasattr(canvas, 'configure'):
            canvas.configure(scrollregion=canvas.bbox("all"))
    
    def increase_quantity(self, item):
        """Increase item quantity"""
        item['quantity'] += 1
        self.update_cart_display()
    
    def decrease_quantity(self, item):
        """Decrease item quantity"""
        if item['quantity'] > 1:
            item['quantity'] -= 1
        else:
            self.cart.remove(item)
        self.update_cart_display()
    
    def remove_from_cart(self, item):
        """Remove item from cart"""
        self.cart.remove(item)
        self.update_cart_display()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart:
            if messagebox.askyesno("Clear Cart", "Are you sure you want to clear the cart?"):
                self.cart = []
                self.update_cart_display()
    
    def confirm_order(self):
        """Confirm and send order to admin for approval"""
        print("\n" + "="*50)
        print("CONFIRM ORDER BUTTON CLICKED!")
        print("="*50)
        
        if not self.cart:
            print("✗ Cart is empty")
            messagebox.showwarning("Empty Cart", "Please add items to your cart first.")
            return
        
        print(f"✓ Cart has {len(self.cart)} items")
        
        # Check database connection
        try:
            if not self.app.db_connection.is_connected():
                print("✗ Database not connected - reconnecting...")
                self.app.setup_database()
        except:
            print("✗ Database connection error")
            messagebox.showerror("Connection Error", "Database connection lost. Please restart the application.")
            return
        
        total = sum(item['price'] * item['quantity'] for item in self.cart)
        order_type_msg = self.order_type.get()
        
        print(f"Order Type: {order_type_msg}")
        print(f"Total: ₱{total:.2f}")
        print(f"User ID: {self.app.current_user['user_id']}")
        
        # Create detailed order summary
        items_summary = "\n".join([f"  • {item['item_name']} x{item['quantity']} - ₱{item['price'] * item['quantity']:.2f}" 
                                   for item in self.cart])
        
        # Confirmation dialog
        confirm_msg = f"📋 Order Summary\n\n"
        confirm_msg += f"Order Type: {order_type_msg}\n"
        confirm_msg += f"Total Items: {len(self.cart)}\n\n"
        confirm_msg += f"Items:\n{items_summary}\n\n"
        confirm_msg += f"Total: ₱{total:.2f}\n\n"
        confirm_msg += "Send order to admin for approval?"
        
        if not messagebox.askyesno("Confirm Order", confirm_msg):
            print("User cancelled order")
            return
        
        print("\nSaving orders to database...")
        
        try:
            cursor = self.app.db_connection.cursor()
            order_count = 0
            
            # Insert each cart item as a separate order
            for item in self.cart:
                item_total = item['price'] * item['quantity']
                
                print(f"  Inserting: {item['item_name']} x{item['quantity']} = ₱{item_total:.2f}")
                
                cursor.execute(
                    """
                    INSERT INTO orders (
                        user_id,
                        item_name,
                        quantity,
                        price,
                        total_price,
                        order_status,
                        order_type
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.app.current_user['user_id'],
                        item['item_name'],
                        item['quantity'],
                        item['price'],
                        item_total,
                        "Pending",
                        order_type_msg
                    )

                )
                order_count += 1
            
            self.app.db_connection.commit()
            cursor.close()
            
            print(f"\n✓✓✓ SUCCESS! {order_count} orders saved to database ✓✓✓")
            print("="*50 + "\n")
            
            # Success message
            success_msg = f"✅ Order Confirmed!\n\n"
            success_msg += f"{order_count} items ordered\n"
            success_msg += f"Total: ₱{total:.2f}\n"
            success_msg += f"Type: {order_type_msg}\n\n"
            success_msg += f"Status: Pending Admin Approval\n\n"
            success_msg += f"Check 'My Orders' to view status."
            
            messagebox.showinfo("Success", success_msg)
            
            # Clear cart
            self.cart = []
            self.update_cart_display()
            
        except Exception as e:
            print(f"\n✗✗✗ ERROR SAVING ORDER ✗✗✗")
            print(f"Error: {str(e)}")
            print("="*50 + "\n")
            messagebox.showerror("Error", f"Failed to save order:\n\n{str(e)}\n\nPlease try again.")
            try:
                self.app.db_connection.rollback()
            except:
                pass
    
    def view_my_orders(self):
        """View user's order history with detailed information"""
        orders_window = tk.Toplevel(self.app.root)
        orders_window.title("My Orders")
        orders_window.geometry("1000x650")
        orders_window.configure(bg=self.app.bg_color)
        orders_window.resizable(True, True)
        
        # Title
        title_frame = tk.Frame(orders_window, bg=self.app.bg_color, padx=30, pady=20)
        title_frame.pack(fill='x')
        
        tk.Label(title_frame, text="📋 My Orders", font=("Segoe UI", 24, "bold"),
                bg=self.app.bg_color, fg=self.app.dark_brown).pack(side='left')
        
        # Refresh button
        tk.Button(title_frame, text="↻ Refresh", font=("Segoe UI", 10),
                 bg=self.app.accent_color, fg=self.app.secondary_bg, bd=0, cursor="hand2",
                 padx=15, pady=8, command=lambda: load_orders()).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(orders_window, bg=self.app.bg_color, padx=30)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Status:", font=("Segoe UI", 11),
                bg=self.app.bg_color, fg=self.app.text_color).pack(side='left', padx=(0, 10))
        
        filter_var = tk.StringVar(value="All")
        
        for status in ["All", "Pending", "Approved", "Rejected"]:
            tk.Radiobutton(filter_frame, text=status, variable=filter_var, value=status,
                          font=("Segoe UI", 10), bg=self.app.bg_color, fg=self.app.text_color,
                          selectcolor=self.app.secondary_bg, 
                          command=lambda: load_orders(filter_var.get())).pack(side='left', padx=5)
        
        # Treeview
        tree_frame = tk.Frame(orders_window, bg=self.app.bg_color, padx=30)
        tree_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        columns = ('Order ID', 'Item', 'Qty', 'Price', 'Total', 'Type', 'Status', 'Date')
        orders_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=18)
        
        # Configure columns
        for col in columns:
            orders_tree.heading(col, text=col)
            if col == 'Order ID':
                orders_tree.column(col, width=80)
            elif col == 'Item':
                orders_tree.column(col, width=220)
            elif col == 'Qty':
                orders_tree.column(col, width=60)
            elif col in ['Price', 'Total']:
                orders_tree.column(col, width=100)
            elif col == 'Type':
                orders_tree.column(col, width=130)
            elif col == 'Status':
                orders_tree.column(col, width=100)
            else:
                orders_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=orders_tree.yview)
        orders_tree.configure(yscrollcommand=scrollbar.set)
        
        orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status color tags
        orders_tree.tag_configure('Pending', foreground='#FFA726')
        orders_tree.tag_configure('Approved', foreground='#4CAF50')
        orders_tree.tag_configure('Rejected', foreground='#e74c3c')
        
        def load_orders(status_filter="All"):
            """Load user's orders with optional filter"""
            for item in orders_tree.get_children():
                orders_tree.delete(item)
            
            try:
                cursor = self.app.db_connection.cursor(dictionary=True)
                
                if status_filter == "All":
                    cursor.execute("""
                        SELECT order_id, item_name, quantity, price, total_price, 
                               order_type, order_status, order_date
                        FROM orders
                        WHERE user_id = %s
                        ORDER BY order_date DESC
                    """, (self.app.current_user['user_id'],))
                else:
                    cursor.execute("""
                        SELECT order_id, item_name, quantity, price, total_price, 
                               order_type, order_status, order_date
                        FROM orders
                        WHERE user_id = %s AND order_status = %s
                        ORDER BY order_date DESC
                    """, (self.app.current_user['user_id'], status_filter))

                orders = cursor.fetchall()
                cursor.close()

                if not orders:
                    orders_tree.insert('', tk.END, values=('', 'No orders found for this status', '', '', '', '', '', ''), 
                                       tags=('empty_message',))
                    # Optionally, you can configure the empty_message tag to center the text
                    # (This is more complex in ttk, but the simplest approach is to insert a row)
                    status_summary.config(text="Total Orders: 0")
                    return
                
                # Variables for summary
                total_orders = 0
                total_spent = 0.0
                pending_count = 0
                approved_count = 0
                rejected_count = 0

                for order in orders:
                    # Insert data into the Treeview
                    orders_tree.insert('', tk.END, values=(
                        order['order_id'],
                        order['item_name'],
                        order['quantity'],
                        f"₱{float(order['price']):.2f}",
                        f"₱{float(order['total_price']):.2f}",
                        order.get('order_type', 'N/A'),
                        order['order_status'],
                        order['order_date'].strftime("%Y-%m-%d %H:%M")
                    ), tags=(order['order_status'],))
                    
                    # Update summary variables
                    total_orders += 1
                    total_spent += float(order['total_price'])
                    if order['order_status'] == 'Pending':
                        pending_count += 1
                    elif order['order_status'] == 'Approved':
                        approved_count += 1
                    elif order['order_status'] == 'Rejected':
                        rejected_count += 1

                # Update the status summary label
                summary_text = f"Total Orders: {total_orders} | Spent: ₱{total_spent:.2f} | "
                summary_text += f"Pending: {pending_count} | Approved: {approved_count} | Rejected: {rejected_count}"
                status_summary.config(text=summary_text)

            except Error as e:
                messagebox.showerror("Database Error", f"Error loading orders: {e}")
                print(f"Database Error: {e}") # Debugging line
        
        # NOTE: The summary_frame, status_summary, legend_frame, and close_frame
        # need to be defined outside of load_orders but inside view_my_orders.
        # Assuming they are defined right after the Treeview is packed:
        
        # Status summary at bottom (continuing the view_my_orders method)
        summary_frame = tk.Frame(orders_window, bg=self.app.bg_color, padx=30, pady=10)
        summary_frame.pack(fill='x')
        
        status_summary = tk.Label(summary_frame, text="Total Orders: 0", 
                                 font=("Segoe UI", 11, "bold"),
                                 bg=self.app.bg_color, fg=self.app.text_color)
        status_summary.pack(side='left')
        
        # Legend
        legend_frame = tk.Frame(summary_frame, bg=self.app.bg_color)
        legend_frame.pack(side='right')
        
        tk.Label(legend_frame, text="● Pending", font=("Segoe UI", 9),
                bg=self.app.bg_color, fg='#FFA726').pack(side='left', padx=10)
        tk.Label(legend_frame, text="● Approved", font=("Segoe UI", 9),
                bg=self.app.bg_color, fg='#4CAF50').pack(side='left', padx=10)
        tk.Label(legend_frame, text="● Rejected", font=("Segoe UI", 9),
                bg=self.app.bg_color, fg='#e74c3c').pack(side='left', padx=10)
        
        # Close button
        close_frame = tk.Frame(orders_window, bg=self.app.bg_color, pady=10)
        close_frame.pack(fill='x')
        
        tk.Button(close_frame, text="Close", font=("Segoe UI", 11),
                 bg=self.app.secondary_bg, fg=self.app.text_color, bd=0, cursor="hand2",
                 padx=30, pady=10, command=orders_window.destroy).pack()
        
        # Load initial orders
        load_orders()
                                   