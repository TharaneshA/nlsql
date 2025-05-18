import typer
import os
import json
import getpass
import datetime
from typing import Optional, List
from pathlib import Path
import typer

from utils.config import setup_config, load_config
from db.connector import MySQLConnector
from ai.translator import generate_sql
from utils.formatting import print_sql, print_result
import enum
from InquirerPy import inquirer


class DatabaseType(enum.Enum):
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL"
    SQLITE = "SQLite"

# Main app
app = typer.Typer(add_completion=False, help="Natural Language to SQL CLI Tool - Convert English to SQL queries")

# Subcommands
config_app = typer.Typer(help="Manage API keys and global settings")
profile_app = typer.Typer(help="Create and manage database connection profiles")
connect_app = typer.Typer(help="Connect to a database using the active profile")
list_app = typer.Typer(help="List available databases and tables in current connection")
saved_app = typer.Typer(help="Save and manage frequently used queries")

# Register subcommands
app.add_typer(config_app, name="config")
app.add_typer(profile_app, name="profile")
app.add_typer(connect_app, name="connect")
app.add_typer(list_app, name="list")
app.add_typer(saved_app, name="saved")

# Constants
CONFIG_DIR = Path.home() / ".nlsql"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_DIR = CONFIG_DIR / "profiles"
SAVED_QUERIES_DIR = CONFIG_DIR / "saved_queries"
HISTORY_FILE = CONFIG_DIR / "history.json"
ACTIVE_PROFILE_FILE = CONFIG_DIR / "active_profile.txt"

# Ensure directories exist
CONFIG_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
SAVED_QUERIES_DIR.mkdir(exist_ok=True)

# Helper functions
def get_active_profile():
    """Get the name of the active profile"""
    if not ACTIVE_PROFILE_FILE.exists():
        return None
    return ACTIVE_PROFILE_FILE.read_text().strip()

def set_active_profile(profile_name):
    """Set the active profile"""
    ACTIVE_PROFILE_FILE.write_text(profile_name)

def load_profile(profile_name):
    """Load a profile by name"""
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    if not profile_path.exists():
        typer.echo(f"Profile '{profile_name}' not found")
        raise typer.Exit(1)
    with open(profile_path, 'r') as f:
        return json.load(f)

def save_profile(profile_name, profile_data):
    """Save a profile"""
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    with open(profile_path, 'w') as f:
        json.dump(profile_data, f, indent=2)

def save_query(name, query):
    """Save a query for later use"""
    query_path = SAVED_QUERIES_DIR / f"{name}.sql"
    with open(query_path, 'w') as f:
        f.write(query)

def load_query(name):
    """Load a saved query"""
    query_path = SAVED_QUERIES_DIR / f"{name}.sql"
    if not query_path.exists():
        typer.echo(f"Query '{name}' not found")
        raise typer.Exit(1)
    with open(query_path, 'r') as f:
        return f.read()

def add_to_history(question, sql_query, executed=False):
    """Add a query to history"""
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "question": question,
        "sql": sql_query,
        "executed": executed
    })
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

# Setup command
@app.command()
def setup():
    """Initial one-time setup (API key & global settings)"""
    typer.echo("Welcome to NLSQL! Let's set up your environment.")
    config = setup_config()
    
    # Save config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    typer.echo("\nConfiguration completed successfully!")
    typer.echo("\nNext, create a database profile with: nlsql profile create <name>")

# Config commands
@config_app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context):
    """Show available config commands when no subcommand is provided"""
    if ctx.invoked_subcommand is not None:
        return
    
    # Import InquirerPy for interactive selection
    try:
        from InquirerPy import inquirer
    except ImportError:
        typer.echo("Installing required dependency for interactive selection...")
        import subprocess
        subprocess.check_call(["pip", "install", "InquirerPy"])
        from InquirerPy import inquirer
    
    # Show available config commands
    action = inquirer.select(
        message="Select config action:",
        choices=["list", "set", "unset"],
        default="list"
    ).execute()
    
    if action == "list":
        config_list()
    elif action == "set":
        config_set_interactive()
    elif action == "unset":
        config_unset_interactive()

@config_app.command("list")
def config_list():
    """List all config settings"""
    if not CONFIG_FILE.exists():
        typer.echo("No configuration found. Run 'nlsql setup' first.")
        return
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    typer.echo("Current configuration:")
    for key, value in config.items():
        # Mask sensitive values
        if key in ['api_key', 'password'] or key.endswith('_api_key'):
            value = "*" * 8
        typer.echo(f"{key}: {value}")

@config_app.command("set")
def config_set(key_value: Optional[str] = None):
    """Set a config value (API_KEY, etc.)"""
    if key_value is None:
        config_set_interactive()
        return
    
    if "=" not in key_value:
        typer.echo("Invalid format. Use KEY=VALUE")
        return
    
    key, value = key_value.split("=", 1)
    key = key.strip()
    value = value.strip()
    
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    config[key] = value
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"Config value '{key}' set successfully")

def config_set_interactive():
    """Interactive config value setting"""
    from ai.providers import AIProvider
    
    # Import InquirerPy for interactive selection
    try:
        from InquirerPy import inquirer
    except ImportError:
        typer.echo("Installing required dependency for interactive selection...")
        import subprocess
        subprocess.check_call(["pip", "install", "InquirerPy"])
        from InquirerPy import inquirer
    
    # Select AI provider
    provider_choices = [p.value for p in AIProvider]
    provider = inquirer.select(
        message="Select AI provider:",
        choices=provider_choices,
        default=provider_choices[0]
    ).execute()
    
    # Get API key
    while True:
        api_key = typer.prompt(f'Enter your {provider.title()} API key', hide_input=True).strip()
        if len(api_key) >= 20:
            break
        typer.echo('Invalid key - must be at least 20 characters')
    
    # Save to config
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    config[f"{provider}_api_key"] = api_key
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"API key for {provider} set successfully")

@config_app.command("unset")
def config_unset(key: Optional[str] = None):
    """Remove a config value"""
    if key is None:
        config_unset_interactive()
        return
    
    if not CONFIG_FILE.exists():
        typer.echo("No configuration found")
        return
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    if key in config:
        del config[key]
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        typer.echo(f"Config value '{key}' removed successfully")
    else:
        typer.echo(f"Config value '{key}' not found")

def config_unset_interactive():
    """Interactive config value removal"""
    if not CONFIG_FILE.exists():
        typer.echo("No configuration found")
        return
    
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    if not config:
        typer.echo("No configuration values to remove")
        return
    
    # Import InquirerPy for interactive selection
    try:
        from InquirerPy import inquirer
    except ImportError:
        typer.echo("Installing required dependency for interactive selection...")
        import subprocess
        subprocess.check_call(["pip", "install", "InquirerPy"])
        from InquirerPy import inquirer
    
    # Select key to remove
    key = inquirer.select(
        message="Select config value to remove:",
        choices=list(config.keys()),
    ).execute()
    
    del config[key]
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    typer.echo(f"Config value '{key}' removed successfully")

# Profile commands
@profile_app.command("create")
def profile_create(name: str):
    """Create a new database profile"""
    typer.echo(f"Creating new profile '{name}'")
    
    # Import InquirerPy for interactive selection
    try:
        from InquirerPy import inquirer
        from InquirerPy.base.control import Choice
    except ImportError:
        typer.echo("Installing required dependency for interactive selection...")
        import subprocess
        subprocess.check_call(["pip", "install", "InquirerPy"])
        from InquirerPy import inquirer
        from InquirerPy.base.control import Choice
    
    # Interactive prompts for connection details
    db_types = [DatabaseType.MYSQL.value, DatabaseType.POSTGRESQL.value, DatabaseType.SQLITE.value]
    
    # Use InquirerPy for interactive database type selection with arrow keys
    db_type = inquirer.select(
        message="Select database type:",
        choices=db_types,
        default=db_types[0]
    ).execute()
    
    host = typer.prompt("Host", default="localhost")
    port = typer.prompt("Port", default="3306" if db_type == "MySQL" else "5432")
    database = typer.prompt("Database name")
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)
    connection_options = typer.prompt("Connection options", default="")
    
    profile = {
        "type": db_type,
        "host": host,
        "port": port,
        "database": database,
        "username": username,
        "password": password,
        "options": connection_options
    }
    
    save_profile(name, profile)
    typer.echo(f"Profile '{name}' created successfully!")
    
    # Set as active if it's the first profile
    if not get_active_profile():
        set_active_profile(name)
        typer.echo(f"Set '{name}' as the active profile")

@profile_app.command("list")
def profile_list():
    """List all saved profiles"""
    profiles = [p.stem for p in PROFILES_DIR.glob("*.json")]
    active = get_active_profile()
    
    if not profiles:
        typer.echo("No profiles found. Create one with: nlsql profile create <name>")
        return
    
    typer.echo("Available profiles:")
    for profile in profiles:
        prefix = "* " if profile == active else "  "
        profile_data = load_profile(profile)
        typer.echo(f"{prefix}{profile} ({profile_data['type']})")

@profile_app.command("use")
def profile_use(name: str):
    """Switch to a specific profile"""
    profile_path = PROFILES_DIR / f"{name}.json"
    if not profile_path.exists():
        typer.echo(f"Profile '{name}' not found")
        return
    
    set_active_profile(name)
    typer.echo(f"Switched to profile '{name}'")

@profile_app.command("edit")
@profile_app.command("edit")
def profile_edit(name: str):
    """Edit an existing profile"""
    profile = load_profile(name)
    
    # Interactive prompts with current values as defaults
    profile["type"] = typer.prompt(
        "Database type", 
        type=DatabaseType, 
        default=DatabaseType(profile["type"])
    ).value
    profile["host"] = typer.prompt("Host", default=profile["host"])
    profile["port"] = typer.prompt("Port", default=profile["port"])
    profile["database"] = typer.prompt("Database name", default=profile["database"])
    profile["username"] = typer.prompt("Username", default=profile["username"])
    new_password = typer.prompt("Password (leave empty to keep current)", default="", hide_input=True)
    if new_password:
        profile["password"] = new_password
    profile["options"] = typer.prompt("Connection options", default=profile.get("options", ""))

    save_profile(name, profile)
    typer.echo(f"Profile '{name}' updated successfully!")


@profile_app.command("delete")
def profile_delete(name: str):
    """Delete a profile"""
    profile_path = PROFILES_DIR / f"{name}.json"
    if not profile_path.exists():
        typer.echo(f"Profile '{name}' not found")
        return
    
    confirm = typer.confirm(f"Are you sure you want to delete profile '{name}'?")
    if not confirm:
        return
    
    profile_path.unlink()
    typer.echo(f"Profile '{name}' deleted successfully")
    
    # If this was the active profile, clear it
    if get_active_profile() == name:
        ACTIVE_PROFILE_FILE.unlink(missing_ok=True)
        typer.echo("Active profile cleared")

# Connect command
@connect_app.callback(invoke_without_command=True)
def connect(ctx: typer.Context, new: bool = typer.Option(False, "--new", help="Force new connection dialog")):
    """Connect using active profile"""
    if ctx.invoked_subcommand is not None:
        return
    
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    profile = load_profile(active_profile)
    typer.echo(f"Connected to {profile['type']} database '{profile['database']}' as '{profile['username']}'")

# List commands
@list_app.callback(invoke_without_command=True)
def list_items(ctx: typer.Context, databases: bool = typer.Option(False, "--databases", help="Show only databases")):
    """List databases/tables in current connection"""
    if ctx.invoked_subcommand is not None:
        return
    
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    profile = load_profile(active_profile)
    typer.echo(f"Listing from {profile['type']} database '{profile['database']}'")
    
    try:
        # Connect to the database and list tables
        from db.connector import DBConnector
        connector = DBConnector.create_connector(profile)
        connector.connect()
        
        if databases:
            # Show available databases
            if profile['type'] == "MySQL":
                result, columns = connector.execute_query("SHOW DATABASES")
                typer.echo("Available databases:")
                for row in result:
                    typer.echo(f"- {row[0]}")
            elif profile['type'] == "PostgreSQL":
                result, columns = connector.execute_query("SELECT datname FROM pg_database WHERE datistemplate = false")
                typer.echo("Available databases:")
                for row in result:
                    typer.echo(f"- {row[0]}")
            elif profile['type'] == "SQLite":
                typer.echo("SQLite does not support multiple databases in the same file.")
        else:
            # Show tables in current database
            if profile['type'] == "MySQL":
                result, columns = connector.execute_query("SHOW TABLES")
                typer.echo("Available tables:")
                for row in result:
                    typer.echo(f"- {row[0]}")
            elif profile['type'] == "PostgreSQL":
                result, columns = connector.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                typer.echo("Available tables:")
                for row in result:
                    typer.echo(f"- {row[0]}")
            elif profile['type'] == "SQLite":
                result, columns = connector.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                typer.echo("Available tables:")
                for row in result:
                    typer.echo(f"- {row[0]}")
        
        connector.close()
    except Exception as e:
        typer.echo(f"Error connecting to database: {str(e)}")
        typer.echo("Please check your connection profile and try again.")
        return

@list_app.command("tables")
def list_tables(db: Optional[str] = None):
    """Show tables (in specific DB if provided)"""
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    profile = load_profile(active_profile)
    db_name = db or profile['database']
    typer.echo(f"Tables in {db_name}:")
    
    try:
        # Connect to the database and list tables
        from db.connector import DBConnector
        connector = DBConnector.create_connector(profile)
        connector.connect()
        
        # If a specific database was provided, use it
        if db and profile['type'] in ["MySQL", "PostgreSQL"]:
            if profile['type'] == "MySQL":
                connector.execute_query(f"USE {db}")
            elif profile['type'] == "PostgreSQL":
                # Close current connection and reconnect to the specified database
                connector.close()
                profile_copy = profile.copy()
                profile_copy['database'] = db
                connector = DBConnector.create_connector(profile_copy)
                connector.connect()
        
        # Get tables based on database type
        if profile['type'] == "MySQL":
            result, columns = connector.execute_query("SHOW TABLES")
        elif profile['type'] == "PostgreSQL":
            result, columns = connector.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        elif profile['type'] == "SQLite":
            result, columns = connector.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        
        if not result:
            typer.echo("No tables found in this database.")
        else:
            for row in result:
                typer.echo(f"- {row[0]}")
        
        connector.close()
    except Exception as e:
        typer.echo(f"Error listing tables: {str(e)}")
        typer.echo("Please check your connection profile and try again.")
        return

# Describe command
@app.command()
def describe(table: str):
    """Show table schema"""
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    profile = load_profile(active_profile)
    typer.echo(f"Schema for table '{table}':")
    
    try:
        # Connect to the database and get table schema
        from db.connector import DBConnector
        connector = DBConnector.create_connector(profile)
        
        # Get schema based on database type
        if profile['type'] == "MySQL":
            result, columns = connector.execute_query(f"DESCRIBE `{table}`")
            for row in result:
                field = row[0]
                type_info = row[1]
                null = "NULL" if row[2] == "YES" else "NOT NULL"
                key = row[3] if row[3] else ""
                default = f"DEFAULT {row[4]}" if row[4] is not None else ""
                extra = row[5] if row[5] else ""
                typer.echo(f"{field} {type_info} {null} {key} {default} {extra}".strip())
        elif profile['type'] == "PostgreSQL":
            result, columns = connector.execute_query(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            for row in result:
                field = row[0]
                type_info = row[1]
                null = "NULL" if row[2] == "YES" else "NOT NULL"
                default = f"DEFAULT {row[3]}" if row[3] is not None else ""
                typer.echo(f"{field} {type_info} {null} {default}".strip())
        elif profile['type'] == "SQLite":
            result, columns = connector.execute_query(f"PRAGMA table_info({table})")
            for row in result:
                cid = row[0]
                field = row[1]
                type_info = row[2]
                not_null = "NOT NULL" if row[3] == 1 else "NULL"
                default = f"DEFAULT {row[4]}" if row[4] is not None else ""
                pk = "PRIMARY KEY" if row[5] == 1 else ""
                typer.echo(f"{field} {type_info} {not_null} {default} {pk}".strip())
        
        connector.close()
    except Exception as e:
        typer.echo(f"Error describing table: {str(e)}")
        typer.echo("Please check your connection profile and try again.")

# Cache schema command
@app.command("cache-schema")
def cache_schema():
    """Cache current database schema"""
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    typer.echo(f"Caching schema for active profile '{active_profile}'...")
    
    try:
        # Connect to the database and cache the schema
        from db.connector import DBConnector
        from db.schema import get_schema
        
        profile = load_profile(active_profile)
        connector = DBConnector.create_connector(profile)
        connector.connect()
        
        # Get and cache the schema with sample data
        schema = get_schema(connector, force_refresh=True, include_sample_data=True)
        
        # Save the schema to a cache file
        cache_dir = CONFIG_DIR / "schema_cache"
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / f"{active_profile}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        connector.close()
        typer.echo(f"Schema cached successfully to {cache_file}")
    except Exception as e:
        typer.echo(f"Error caching schema: {str(e)}")
        typer.echo("Please check your connection profile and try again.")

# Query command
@app.command(name="query", help="Generate SQL from natural language and optionally execute it")
@app.command(name="q", hidden=True)  # Short alias
def query(
    text: str = typer.Argument(..., help="Your question in plain English (e.g. 'show recent orders')"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open the generated SQL in editor for modifications"),
    execute: bool = typer.Option(False, "--execute", "-x", help="Execute the query immediately without confirmation"),
    save: Optional[str] = typer.Option(None, "--save", "-s", help="Save the query with a name for later use"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table, json, or csv"),
    export: Optional[Path] = typer.Option(None, "--export", help="Save query results to a file"),
    explain: bool = typer.Option(False, "--explain", help="Show the database execution plan for the query"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit the number of results returned")
):
    """Generate and optionally run query"""
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    profile = load_profile(active_profile)
    
    # Load config for API key
    config = {}
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    # Get AI provider configuration
    provider_config = None
    if 'ai_provider' in config:
        from ai.providers import ProviderConfig
        provider_config = ProviderConfig.from_dict(config['ai_provider'])
    
    if not provider_config or not provider_config.is_configured:
        typer.echo("AI provider not configured. Run 'nlsql setup' or configure your AI provider.")
        return
    
    # Generate SQL
    typer.echo(f"Translating: {text}")
    
    # Get actual schema from database if connected
    schema = None
    try:
        from db.connector import DBConnector
        connector = DBConnector.create_connector(profile)
        connector.connect()
        schema = connector.get_schema()
        connector.close()
    except Exception as e:
        typer.echo(f"Warning: Could not fetch schema from database: {str(e)}")
        # Fallback to placeholder schema
        schema = {"tables": ["users", "orders", "products"]}
    
    # Get conversation history for context
    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # Generate SQL with enhanced context
    sql_query = generate_sql(text, schema, provider_config, history=history)
    
    # Clean up SQL query by removing markdown formatting if present
    if sql_query.startswith('```'):
        # Extract SQL from markdown code block
        parts = sql_query.split('```')
        if len(parts) >= 3:  # Has opening and closing markers
            sql_content = parts[1]
            # Remove language identifier if present
            if sql_content.startswith('sql'):
                sql_query = sql_content[3:].strip()
            else:
                sql_query = sql_content.strip()
        else:  # Only has opening marker
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    # Ensure no markdown markers remain
    sql_query = sql_query.replace('```', '').strip()
    
    print_sql(sql_query)
    
    # Edit if requested
    if edit:
        typer.echo("\n--- Edit SQL (press Enter to execute, Ctrl+C to cancel) ---")
        # Pre-populate the prompt with the generated SQL
        try:
            new_sql = typer.prompt("", default=sql_query, show_default=True)
            if new_sql != sql_query:
                sql_query = new_sql
                typer.echo("\nSQL updated:")
                print_sql(sql_query)
        except KeyboardInterrupt:
            typer.echo("\nEdit cancelled")
            raise typer.Exit()
    
    # Save if requested
    if save:
        save_query(save, sql_query)
        typer.echo(f"Query saved as '{save}'")
    
    # Add to history
    add_to_history(text, sql_query, executed=execute)
    
    # Execute if requested
    if execute:
        typer.echo("Executing query...")
        try:
            # Connect to the database using the active profile
            from db.connector import DBConnector
            connector = DBConnector.create_connector(profile)
            connector.connect()
            
            # Add EXPLAIN if requested
            query_to_execute = f"EXPLAIN {sql_query}" if explain else sql_query
            
            # Add LIMIT if specified
            if limit is not None and "LIMIT" not in sql_query.upper():
                query_to_execute = f"{query_to_execute} LIMIT {limit}"
            
            # Execute the query and get actual results
            if explain:
                typer.echo("Execution plan:")
                result, columns = connector.execute_query(query_to_execute)
                print_result(result, columns, output_format=format)
                # Execute the actual query after showing the plan
                query_to_execute = sql_query
                if limit is not None and "LIMIT" not in sql_query.upper():
                    query_to_execute = f"{query_to_execute} LIMIT {limit}"
                result, columns = connector.execute_query(query_to_execute)
            else:
                result, columns = connector.execute_query(query_to_execute)
            
            connector.close()
        except Exception as e:
            typer.echo(f"Error executing query: {str(e)}")
            raise typer.Exit(1)
        
        if export:
            typer.echo(f"Exporting results to {export}")
            # This would export the results to a file
        else:
            print_result(result, columns, output_format=format)

# Run command
@app.command()
def run(name: str):
    """Run a saved query"""
    sql_query = load_query(name)
    typer.echo(f"Running saved query '{name}':")
    print_sql(sql_query)
    
    try:
        # Connect to the database and execute the query
        from db.connector import DBConnector
        
        active_profile = get_active_profile()
        if not active_profile:
            typer.echo("No active profile. Create one with: nlsql profile create <name>")
            return
        
        profile = load_profile(active_profile)
        connector = DBConnector.create_connector(profile)
        connector.connect()
        
        # Execute the query
        result, columns = connector.execute_query(sql_query)
        print_result(result, columns)
        
        connector.close()
    except Exception as e:
        typer.echo(f"Error executing query: {str(e)}")
        raise typer.Exit(1)

# Saved queries commands
@saved_app.command("list")
def saved_list():
    """List saved queries"""
    queries = [p.stem for p in SAVED_QUERIES_DIR.glob("*.sql")]
    
    if not queries:
        typer.echo("No saved queries found")
        return
    
    typer.echo("Saved queries:")
    for query in queries:
        typer.echo(f"- {query}")

@saved_app.command("delete")
def saved_delete(name: str):
    """Delete a saved query"""
    query_path = SAVED_QUERIES_DIR / f"{name}.sql"
    if not query_path.exists():
        typer.echo(f"Query '{name}' not found")
        return
    
    confirm = typer.confirm(f"Are you sure you want to delete query '{name}'?")
    if not confirm:
        return
    
    query_path.unlink()
    typer.echo(f"Query '{name}' deleted successfully")

# History command
@app.command()
def history():
    """View query history"""
    if not HISTORY_FILE.exists():
        typer.echo("No query history found")
        return
    
    with open(HISTORY_FILE, 'r') as f:
        history_data = json.load(f)
    
    if not history_data:
        typer.echo("No query history found")
        return
    
    typer.echo("Query history:")
    for i, entry in enumerate(history_data[-10:], 1):  # Show last 10 entries
        timestamp = entry["timestamp"].split("T")[0]  # Just show the date
        executed = "(executed)" if entry["executed"] else ""
        typer.echo(f"{i}. [{timestamp}] {executed} {entry['question']}")

# Version command
@app.command()
def version():
    """Show version info"""
    typer.echo("NLSQL v0.1.0")
    typer.echo("Natural Language to SQL CLI Tool")
    typer.echo("https://github.com/TharaneshA/nlsql")

# Setup test database command
@app.command("setup-test-db")
def setup_test_db(
    users: int = typer.Option(50, help="Number of users to generate"),
    products: int = typer.Option(100, help="Number of products to generate"),
    orders: int = typer.Option(200, help="Number of orders to generate"),
    db_path: Optional[str] = typer.Option(None, help="Custom path for the test database")
):
    """Set up a test SQLite database with sample data for demonstration"""
    try:
        from scripts.setup_test_db import setup
        setup(db_path=db_path, users=users, products=products, orders=orders)
    except ImportError as e:
        typer.echo(f"Error: Could not import setup script: {str(e)}")
        typer.echo("Make sure the scripts directory is in your Python path.")

# Main entry point
@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """NLSQL - Natural Language to SQL CLI Tool"""
    # Create necessary directories
    CONFIG_DIR.mkdir(exist_ok=True)
    PROFILES_DIR.mkdir(exist_ok=True)
    SAVED_QUERIES_DIR.mkdir(exist_ok=True)
    
    # If no command is provided, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())

if __name__ == "__main__":
    app()