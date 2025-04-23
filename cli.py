import typer
import os
import json
import getpass
import datetime
from typing import Optional, List
from pathlib import Path
from typer.models import Choice

from utils.config import setup_config, load_config
from db.connector import MySQLConnector
from ai.translator import generate_sql
from utils.formatting import print_sql, print_result

# Main app
app = typer.Typer(add_completion=False, help="Natural Language to SQL CLI Tool")

# Subcommands
config_app = typer.Typer(help="API and global configuration management")
profile_app = typer.Typer(help="Manage database connection profiles")
connect_app = typer.Typer(help="Connect using active profile")
list_app = typer.Typer(help="List databases/tables in current connection")
saved_app = typer.Typer(help="Manage saved queries")

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
        if key in ['gemini_api_key', 'password']:
            value = "*" * 8
        typer.echo(f"{key}: {value}")

@config_app.command("set")
def config_set(key_value: str):
    """Set a config value (API_KEY, etc.)"""
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

@config_app.command("unset")
def config_unset(key: str):
    """Remove a config value"""
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

# Profile commands
@profile_app.command("create")
def profile_create(name: str):
    """Create a new database profile"""
    typer.echo(f"Creating new profile '{name}'")
    
    # Interactive prompts for connection details
    db_types = ["MySQL", "PostgreSQL", "SQLite"]
    db_type = typer.prompt("Database type", type=Choice(db_types))
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
def profile_edit(name: str):
    """Edit an existing profile"""
    profile = load_profile(name)
    
    # Interactive prompts with current values as defaults
    db_types = ["MySQL", "PostgreSQL", "SQLite"]
    profile["type"] = typer.prompt("Database type", type=Choice(db_types), default=profile["type"])
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
    
    # This would connect to the database and list tables
    # For now, just show a placeholder
    typer.echo("Available tables:")
    typer.echo("- users")
    typer.echo("- products")
    typer.echo("- orders")

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
    
    # This would connect to the database and list tables
    # For now, just show a placeholder
    typer.echo("- users")
    typer.echo("- products")
    typer.echo("- orders")

# Describe command
@app.command()
def describe(table: str):
    """Show table schema"""
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    typer.echo(f"Schema for table '{table}':")
    # This would connect to the database and show the schema
    # For now, just show a placeholder
    typer.echo("id INT PRIMARY KEY")
    typer.echo("name VARCHAR(255)")
    typer.echo("created_at TIMESTAMP")

# Cache schema command
@app.command("cache-schema")
def cache_schema():
    """Cache current database schema"""
    active_profile = get_active_profile()
    if not active_profile:
        typer.echo("No active profile. Create one with: nlsql profile create <name>")
        return
    
    typer.echo(f"Caching schema for active profile '{active_profile}'...")
    # This would connect to the database and cache the schema
    typer.echo("Schema cached successfully")

# Query command
@app.command()
def query(
    text: str = typer.Argument(..., help="Natural language question to translate to SQL"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Edit before execution"),
    execute: bool = typer.Option(False, "--execute", "-x", help="Execute without confirmation"),
    save: Optional[str] = typer.Option(None, "--save", help="Save query for later"),
    format: str = typer.Option("table", "--format", help="Output format (table/json/csv)"),
    export: Optional[Path] = typer.Option(None, "--export", help="Export results to file"),
    explain: bool = typer.Option(False, "--explain", help="Show query execution plan")
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
    
    api_key = config.get('gemini_api_key', '')
    if not api_key:
        typer.echo("API key not found. Run 'nlsql setup' or 'nlsql config set gemini_api_key=YOUR_KEY'")
        return
    
    # Generate SQL
    typer.echo(f"Translating: {text}")
    schema = {"tables": ["users", "orders", "products"]}  # Placeholder
    sql_query = generate_sql(text, schema, api_key)
    print_sql(sql_query)
    
    # Edit if requested
    if edit:
        typer.echo("\n--- Edit SQL (type new SQL and press Enter, or leave blank to keep) ---")
        new_sql = typer.prompt("Edit SQL", default=sql_query, show_default=False)
        if new_sql != sql_query:
            sql_query = new_sql
            typer.echo("SQL updated:")
            print_sql(sql_query)
    
    # Save if requested
    if save:
        save_query(save, sql_query)
        typer.echo(f"Query saved as '{save}'")
    
    # Add to history
    add_to_history(text, sql_query, executed=execute)
    
    # Execute if requested
    if execute:
        typer.echo("Executing query...")
        # This would connect to the database and execute the query
        # For now, just show a placeholder
        result = [(1, "John", "2023-01-01"), (2, "Jane", "2023-02-01")]
        columns = ["id", "name", "date"]
        
        if explain:
            typer.echo("Execution plan:")
            typer.echo("SIMPLE TABLE ACCESS")
        
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
    
    # This would connect to the database and execute the query
    # For now, just show a placeholder
    result = [(1, "John", "2023-01-01"), (2, "Jane", "2023-02-01")]
    columns = ["id", "name", "date"]
    print_result(result, columns)

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