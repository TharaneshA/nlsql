import os
import json
from pathlib import Path

def extract_schema_from_mysql(connection):
    """Extract schema from a MySQL database."""
    schema = {"tables": {}}
    cursor = connection.cursor(dictionary=True)
    # Get tables
    cursor.execute("SHOW TABLES")
    tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
    for table in tables:
        # Get columns
        cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        columns = cursor.fetchall()
        # Get foreign keys
        cursor.execute(f"SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table}' AND REFERENCED_TABLE_NAME IS NOT NULL")
        fks = cursor.fetchall()
        schema["tables"][table] = {
            "columns": columns,
            "foreign_keys": fks
        }
    cursor.close()
    return schema

def extract_schema_from_postgresql(connection):
    """Extract schema from a PostgreSQL database."""
    schema = {"tables": {}}
    cursor = connection.cursor()
    
    # Get tables in the public schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        # Get columns
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table}'
        """)
        columns = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"""
            SELECT
                kcu.column_name,
                ccu.table_name AS referenced_table,
                ccu.column_name AS referenced_column
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table}'
        """)
        fks = cursor.fetchall()
        
        schema["tables"][table] = {
            "columns": columns,
            "foreign_keys": fks
        }
    
    cursor.close()
    return schema

def extract_schema_from_sqlite(connection):
    """Extract schema from a SQLite database."""
    schema = {"tables": {}}
    cursor = connection.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables:
        # Get columns
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        fks = cursor.fetchall()
        
        schema["tables"][table] = {
            "columns": columns,
            "foreign_keys": fks
        }
    
    cursor.close()
    return schema

def get_schema(database_connection, force_refresh=False):
    """Get database schema with caching."""
    # Create cache directory
    cache_dir = Path.home() / ".nlsql" / "schema_cache"
    cache_dir.mkdir(exist_ok=True, parents=True)
    
    # Determine database type and name
    db_type = database_connection.profile.get('type', 'MySQL')
    db_name = database_connection.profile.get('database', 'default')
    
    # Create cache file path
    cache_file = cache_dir / f"{db_type}_{db_name}_schema.json"
    
    # Return cached schema if available and not forcing refresh
    if cache_file.exists() and not force_refresh:
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    # Connect to database
    conn = database_connection.connect()
    
    # Extract schema based on database type
    if db_type == "MySQL":
        schema = extract_schema_from_mysql(conn)
    elif db_type == "PostgreSQL":
        schema = extract_schema_from_postgresql(conn)
    elif db_type == "SQLite":
        schema = extract_schema_from_sqlite(conn)
    else:
        # Fallback for unsupported database types
        schema = {"tables": {}}
    
    # Close connection
    database_connection.close()
    
    # Cache the schema
    with open(cache_file, 'w') as f:
        json.dump(schema, f, indent=2)
    
    return schema