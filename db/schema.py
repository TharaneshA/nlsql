import os
import json
from pathlib import Path
from datetime import datetime, date

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

def get_schema(database_connection, force_refresh=False, include_sample_data=True):
    """Get database schema with caching. Optionally includes sample data."""
    # Include sample data flag controls whether to fetch sample rows from each table
    # Create cache directory
    cache_dir = Path.home() / ".nlsql" / "schema_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate cache key based on connection details
    profile = database_connection.profile
    cache_key = f"{profile.get('type', 'unknown')}_{profile.get('host', '')}_{profile.get('database', '')}"
    cache_file = cache_dir / f"{cache_key}.json"
    
    # Use cached schema if available and not forcing refresh
    if cache_file.exists() and not force_refresh:
        try:
            with open(cache_file, 'r') as f:
                cached_schema = json.load(f)
                # Add sample data if requested and not already in cache
                if include_sample_data and "sample_data" not in cached_schema:
                    cached_schema["sample_data"] = extract_sample_data(database_connection)
                return cached_schema
        except (json.JSONDecodeError, IOError):
            # If cache is corrupted, continue to regenerate
            pass
    
    # Extract schema based on database type
    db_type = profile.get('type', 'MySQL')
    if db_type == "MySQL":
        schema = extract_schema_from_mysql(database_connection.connection)
    elif db_type == "PostgreSQL":
        schema = extract_schema_from_postgresql(database_connection.connection)
    elif db_type == "SQLite":
        schema = extract_schema_from_sqlite(database_connection.connection)
    else:
        schema = {"tables": {}}
    
    # Add sample data if requested
    if include_sample_data:
        schema["sample_data"] = extract_sample_data(database_connection)
    
    # Cache the schema
    try:
        with open(cache_file, 'w') as f:
            json.dump(schema, f, indent=2)
    except IOError:
        pass  # Silently fail if we can't write to cache
    
    return schema

def extract_sample_data(database_connection, max_tables=10, max_rows=5):
    """Extract sample data from tables to provide context for AI."""
    import json
    from datetime import datetime, date
    
    sample_data = {}
    try:
        cursor = database_connection.connection.cursor()
        
        # Get list of tables
        db_type = database_connection.profile.get('type', 'MySQL')
        if db_type == "MySQL":
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == "PostgreSQL":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == "SQLite":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            tables = []
        
        # Limit number of tables to avoid excessive data
        tables = tables[:max_tables]
        
        for table in tables:
            try:
                # Escape table name according to database type
                if db_type == "MySQL":
                    table_sql = f"`{table}`"
                elif db_type == "PostgreSQL":
                    table_sql = f'"{table}"'
                else:  # SQLite
                    table_sql = f'"{table}"'
                
                # Get sample rows
                cursor.execute(f"SELECT * FROM {table_sql} LIMIT {max_rows}")
                rows = cursor.fetchall()
                
                # Get column names
                if db_type == "MySQL":
                    columns = [desc[0] for desc in cursor.description]
                elif db_type == "PostgreSQL":
                    columns = [desc[0] for desc in cursor.description]
                else:  # SQLite
                    columns = [desc[0] for desc in cursor.description]
                
                # Format as list of dictionaries
                formatted_rows = []
                for row in rows:
                    formatted_row = {}
                    for i, col in enumerate(columns):
                        # Convert non-serializable types to strings
                        value = row[i]
                        if isinstance(value, (datetime, date)):
                            value = value.isoformat()
                        formatted_row[col] = value
                    formatted_rows.append(formatted_row)
                
                sample_data[table] = {
                    "columns": columns,
                    "rows": formatted_rows
                }
            except Exception as e:
                # Skip tables with errors
                continue
        
        cursor.close()
    except Exception as e:
        # Return empty dict if any error occurs
        pass
    
    return sample_data

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