import mysql.connector

print("=== Testing XAMPP MySQL Connection ===")

try:
    # Try to connect to XAMPP MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # XAMPP default has no password
        port=3306
    )
    
    print("✅ Successfully connected to MySQL!")
    
    cursor = conn.cursor()
    
    # Show databases
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    print(f"\nFound {len(databases)} databases:")
    for db in databases:
        print(f"  - {db[0]}")
    
    # Create our database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS starbroke_db")
    print("✅ Created/verified 'starbroke_db' database")
    
    cursor.execute("USE starbroke_db")
    
    # Test creating a table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Created test table")
    
    # Insert test data
    cursor.execute("INSERT INTO test_table (name) VALUES (%s)", ("Test User",))
    conn.commit()
    print("✅ Inserted test data")
    
    # Query test data
    cursor.execute("SELECT * FROM test_table")
    results = cursor.fetchall()
    print(f"✅ Found {len(results)} records in test table")
    
    cursor.close()
    conn.close()
    print("\n✅ All tests passed! MySQL is working correctly.")
    
except mysql.connector.Error as err:
    print(f"❌ MySQL Error: {err}")
    print(f"Error code: {err.errno}")
    
    if err.errno == 2003:
        print("\n⚠️ Cannot connect to MySQL server. Please check:")
        print("   1. Is XAMPP running?")
        print("   2. Is MySQL service started in XAMPP Control Panel?")
        print("   3. Check XAMPP Control Panel - MySQL should show 'Running'")
    elif err.errno == 1045:
        print("\n⚠️ Access denied. Try these:")
        print("   1. Open XAMPP Control Panel")
        print("   2. Click 'Shell' button")
        print("   3. Type: mysqladmin -u root password ''")
        print("   4. Press Enter (this sets empty password)")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")