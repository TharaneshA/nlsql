# NLSQL - Natural Language to SQL CLI Tool

[![PyPI Version](https://img.shields.io/pypi/v/nlsql.svg)](https://pypi.org/project/nlsql/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/TharaneshA/nlsql/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/)

Convert natural language questions to SQL queries through a command-line interface.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/TharaneshA/nlsql.git
cd nlsql
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package locally:
```bash
pip install -e .
```

## Setup

1. Run the initial setup:
```bash
nlsql setup
```

2. Enter your Gemini API key when prompted
3. Optionally set up a database profile during setup, or create one later using:
```bash
nlsql profile create <profile-name>
```

## Usage

### Managing Profiles

- List profiles: `nlsql profile list`
- Create profile: `nlsql profile create <name>`
- Switch profile: `nlsql profile use <name>`
- Edit profile: `nlsql profile edit <name>`
- Delete profile: `nlsql profile delete <name>`

### Database Operations

- Connect to database: `nlsql connect`
- List tables: `nlsql list tables`
- Show table schema: `nlsql describe <table-name>`
- Cache database schema: `nlsql cache-schema`

### Querying

Basic query:
```bash
nlsql query "Show me all users from New York"
```

Options:
- `--edit` (`-e`): Edit SQL before execution
- `--execute` (`-x`): Execute the query
- `--save <name>`: Save query for later use
- `--format <format>`: Output format (table/json/csv)
- `--export <file>`: Export results to file
- `--explain`: Show query execution plan

### Saved Queries

- List saved queries: `nlsql saved list`
- Run saved query: `nlsql run <query-name>`
- Delete saved query: `nlsql saved delete <query-name>`

### History

- View query history: `nlsql history`

### Configuration

- List config: `nlsql config list`
- Set config value: `nlsql config set KEY=VALUE`
- Unset config value: `nlsql config unset KEY`

## Examples

1. Create and use a database profile:
```bash
nlsql profile create mydb
nlsql profile use mydb
```

2. Query with natural language:
```bash
nlsql query "Find all orders placed in the last 7 days" --execute
```

3. Save and reuse a query:
```bash
nlsql query "Show top 10 customers by order value" --save top_customers
nlsql run top_customers
```

4. Export query results:
```bash
nlsql query "List all products with low stock" --format csv --export low_stock.csv
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
