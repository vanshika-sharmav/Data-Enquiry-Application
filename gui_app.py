"""
gui_app.py

Data Inquiry Application - GUI Version
----------------------------------------
The same product database app as app.py, but with a graphical
interface built using tkinter (built into Python, no install needed).

Features:
- View all products in a table
- Search by name, filter by category, sort by price
- Low stock rows are highlighted in red automatically
- Add, update quantity, and delete products (with validation)
- Export the currently displayed results to CSV

Before running this file, make sure you've run setup_database.py
once to create the database:
    python setup_database.py
    python gui_app.py
"""

import sqlite3
import csv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

DB_NAME = "inventory.db"
LOW_STOCK_THRESHOLD = 20  # Rows with quantity below this are highlighted


class DataInquiryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Inquiry Application")
        self.root.geometry("750x500")

        self.build_search_bar()
        self.build_table()
        self.build_action_buttons()

        self.load_all_products()

    # -----------------------------------------------------------------
    # Database helpers
    # -----------------------------------------------------------------

    def get_connection(self):
        return sqlite3.connect(DB_NAME)

    def run_query(self, query, params=()):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        connection.close()
        return rows

    def run_update(self, query, params=()):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        rows_changed = cursor.rowcount
        connection.close()
        return rows_changed

    # -----------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------

    def build_search_bar(self):
        frame = tk.Frame(self.root, pady=10)
        frame.pack(fill="x", padx=10)

        tk.Label(frame, text="Search name:").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(frame, width=15)
        self.search_entry.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Category:").grid(row=0, column=2, padx=5)
        self.category_entry = tk.Entry(frame, width=12)
        self.category_entry.grid(row=0, column=3, padx=5)

        tk.Button(frame, text="Search", command=self.search_by_name).grid(row=0, column=4, padx=5)
        tk.Button(frame, text="Filter", command=self.filter_by_category).grid(row=0, column=5, padx=5)
        tk.Button(frame, text="Sort by Price ↑", command=lambda: self.sort_by_price("ASC")).grid(row=0, column=6, padx=5)
        tk.Button(frame, text="Sort by Price ↓", command=lambda: self.sort_by_price("DESC")).grid(row=0, column=7, padx=5)
        tk.Button(frame, text="Show All", command=self.load_all_products).grid(row=0, column=8, padx=5)

    def build_table(self):
        columns = ("id", "name", "category", "price", "quantity")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        headings = {"id": "ID", "name": "Name", "category": "Category", "price": "Price", "quantity": "Quantity"}
        widths = {"id": 40, "name": 220, "category": 130, "price": 90, "quantity": 90}

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center" if col != "name" else "w")

        # Rows below the low stock threshold will use this red-tinted tag
        self.tree.tag_configure("low_stock", background="#ffdddd")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

    def build_action_buttons(self):
        frame = tk.Frame(self.root, pady=10)
        frame.pack(fill="x", padx=10)

        tk.Button(frame, text="Add Product", command=self.add_product).pack(side="left", padx=5)
        tk.Button(frame, text="Update Quantity", command=self.update_quantity).pack(side="left", padx=5)
        tk.Button(frame, text="Delete Product", command=self.delete_product).pack(side="left", padx=5)
        tk.Button(frame, text="Low Stock Alert", command=self.show_low_stock, fg="red").pack(side="left", padx=5)
        tk.Button(frame, text="Export to CSV", command=self.export_to_csv).pack(side="right", padx=5)

        self.status_label = tk.Label(self.root, text="", fg="gray")
        self.status_label.pack(pady=(0, 5))

    # -----------------------------------------------------------------
    # Table display
    # -----------------------------------------------------------------

    def display_rows(self, rows):
        """Clear the table and re-populate it, highlighting low stock rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            id_, name, category, price, quantity = row
            tags = ("low_stock",) if quantity < LOW_STOCK_THRESHOLD else ()
            self.tree.insert("", "end", values=(id_, name, category, f"${price:.2f}", quantity), tags=tags)

        self.current_rows = rows
        self.status_label.config(text=f"{len(rows)} result(s) — rows in red are below {LOW_STOCK_THRESHOLD} in stock")

    # -----------------------------------------------------------------
    # Query actions
    # -----------------------------------------------------------------

    def load_all_products(self):
        rows = self.run_query("SELECT * FROM products")
        self.display_rows(rows)

    def search_by_name(self):
        keyword = self.search_entry.get().strip()
        rows = self.run_query("SELECT * FROM products WHERE name LIKE ?", (f"%{keyword}%",))
        self.display_rows(rows)

    def filter_by_category(self):
        category = self.category_entry.get().strip()
        rows = self.run_query("SELECT * FROM products WHERE category = ?", (category,))
        self.display_rows(rows)

    def sort_by_price(self, direction):
        rows = self.run_query(f"SELECT * FROM products ORDER BY price {direction}")
        self.display_rows(rows)

    def show_low_stock(self):
        rows = self.run_query(
            "SELECT * FROM products WHERE quantity < ? ORDER BY quantity ASC",
            (LOW_STOCK_THRESHOLD,)
        )
        self.display_rows(rows)
        if not rows:
            messagebox.showinfo("Low Stock Alert", f"No products are below a quantity of {LOW_STOCK_THRESHOLD}.")

    # -----------------------------------------------------------------
    # Add / update / delete (with validation)
    # -----------------------------------------------------------------

    def add_product(self):
        name = simpledialog.askstring("Add Product", "Product name:")
        if not name or not name.strip():
            messagebox.showerror("Invalid input", "Product name can't be empty.")
            return

        category = simpledialog.askstring("Add Product", "Category:")
        if not category or not category.strip():
            messagebox.showerror("Invalid input", "Category can't be empty.")
            return

        price = self.ask_valid_number("Price:", allow_zero=False, number_type=float)
        if price is None:
            return

        quantity = self.ask_valid_number("Quantity:", allow_zero=True, number_type=int)
        if quantity is None:
            return

        self.run_update(
            "INSERT INTO products (name, category, price, quantity) VALUES (?, ?, ?, ?)",
            (name.strip(), category.strip(), price, quantity)
        )
        messagebox.showinfo("Success", f"Added '{name}' to the database.")
        self.load_all_products()

    def update_quantity(self):
        selected = self.get_selected_id()
        if selected is None:
            return

        new_quantity = self.ask_valid_number("New quantity:", allow_zero=True, number_type=int)
        if new_quantity is None:
            return

        changed = self.run_update("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, selected))
        if changed:
            messagebox.showinfo("Success", "Quantity updated.")
        else:
            messagebox.showerror("Error", f"No product found with ID {selected}.")
        self.load_all_products()

    def delete_product(self):
        selected = self.get_selected_id()
        if selected is None:
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Delete product ID {selected}? This can't be undone.")
        if not confirm:
            return

        changed = self.run_update("DELETE FROM products WHERE id = ?", (selected,))
        if changed:
            messagebox.showinfo("Success", "Product deleted.")
        else:
            messagebox.showerror("Error", f"No product found with ID {selected}.")
        self.load_all_products()

    def get_selected_id(self):
        """Return the ID of the row selected in the table, or show an error."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("No selection", "Please click a row in the table first.")
            return None
        values = self.tree.item(selection[0], "values")
        return int(values[0])

    def ask_valid_number(self, prompt, allow_zero, number_type):
        """Keep asking a simple dialog box until a valid, non-negative number is given."""
        while True:
            raw_value = simpledialog.askstring("Add Product", prompt)
            if raw_value is None:
                return None  # user clicked Cancel
            try:
                value = number_type(raw_value)
            except ValueError:
                messagebox.showerror("Invalid input", f"Please enter a valid {number_type.__name__}.")
                continue
            if value < 0:
                messagebox.showerror("Invalid input", "Negative values aren't allowed.")
                continue
            if value == 0 and not allow_zero:
                messagebox.showerror("Invalid input", "Zero isn't allowed here.")
                continue
            return value

    # -----------------------------------------------------------------
    # CSV export
    # -----------------------------------------------------------------

    def export_to_csv(self):
        rows = getattr(self, "current_rows", [])
        if not rows:
            messagebox.showinfo("Nothing to export", "There are no rows currently displayed.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="products_export.csv"
        )
        if not filepath:
            return  # user cancelled

        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "category", "price", "quantity"])
            writer.writerows(rows)

        messagebox.showinfo("Export complete", f"Exported {len(rows)} row(s) to:\n{filepath}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataInquiryApp(root)
    root.mainloop()
