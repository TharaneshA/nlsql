nlsql --# NLSQL - Natural Language to SQL CLI Tool

[![PyPI Version](https://img.shields.io/pypi/v/nlsql.svg)](https://pypi.org/project/nlsql/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/TharaneshA/nlsql/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)

Convert natural language questions to SQL queries through a command-line interface.

## Features
- **Natural Language Processing**: Transform plain English questions into SQL
- **MySQL Integration**: Built-in support for MySQL databases
- **Demo Mode**: Test queries without database connection
- **Configurable**: Easy database configuration via JSON file
- **CLI Interface**: Simple command-line usage

## Installation
```bash
# Install from PyPI
pip install nlsql

# Or install locally
pip install -e .
```

## Configuration
1. Create `config.json`:
```json
{
  "host": "localhost",
  "user": "your_username",
  "password": "your_password",
  "database": "your_database"
}
```

## Usage
### Basic Query
```bash
nlsql "Show me the top 5 customers by total purchases"
```

### Demo Mode
```bash
nlsql "List all products in the electronics category" --demo
```

### Help Command
```bash
nlsql --help
```

## Examples
**Query with conditions:**
```bash
nlsql "Find orders between June 2023 and August 2023 over $500"
```

**Join operations:**
```bash
nlsql "Show customer names with their order totals"
```

## Development Setup
```bash
git clone https://github.com/TharaneshA/nlsql.git
cd nlsql
pip install -r requirements.txt
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.
