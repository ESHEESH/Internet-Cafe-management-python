# 🔒 Kiosk Mode Control Guide

## Overview
The Starbroke Internet Cafe System now includes **Global Kiosk Mode Control** that allows administrators to enable or disable PC lock features system-wide.

---

## 🎯 **How to Use Kiosk Mode Control**

### **Step 1: Access Admin Panel**
1. Click **"🔒 Admin Panel"** on PC selection screen
2. Login with admin credentials:
   - Username: `admin`
   - Password: `admin123`

### **Step 2: Navigate to Kiosk Control**
1. In the admin panel sidebar, click **"🔒 Kiosk Mode Control"**
2. You'll see the current status and control options

### **Step 3: Toggle Kiosk Mode**
- **To ENABLE**: Click **"🔒 ENABLE Kiosk Mode"**
- **To DISABLE**: Click **"🔓 DISABLE Kiosk Mode"**

---

## 🔒 **When Kiosk Mode is ENABLED**

### **User Experience:**
- ✅ Full-screen lock active
- ✅ Alt+Tab is blocked
- ✅ Task Manager is disabled
- ✅ Windows key is blocked
- ✅ System keys are blocked
- ✅ Taskbar is hidden
- ✅ Cannot switch to other applications

### **Security Level:** **HIGH** 🔴

### **PC Selection Screen Shows:**
```
🔒 KIOSK MODE ACTIVE
• Alt+Tab Disabled • System Keys Blocked • Secure Mode
```

---

## 🔓 **When Kiosk Mode is DISABLED**

### **User Experience:**
- ✅ Normal window behavior
- ✅ Alt+Tab works normally
- ✅ Task Manager accessible
- ✅ System keys functional
- ✅ Can switch between applications
- ✅ Taskbar visible

### **Security Level:** **REDUCED** 🟡

### **PC Selection Screen Shows:**
```
🔓 KIOSK MODE DISABLED
• Normal Window Behavior • Reduced Security Mode
```

---

## ⚙️ **Technical Details**

### **Database Storage**
- Setting stored in `system_settings` table
- Setting name: `kiosk_mode_enabled`
- Values: `'true'` or `'false'`

### **Default Behavior**
- **Default**: Kiosk Mode is **ENABLED** (for security)
- **First Run**: Creates setting with `'true'` value
- **Database Error**: Defaults to **ENABLED** (fail-safe)

### **When Changes Take Effect**
- **Immediate**: PC selection screen updates instantly
- **New Logins**: Users logging in get the new setting
- **Existing Sessions**: May need to logout/login to see changes

---

## 🚨 **Important Security Notes**

### **⚠️ Disabling Kiosk Mode Reduces Security**
When kiosk mode is disabled:
- Users can access other applications
- Users can potentially access system settings
- Users might be able to browse the internet outside the cafe system
- Risk of users installing software or changing settings

### **✅ Recommended Usage**
- **Keep ENABLED** for public internet cafes
- **Disable temporarily** only for maintenance or special users
- **Re-enable immediately** after maintenance

### **🔧 Emergency Features Still Work**
Regardless of kiosk mode setting:
- ✅ Emergency Exit always available
- ✅ Emergency Unlock always works
- ✅ Admin panels are never affected
- ✅ Force logout from admin panel works

---

## 📋 **Step-by-Step Demo**

### **Test 1: Disable Kiosk Mode**
1. Start application → See "🔒 KIOSK MODE ACTIVE"
2. Open Admin Panel → Login
3. Go to "🔒 Kiosk Mode Control"
4. Click "🔓 DISABLE Kiosk Mode"
5. Confirm the action
6. Return to PC selection → See "🔓 KIOSK MODE DISABLED"
7. Login as user → Alt+Tab should work

### **Test 2: Enable Kiosk Mode**
1. In Admin Panel → "🔒 Kiosk Mode Control"
2. Click "🔒 ENABLE Kiosk Mode"
3. Confirm the action
4. Return to PC selection → See "🔒 KIOSK MODE ACTIVE"
5. Login as user → Alt+Tab should be blocked

---

## 🔧 **Troubleshooting**

### **Problem: Changes Don't Take Effect**
**Solution:**
1. Logout current user session
2. Return to PC selection screen
3. Login again to see changes

### **Problem: Can't Access Admin Panel**
**Solution:**
1. Use Emergency Exit (requires admin credentials)
2. Restart application
3. Admin panels are never affected by kiosk mode

### **Problem: Database Error**
**Solution:**
1. Check MySQL/XAMPP is running
2. Verify database connection
3. System defaults to ENABLED for security

---

## 💡 **Best Practices**

### **For Internet Cafe Owners:**
1. **Keep kiosk mode ENABLED** during business hours
2. **Disable temporarily** for trusted customers or maintenance
3. **Monitor user sessions** regularly
4. **Train staff** on emergency procedures

### **For System Administrators:**
1. **Test both modes** before going live
2. **Document your security policy**
3. **Regular database backups**
4. **Monitor system logs**

---

## 🎯 **Quick Reference**

| Feature | Enabled | Disabled |
|---------|---------|----------|
| Alt+Tab | ❌ Blocked | ✅ Works |
| Task Manager | ❌ Blocked | ✅ Works |
| Windows Key | ❌ Blocked | ✅ Works |
| Full Screen | ✅ Forced | ❌ Normal |
| Taskbar | ❌ Hidden | ✅ Visible |
| Security Level | 🔴 High | 🟡 Reduced |

---

**🔒 Remember: Security first! Keep kiosk mode enabled unless absolutely necessary to disable it.**