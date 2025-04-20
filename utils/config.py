import os
import json

def setup_config():
    """Interactive configuration setup for first-time users"""
    config = {}
    print("\n=== Gemini API Configuration ===")
    
    # Collect and validate API key
    while True:
        api_key = input('Enter your Gemini API key: ').strip()
        if len(api_key) >= 20:
            config['gemini_api_key'] = api_key
            break
        print('Invalid key - must be at least 20 characters')
    
    # Existing database setup
    print("\n=== Database Configuration ===")
    config['host'] = input('Database host [localhost]: ') or 'localhost'
    config['user'] = input('Database user [root]: ') or 'root'
    config['password'] = input('Database password: ')
    config['database'] = input('Database name: ')
    
    return config


def load_config(config_path=None):
    """Load configuration from a JSON file or environment variables."""
    config = {}
    # Load from config file if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    # Override with environment variables if present
    config['host'] = os.environ.get('MYSQL_HOST', config.get('host', 'localhost'))
    config['user'] = os.environ.get('MYSQL_USER', config.get('user', 'root'))
    config['password'] = os.environ.get('MYSQL_PASSWORD', config.get('password', ''))
    config['database'] = os.environ.get('MYSQL_DATABASE', config.get('database', ''))
    config['gemini_api_key'] = os.environ.get('GEMINI_API_KEY', config.get('gemini_api_key', ''))
    return config