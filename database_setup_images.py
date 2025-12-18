"""
Run this script ONCE to add image column to your cafe_items table
This will allow you to store image paths for food items
"""

import mysql.connector
from mysql.connector import Error

def add_image_column():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3307,
            user='root',
            password='',
            database='internet_cafe'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Add image_path column to cafe_items table
            try:
                cursor.execute("""
                    ALTER TABLE cafe_items 
                    ADD COLUMN image_path VARCHAR(255) DEFAULT NULL
                """)
                connection.commit()
                print("✓ Successfully added image_path column to cafe_items table!")
            except Error as e:
                if "Duplicate column name" in str(e):
                    print("✓ image_path column already exists!")
                else:
                    print(f"Error: {e}")
            
            cursor.close()
            connection.close()
            print("✓ Database update complete!")
            
    except Error as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    add_image_column()
    print("\nYou can now add images to your cafe items!")
    print("Place your food images in a folder called 'images' in the same directory as your program.")