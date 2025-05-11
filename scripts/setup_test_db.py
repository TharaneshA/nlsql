import os
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path
import typer
from typing import Optional

# Create a CLI app
app = typer.Typer(help="Setup test database for NLSQL")

# Constants
DEFAULT_DB_PATH = Path.home() / ".nlsql" / "test_db.sqlite"

# Sample data
PRODUCT_CATEGORIES = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Toys", "Sports", "Beauty", "Food"]
PRODUCT_NAMES = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Tablet", "Smart Watch", "Camera", "TV", "Speaker"],
    "Clothing": ["T-Shirt", "Jeans", "Dress", "Jacket", "Sweater", "Socks", "Hat", "Shoes"],
    "Books": ["Fiction Novel", "Biography", "Cookbook", "Self-Help", "History Book", "Science Book", "Children's Book", "Poetry"],
    "Home & Kitchen": ["Blender", "Coffee Maker", "Toaster", "Microwave", "Vacuum", "Cookware Set", "Knife Set", "Bedding"],
    "Toys": ["Action Figure", "Board Game", "Puzzle", "Stuffed Animal", "Building Blocks", "Remote Control Car", "Doll", "Educational Toy"],
    "Sports": ["Basketball", "Tennis Racket", "Yoga Mat", "Bicycle", "Weights", "Running Shoes", "Football", "Golf Clubs"],
    "Beauty": ["Shampoo", "Perfume", "Makeup Kit", "Face Cream", "Hair Dryer", "Nail Polish", "Razor", "Lotion"],
    "Food": ["Chocolate", "Coffee", "Pasta", "Snacks", "Cereal", "Canned Goods", "Spices", "Beverages"]
}
FIRST_NAMES = ["John", "Jane", "Michael", "Emily", "David", "Sarah", "Robert", "Lisa", "William", "Emma"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
STATES = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
STATUS_OPTIONS = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]

def create_tables(conn):
    """Create the database tables"""
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
    ''')
    
    # Create product_categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS product_categories (
        category_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        category_id INTEGER,
        price REAL NOT NULL,
        stock_quantity INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES product_categories (category_id)
    )
    ''')
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        shipping_address TEXT,
        shipping_city TEXT,
        shipping_state TEXT,
        shipping_zip_code TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    # Create order_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    conn.commit()

def generate_fake_data(conn, num_users=50, num_products=100, num_orders=200):
    """Generate fake data for the database"""
    cursor = conn.cursor()
    
    # Insert product categories
    for i, category in enumerate(PRODUCT_CATEGORIES, 1):
        cursor.execute(
            "INSERT INTO product_categories (category_id, name, description) VALUES (?, ?, ?)",
            (i, category, f"Products in the {category} category")
        )
    
    # Insert products
    product_id = 1
    for category_id, category in enumerate(PRODUCT_CATEGORIES, 1):
        for product_name in PRODUCT_NAMES[category]:
            price = round(random.uniform(9.99, 999.99), 2)
            stock = random.randint(0, 1000)
            cursor.execute(
                "INSERT INTO products (product_id, name, description, category_id, price, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)",
                (product_id, product_name, f"A {product_name} in the {category} category", category_id, price, stock)
            )
            product_id += 1
    
    # Insert users
    for user_id in range(1, num_users + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{user_id}@example.com"
        phone = f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        city_idx = random.randint(0, len(CITIES) - 1)
        city = CITIES[city_idx]
        state = STATES[city_idx]
        zip_code = f"{random.randint(10000, 99999)}"
        created_at = datetime.now() - timedelta(days=random.randint(1, 1000))
        last_login = created_at + timedelta(days=random.randint(1, 100))
        
        cursor.execute(
            "INSERT INTO users (user_id, first_name, last_name, email, phone, address, city, state, zip_code, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, first_name, last_name, email, phone, f"{random.randint(100, 9999)} Main St", city, state, zip_code, created_at, last_login)
        )
    
    # Insert orders and order items
    for order_id in range(1, num_orders + 1):
        user_id = random.randint(1, num_users)
        order_date = datetime.now() - timedelta(days=random.randint(1, 365))
        status = random.choice(STATUS_OPTIONS)
        
        # Get user's address for shipping
        cursor.execute("SELECT address, city, state, zip_code FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        
        # Generate order items
        num_items = random.randint(1, 5)
        order_items = []
        total_amount = 0
        
        for _ in range(num_items):
            # Ensure valid range for random product selection
            max_product = max(1, product_id - 1)
            item_product_id = random.randint(1, max_product)
            quantity = random.randint(1, 5)
            
            # Get product price
            cursor.execute("SELECT price FROM products WHERE product_id = ?", (item_product_id,))
            price = cursor.fetchone()[0]
            
            item_total = price * quantity
            total_amount += item_total
            order_items.append((product_id, quantity, price))
        
        # Insert order
        cursor.execute(
            "INSERT INTO orders (order_id, user_id, order_date, total_amount, status, shipping_address, shipping_city, shipping_state, shipping_zip_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (order_id, user_id, order_date, total_amount, status, user_data[0], user_data[1], user_data[2], user_data[3])
        )
        
        # Insert order items
        for i, (product_id, quantity, price) in enumerate(order_items, 1):
            cursor.execute(
                "INSERT INTO order_items (order_item_id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
                ((order_id - 1) * 10 + i, order_id, product_id, quantity, price)
            )
    
    conn.commit()

@app.command()
def setup(db_path: Optional[str] = None, users: int = 50, products: int = 100, orders: int = 200):
    """Set up a test SQLite database with sample data"""
    # Determine database path
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    else:
        # Convert string path to Path object
        db_path = Path(db_path)
    
    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database already exists
    if db_path.exists():
        overwrite = typer.confirm(f"Database already exists at {db_path}. Overwrite?", default=False)
        if not overwrite:
            typer.echo("Setup cancelled.")
            return
        db_path.unlink()
    
    typer.echo(f"Setting up test database at {db_path}")
    
    # Create database and tables
    conn = sqlite3.connect(str(db_path))
    create_tables(conn)
    
    # Generate fake data
    typer.echo(f"Generating {users} users, {products} products, and {orders} orders...")
    generate_fake_data(conn, num_users=users, num_products=products, num_orders=orders)
    
    # Create a profile for this database
    try:
        # Import locally to avoid circular imports
        from utils.config import save_profile, set_active_profile, get_active_profile
        
        profile_name = "test_db"
        profile = {
            "type": "SQLite",
            "database": str(db_path),
            "host": "",
            "port": "",
            "username": "",
            "password": "",
            "options": ""
        }
        
        save_profile(profile_name, profile)
        
        # Set as active if no active profile exists
        if not get_active_profile():
            set_active_profile(profile_name)
            typer.echo(f"Set '{profile_name}' as the active profile")
        else:
            typer.echo(f"Created profile '{profile_name}' for the test database")
            typer.echo(f"Switch to it with: nlsql profile use {profile_name}")
    except ImportError:
        typer.echo("Could not create profile automatically. Please create one manually.")
    
    conn.close()
    typer.echo("Test database setup complete!")
    typer.echo("\nSample queries you can try:")
    typer.echo("- Show me all users from New York")
    typer.echo("- What are the top 5 most expensive products?")
    typer.echo("- How many orders were placed in the last 6 months?")
    typer.echo("- Which user has spent the most money?")
    typer.echo("- List all products with less than 10 items in stock")

if __name__ == "__main__":
    app()