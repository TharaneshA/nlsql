# nlsql

A natural language SQL interface for MySQL databases.

## Requirements
- Python 3.7+
- MySQL server
- Required Python packages (see below)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/TharaneshA/nlsql.git
   cd nlsql
   ```
2. Install dependencies:
   ```sh
   pip install mysql-connector-python
   ```
   Or, if you have a `requirements.txt` file:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

Edit your database configuration in your code or environment variables as needed. Example config:
```python
config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'yourdatabase'
}
```

# NLSQL - Natural Language to SQL CLI Tool

NLSQL is a command-line tool that translates natural language questions into SQL queries using Google's Gemini AI. It connects to your MySQL database, extracts the schema, and generates appropriate SQL based on your questions.

## Installation

1. Clone this repository
2. Install dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

You can configure NLSQL in two ways:

1. Using a config file (recommended):
   - Copy `config.json.example` to `config.json`
   - Edit the file with your MySQL credentials and Gemini API key

2. Using environment variables:
   - `MYSQL_HOST` - MySQL server hostname (default: localhost)
   - `MYSQL_USER` - MySQL username (default: root)
   - `MYSQL_PASSWORD` - MySQL password
   - `MYSQL_DATABASE` - MySQL database name
   - `GEMINI_API_KEY` - Your Google Gemini API key

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your configuration

## Usage

### CLI Tool

```sh
python cli.py "What are the top 10 products by sales?"
```

Demo mode (no database connection required):
```sh
python cli.py "Show me all users" --demo
```

Options:
```sh
python cli.py --help
```

### In Python Scripts

```python
from db.connector import MySQLConnector
from utils.config import load_config

config = load_config('config.json')
conn = MySQLConnector(config).connect()
# Use conn as a MySQL connection
```

## Troubleshooting
- If you see `ImportError: No module named 'mysql.connector'`, ensure you have installed `mysql-connector-python`.
- Make sure your MySQL server is running and accessible.

## License
See [LICENSE](LICENSE) for details.