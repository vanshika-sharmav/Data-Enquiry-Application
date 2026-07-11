# Data Inquiry Application

A Python application to query, filter, and manage a relational database — available as both a command-line tool and a graphical (Tkinter) desktop app. Built as a hands-on introduction to SQL, database design, and Python application structure.

## Features

- **Query & filter** — search products by name, filter by category, and sort by price using parameterized SQL (`SELECT`).
- **Full CRUD support** — add, update, and delete records (`INSERT`, `UPDATE`, `DELETE`).
- **Low stock alerts** — flag products below a configurable quantity threshold.
- **CSV export** — export query results for reporting or use in other tools.
- **Input validation** — blocks empty fields and negative prices/quantities to keep data clean.
- **Two interfaces** — a menu-driven CLI (`app.py`) and a graphical desktop app (`gui_app.py`) built with Tkinter, including a live data table with automatic low-stock highlighting.

## Tech Stack

- **Language:** Python 3
- **Database:** SQLite (via Python's built-in `sqlite3` module)
- **GUI:** Tkinter (Python standard library)
- **Version Control:** Git

No external dependencies — everything runs with a standard Python 3.8+ installation.

## Screenshots

*(Add screenshots of the GUI table view and low-stock alert here once you run the app — this is one of the first things recruiters look at on a project README.)*

## Getting Started

### Prerequisites
- Python 3.8 or higher

### Installation
```bash
git clone https://github.com/your-username/data-inquiry-application.git
cd data-inquiry-application
```

### Set up the database
This creates `inventory.db` and seeds it with sample product data (only needs to be run once):
```bash
python setup_database.py
```

### Run the app

**Command-line version:**
```bash
python app.py
```

**Graphical (Tkinter) version:**
```bash
python gui_app.py
```

## Project Structure

```
data-inquiry-application/
├── app.py               # Command-line interface
├── gui_app.py            # Tkinter graphical interface
├── setup_database.py     # Creates and seeds the SQLite database
├── requirements.txt       # Dependency notes (standard library only)
├── LICENSE
├── .gitignore
└── README.md
```

## Example Usage

The database starts with 8 sample products (electronics, stationery, furniture, and accessories). From either interface you can:
- Search `"lamp"` → returns *Desk Lamp*
- Filter by category `"Electronics"` → returns *Wireless Mouse*, *Bluetooth Speaker*
- Set a low-stock threshold of `20` → flags any product with fewer than 20 units in stock
- Export the current results to a `.csv` file

## Roadmap / Possible Improvements

- [ ] Support for multiple database tables (e.g., suppliers, orders)
- [ ] User authentication for multi-user access
- [ ] Charts/analytics view (e.g., stock levels by category)
- [ ] Package as a standalone executable with PyInstaller

## Author

**Vanshika Sharma**
B.Tech Information Technology, University Institute of Technology (UIT) Shimla
