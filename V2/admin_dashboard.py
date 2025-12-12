from tkinter import messagebox


def view_pending_requests(self):
    """View pending account requests"""
    if hasattr(self, 'account_requests') and self.account_requests:
        request_list = "\n\n".join([
            f"Request #{i+1}:\n"
            f"• Username: {req['username']}\n"
            f"• Full Name: {req['full_name']}\n"
            f"• Phone: {req['phone']}\n"
            f"• Birthday: {req['birthday']}\n"
            f"• Requested: {req['requested_at']}\n"
            f"• Status: {req['status']}"
            for i, req in enumerate(self.account_requests)
        ])
        messagebox.showinfo("Pending Requests", 
                          f"Pending Account Requests:\n\n{request_list}")
    else:
        messagebox.showinfo("No Requests", "No pending account requests.")