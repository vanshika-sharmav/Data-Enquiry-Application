"""
app.py

Data Inquiry Application
-------------------------
A command-line tool that lets you query, add, update, and delete
records in a SQLite database using SQL.

Features:
- View, search, filter, and sort products
- Input validation (no negative prices/quantities, no empty names)
- Low stock alerts
- Export query results to CSV

Before running this file, make sure you've run setup_database.py
once to create the database:
    python setup_database.py
    python app.py
"""

import sqlite3
import csv

DB_NAME = "inventory.db"


def get_connection():
    """Open and return a connection to the database."""
    return sqlite3.connect(DB_NAME)


# ---------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------

def get_valid_text(prompt):
    """Keep asking until the user enters some non-empty text."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field can't be empty. Please try again.")


def get_valid_number(prompt, number_type=float, allow_zero=True):
    """
    Keep asking until the user enters a valid, non-negative number.
    number_type can be `float` or `int`.
    """
    while True:
        raw_value = input(prompt).strip()
        try:
            value = number_type(raw_value)
        except ValueError:
            print(f"That's not a valid {number_type.__name__}. Please try again.")
            continue

        if value < 0:
            print("Negative values aren't allowed. Please try again.")
            continue
        if value == 0 and not allow_zero:
            print("Zero isn't allowed here. Please try again.")
            continue

        return value


# ---------------------------------------------------------------------
# Query functions
# ---------------------------------------------------------------------

def view_all_products():
    """Show every product in the database."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    connection.close()

    print_results(rows)
    return rows


def search_by_name():
    """Search for products whose name contains a keyword."""
    keyword = input("Enter a product name (or part of it) to search: ")

    connection = get_connection()
    cursor = connection.cursor()
    # The % symbols allow partial matches (e.g. "lamp" matches "Desk Lamp")
    cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{keyword}%",))
    rows = cursor.fetchall()
    connection.close()

    print_results(rows)
    return rows


def filter_by_category():
    """Show all products in a given category."""
    category = input("Enter a category (e.g. Electronics, Furniture): ")

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    rows = cursor.fetchall()
    connection.close()

    print_results(rows)
    return rows


def sort_by_price():
    """Show all products sorted by price."""
    order = input("Sort lowest to highest or highest to lowest? (low/high): ").strip().lower()
    direction = "ASC" if order == "low" else "DESC"

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM products ORDER BY price {direction}")
    rows = cursor.fetchall()
    connection.close()

    print_results(rows)
    return rows


def show_low_stock():
    """Show products whose quantity is below a threshold the user picks."""
    threshold = int(get_valid_number("Alert me for quantity below: ", number_type=int))

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products WHERE quantity < ? ORDER BY quantity ASC", (threshold,))
    rows = cursor.fetchall()
    connection.close()

    if not rows:
        print(f"\nNo products are below a quantity of {threshold}. Stock looks fine!\n")
    else:
        print(f"\n LOW STOCK ALERT: {len(rows)} product(s) below quantity {threshold}")
        print_results(rows)

    return rows


# ---------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------

def export_to_csv(rows=None):
    """
    Export product rows to a CSV file.
    If no rows are passed in, exports the entire products table.
    """
    if rows is None:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        connection.close()

    if not rows:
        print("There's nothing to export.\n")
        return

    filename = input("Enter a filename to save as (e.g. export.csv): ").strip()
    if not filename:
        filename = "products_export.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "category", "price", "quantity"])
        writer.writerows(rows)

    print(f"Exported {len(rows)} row(s) to '{filename}'.\n")


# ---------------------------------------------------------------------
# Add / update / delete
# ---------------------------------------------------------------------

def add_product():
    """Add a new product to the database, with input validation."""
    name = get_valid_text("Product name: ")
    category = get_valid_text("Category: ")
    price = get_valid_number("Price: ", number_type=float, allow_zero=False)
    quantity = int(get_valid_number("Quantity: ", number_type=int, allow_zero=True))

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO products (name, category, price, quantity)
        VALUES (?, ?, ?, ?)
    """, (name, category, price, quantity))
    connection.commit()
    connection.close()

    print(f"Added '{name}' to the database.")


def update_quantity():
    """Update the quantity of an existing product by its ID."""
    product_id = int(get_valid_number("Enter the ID of the product to update: ", number_type=int))
    new_quantity = int(get_valid_number("Enter the new quantity: ", number_type=int, allow_zero=True))

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE products SET quantity = ? WHERE id = ?
    """, (new_quantity, product_id))
    connection.commit()
    rows_changed = cursor.rowcount
    connection.close()

    if rows_changed:
        print("Quantity updated successfully.")
    else:
        print(f"No product found with ID {product_id}.")


def delete_product():
    """Delete a product from the database by its ID."""
    product_id = int(get_valid_number("Enter the ID of the product to delete: ", number_type=int))

    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    rows_changed = cursor.rowcount
    connection.close()

    if rows_changed:
        print("Product deleted successfully.")
    else:
        print(f"No product found with ID {product_id}.")


# ---------------------------------------------------------------------
# Display + menu
# ---------------------------------------------------------------------

def print_results(rows):
    """Nicely print a list of product rows to the terminal."""
    if not rows:
        print("No results found.\n")
        return

    print(f"\n{'ID':<4}{'Name':<25}{'Category':<15}{'Price':<10}{'Quantity':<10}")
    print("-" * 64)
    for row in rows:
        id_, name, category, price, quantity = row
        print(f"{id_:<4}{name:<25}{category:<15}${price:<9.2f}{quantity:<10}")
    print()


def show_menu():
    """Display the main menu options."""
    print("=" * 40)
    print("      DATA INQUIRY APPLICATION")
    print("=" * 40)
    print("1. View all products")
    print("2. Search by name")
    print("3. Filter by category")
    print("4. Sort by price")
    print("5. Show low stock alert")
    print("6. Export all products to CSV")
    print("7. Add a new product")
    print("8. Update product quantity")
    print("9. Delete a product")
    print("10. Exit")


def main():
    """Run the application loop."""
    while True:
        show_menu()
        choice = input("Choose an option (1-10): ").strip()

        if choice == "1":
            view_all_products()
        elif choice == "2":
            search_by_name()
        elif choice == "3":
            filter_by_category()
        elif choice == "4":
            sort_by_price()
        elif choice == "5":
            show_low_stock()
        elif choice == "6":
            export_to_csv()
        elif choice == "7":
            add_product()
        elif choice == "8":
            update_quantity()
        elif choice == "9":
            delete_product()
        elif choice == "10":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 10.\n")


if __name__ == "__main__":
    main()
