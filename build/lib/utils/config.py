import os
import json

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