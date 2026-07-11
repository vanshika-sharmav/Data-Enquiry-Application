"""
setup_database.py

This script creates a simple SQLite database called 'inventory.db'
with one table: 'products'. It also fills the table with some
sample data so the app has something to query right away.

Run this file ONCE before running app.py:
    python setup_database.py
"""

import sqlite3

# Connect to (or create) the database file
connection = sqlite3.connect("inventory.db")
cursor = connection.cursor()

# Create the 'products' table if it doesn't already exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
""")

# Sample data: (name, category, price, quantity)
sample_products = [
    ("Wireless Mouse", "Electronics", 15.99, 50),
    ("Notebook", "Stationery", 2.50, 200),
    ("Desk Lamp", "Furniture", 22.00, 30),
    ("Bluetooth Speaker", "Electronics", 45.00, 15),
    ("Water Bottle", "Accessories", 8.75, 100),
    ("Backpack", "Accessories", 35.00, 25),
    ("Ballpoint Pen (Pack of 10)", "Stationery", 3.20, 150),
    ("Office Chair", "Furniture", 89.99, 10),
]

# Only insert sample data if the table is currently empty
cursor.execute("SELECT COUNT(*) FROM products")
row_count = cursor.fetchone()[0]

if row_count == 0:
    cursor.executemany("""
        INSERT INTO products (name, category, price, quantity)
        VALUES (?, ?, ?, ?)
    """, sample_products)
    print(f"Inserted {len(sample_products)} sample products into the database.")
else:
    print("Database already has data. Skipping sample data insert.")

# Save changes and close the connection
connection.commit()
connection.close()

print("Database setup complete. File created: inventory.db")
