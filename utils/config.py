import os
import json
import typer
from pathlib import Path
from typing import Optional, List, Literal

# Constants
CONFIG_DIR = Path.home() / ".nlsql"
CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_DIR = CONFIG_DIR / "profiles"

# Ensure directories exist
CONFIG_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)

def setup_config():
    """Interactive configuration setup for first-time users"""
    config = {}
    typer.echo("\n=== Gemini API Configuration ===")
    
    # Collect and validate API key
    while True:
        api_key = typer.prompt('Enter your Gemini API key').strip()
        if len(api_key) >= 20:
            config['gemini_api_key'] = api_key
            break
        typer.echo('Invalid key - must be at least 20 characters')
    
    # Ask if user wants to set up a database profile now
    if typer.confirm("Do you want to set up a database profile now?", default=True):
        profile_name = typer.prompt("Profile name", default="default")
        
        # Database type selection using Literal
        db_type = typer.prompt("Database type", type=Literal["MySQL", "PostgreSQL", "SQLite"])
        
        # Database connection details
        config['db_type'] = db_type
        config['host'] = typer.prompt('Database host', default='localhost')
        config['port'] = typer.prompt('Database port', default='3306' if db_type == "MySQL" else "5432")
        config['user'] = typer.prompt('Database user', default='root')
        config['password'] = typer.prompt('Database password', hide_input=True)
        config['database'] = typer.prompt('Database name')
        
        # Save as profile
        profile = {
            "type": db_type,
            "host": config['host'],
            "port": config['port'],
            "username": config['user'],
            "password": config['password'],
            "database": config['database'],
            "options": ""
        }
        
        save_profile(profile_name, profile)
        set_active_profile(profile_name)
    
    return config


def load_config(config_path=None):
    """Load configuration from a JSON file or environment variables."""
    if config_path is None:
        config_path = CONFIG_FILE
    
    config = {}
    # Load from config file if provided
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Override with environment variables if present
    config['gemini_api_key'] = os.environ.get('GEMINI_API_KEY', config.get('gemini_api_key', ''))
    
    return config

def get_active_profile():
    """Get the name of the active profile"""
    active_profile_file = CONFIG_DIR / "active_profile.txt"
    if not active_profile_file.exists():
        return None
    return active_profile_file.read_text().strip()

def set_active_profile(profile_name):
    """Set the active profile"""
    active_profile_file = CONFIG_DIR / "active_profile.txt"
    active_profile_file.write_text(profile_name)

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
    PROFILES_DIR.mkdir(exist_ok=True)
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    with open(profile_path, 'w') as f:
        json.dump(profile_data, f, indent=2)

def list_profiles():
    """List all available profiles"""
    PROFILES_DIR.mkdir(exist_ok=True)
    return [p.stem for p in PROFILES_DIR.glob("*.json")]

def delete_profile(profile_name):
    """Delete a profile"""
    profile_path = PROFILES_DIR / f"{profile_name}.json"
    if not profile_path.exists():
        return False
    profile_path.unlink()
    
    # If this was the active profile, clear it
    active_profile = get_active_profile()
    if active_profile == profile_name:
        active_profile_file = CONFIG_DIR / "active_profile.txt"
        if active_profile_file.exists():
            active_profile_file.unlink()
    
    return True
