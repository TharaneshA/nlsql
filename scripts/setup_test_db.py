import os
import sqlite3
from pathlib import Path
import typer
from typing import Optional
from datetime import datetime, timedelta
import random

# Import data generation module
from .generate_data import (
    PRODUCT_CATEGORIES, PRODUCT_NAMES, PRODUCT_DESCRIPTIONS,
    generate_price, generate_stock_quantity, generate_user_data, generate_order_data
)

# Create a CLI app
app = typer.Typer(help="Setup test database for NLSQL")

# Constants
DEFAULT_DB_PATH = Path.home() / ".nlsql" / "test_db.sqlite"

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
    products = []
    
    try:
        # Insert product categories with better descriptions
        for i, category in enumerate(PRODUCT_CATEGORIES, 1):
            cursor.execute(
                "INSERT INTO product_categories (category_id, name, description) VALUES (?, ?, ?)",
                (i, category, PRODUCT_DESCRIPTIONS[category])
            )
        
        # Insert products with realistic prices and stock quantities
        product_id = 1
        for category_id, category in enumerate(PRODUCT_CATEGORIES, 1):
            for product_name in PRODUCT_NAMES[category]:
                price = generate_price(category)
                stock = generate_stock_quantity(category)
                description = f"Premium {product_name.lower()} - {PRODUCT_DESCRIPTIONS[category]}"
                
                cursor.execute(
                    "INSERT INTO products (product_id, name, description, category_id, price, stock_quantity) VALUES (?, ?, ?, ?, ?, ?)",
                    (product_id, product_name, description, category_id, price, stock)
                )
                
                products.append({"id": product_id, "price": price})
                product_id += 1
        
        # Insert users with more realistic data
        for user_id in range(1, num_users + 1):
            user_data = generate_user_data(user_id)
            last_login = user_data["created_at"] + timedelta(days=random.randint(1, 100))
            
            cursor.execute(
                "INSERT INTO users (user_id, first_name, last_name, email, phone, address, city, state, zip_code, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_data["first_name"], user_data["last_name"], user_data["email"],
                 user_data["phone"], user_data["address"], user_data["city"], user_data["state"],
                 user_data["zip_code"], user_data["created_at"], last_login)
            )
        
        # Insert orders with realistic patterns
        for order_id in range(1, num_orders + 1):
            user_id = random.randint(1, num_users)
            
            # Get user's address for shipping
            cursor.execute("SELECT address, city, state, zip_code FROM users WHERE user_id = ?", (user_id,))
            user_data = cursor.fetchone()
            
            # Generate order with realistic data
            order_data = generate_order_data(user_id, products)
            
            # Insert order
            cursor.execute(
                "INSERT INTO orders (order_id, user_id, order_date, total_amount, status, shipping_address, shipping_city, shipping_state, shipping_zip_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order_id, user_id, order_data["order_date"], order_data["total_amount"],
                 order_data["status"], user_data[0], user_data[1], user_data[2], user_data[3])
            )
            
            # Insert order items
            for i, item in enumerate(order_data["items"], 1):
                cursor.execute(
                    "INSERT INTO order_items (order_item_id, order_id, product_id, quantity, price) VALUES (?, ?, ?, ?, ?)",
                    ((order_id - 1) * 10 + i, order_id, item["product_id"], item["quantity"], item["price"])
                )
        
        conn.commit()
        
    except sqlite3.Error as e:
        conn.rollback()
        raise typer.Exit(1)
    except Exception as e:
        conn.rollback()
        raise typer.Exit(1)

@app.command()
def setup(db_path: Optional[str] = None, users: int = 50, products: int = 100, orders: int = 200):
    """Set up a test SQLite database with sample data"""
    # Determine database path
    db_path_obj = DEFAULT_DB_PATH if db_path is None else Path(db_path)
    
    # Create parent directory if it doesn't exist
    db_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database already exists
    if db_path_obj.exists():
        overwrite = typer.confirm(f"Database already exists at {db_path_obj}. Overwrite?", default=False)
        if not overwrite:
            typer.echo("Setup cancelled.")
            return
        db_path_obj.unlink()
    
    typer.echo(f"Setting up test database at {db_path_obj}")
    
    # Create database and tables
    conn = sqlite3.connect(str(db_path_obj))
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
            "database": str(db_path_obj),
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