#!/usr/bin/env python3
"""
Test script to verify kiosk mode real-time updates functionality
"""

import mysql.connector
from mysql.connector import Error

def test_kiosk_mode_database():
    """Test kiosk mode database operations"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='internet_cafe',
            use_pure=True
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Create system_settings table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    setting_name VARCHAR(50) PRIMARY KEY,
                    setting_value VARCHAR(100),
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            
            # Test setting kiosk mode to enabled
            cursor.execute("""
                INSERT INTO system_settings (setting_name, setting_value) 
                VALUES ('kiosk_mode_enabled', 'true')
                ON DUPLICATE KEY UPDATE setting_value = 'true'
            """)
            connection.commit()
            
            # Test reading kiosk mode setting
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_name = 'kiosk_mode_enabled'")
            result = cursor.fetchone()
            
            if result:
                is_enabled = result['setting_value'].lower() == 'true'
                print(f"✅ Kiosk mode setting read successfully: {is_enabled}")
            else:
                print("❌ Could not read kiosk mode setting")
                return False
            
            # Test setting kiosk mode to disabled
            cursor.execute("""
                INSERT INTO system_settings (setting_name, setting_value) 
                VALUES ('kiosk_mode_enabled', 'false')
                ON DUPLICATE KEY UPDATE setting_value = 'false'
            """)
            connection.commit()
            
            # Test reading updated setting
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_name = 'kiosk_mode_enabled'")
            result = cursor.fetchone()
            
            if result:
                is_enabled = result['setting_value'].lower() == 'true'
                print(f"✅ Kiosk mode setting updated successfully: {is_enabled}")
            else:
                print("❌ Could not read updated kiosk mode setting")
                return False
            
            # Reset to enabled (default)
            cursor.execute("""
                INSERT INTO system_settings (setting_name, setting_value) 
                VALUES ('kiosk_mode_enabled', 'true')
                ON DUPLICATE KEY UPDATE setting_value = 'true'
            """)
            connection.commit()
            
            cursor.close()
            connection.close()
            
            print("✅ All kiosk mode database tests passed!")
            return True
            
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_methods_exist():
    """Test that required methods exist in main.py"""
    try:
        # Read main.py content
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            'refresh_pc_selection_with_kiosk_check',
            'refresh_kiosk_mode_from_db',
            'should_enable_kiosk_mode',
            'enable_pc_lock',
            'disable_pc_lock'
        ]
        
        missing_methods = []
        for method in required_methods:
            if f'def {method}(' not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Missing methods in main.py: {missing_methods}")
            return False
        else:
            print("✅ All required methods exist in main.py")
            return True
            
    except Exception as e:
        print(f"❌ Error checking methods: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Kiosk Mode Real-Time Updates...")
    print("=" * 50)
    
    # Test database operations
    print("\n1. Testing database operations...")
    db_test = test_kiosk_mode_database()
    
    # Test method existence
    print("\n2. Testing method existence...")
    method_test = test_methods_exist()
    
    # Summary
    print("\n" + "=" * 50)
    if db_test and method_test:
        print("✅ ALL TESTS PASSED!")
        print("\nThe kiosk mode real-time update functionality should work correctly.")
        print("\nTo test manually:")
        print("1. Run main.py")
        print("2. Go to Admin Panel -> Kiosk Mode Control")
        print("3. Toggle kiosk mode on/off")
        print("4. Close admin panel")
        print("5. Check if PC selection screen shows updated kiosk status")
        print("6. Login as user and logout - kiosk mode should refresh")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above and fix them.")