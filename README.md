# nlsql

A natural language SQL interface for MySQL databases.

## Requirements
- Python 3.7+
- MySQL server
- Required Python packages (see below)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/nlsql.git
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

## Usage

You can use the CLI tool (if available) or import the connector in your Python scripts:

```python
from db.connector import MySQLConnector
conn = MySQLConnector(config).connect()
# Use conn as a MySQL connection
```

If there is a CLI:
```sh
python cli.py --help
```

## Troubleshooting
- If you see `ImportError: No module named 'mysql.connector'`, ensure you have installed `mysql-connector-python`.
- Make sure your MySQL server is running and accessible.

## License
See [LICENSE](LICENSE) for details.