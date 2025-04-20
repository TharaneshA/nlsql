import os
import json

def extract_schema_from_db(connection):
    """Extract schema from the MySQL database."""
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

def get_schema(database_connection, force_refresh=False):
    """Get database schema with caching."""
    cache_dir = os.path.join(os.path.expanduser("~"), ".nlsql")
    os.makedirs(cache_dir, exist_ok=True)
    db_name = database_connection.config.get('database', 'default')
    cache_file = os.path.join(cache_dir, f"{db_name}_schema.json")
    if os.path.exists(cache_file) and not force_refresh:
        with open(cache_file, 'r') as f:
            return json.load(f)
    conn = database_connection.connect()
    schema = extract_schema_from_db(conn)
    conn.close()
    with open(cache_file, 'w') as f:
        json.dump(schema, f)
    return schema