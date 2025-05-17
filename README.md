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

## 🔧 Setting Up NLSQL with Your Local Database

To use **NLSQL** with your local database, you need to create a database connection profile. This allows the CLI to connect to your MySQL, PostgreSQL, or SQLite database and translate natural language into SQL queries.

---

### ✅ Step 1: Create a Database Profile

Run the following command to start the profile creation wizard:

```bash
nlsql profile create <profile-name>
```
Replace `<profile-name>` with something meaningful like `my_local_db`.

### 📋 Step 2: Enter Connection Details
You'll be prompted to enter your database connection information:

| Prompt | Example (MySQL) | Example (SQLite) |
|--------|----------------|------------------|
| Database type | MySQL | SQLite |
| Host | localhost | (leave blank) |
| Port | 3306 | (leave blank) |
| Database name | nlsql_demo | /path/to/your/database.db |
| Username | root | (leave blank) |
| Password | your_password | (leave blank) |
| Connection options | (optional) | (optional) |

💡 **Tip**: For SQLite, you can use `:memory:` to create an in-memory database.

### 🔁 Step 3: Set Active Profile
After creating a profile, set it as the active one:
```bash
nlsql profile use <profile-name>
```

### 🧪 Step 4: Test the Connection
You can test the database connection by listing tables:
```bash
nlsql list tables
```

### 💡 Example: MySQL Setup
```bash
nlsql profile create my_mysql_db

# Prompts:
# Database type: MySQL
# Host: localhost
# Port: 3306
# Database name: nlsql_demo
# Username: root
# Password: your_password

nlsql profile use my_mysql_db
nlsql list tables
```

### 💡 Example: SQLite Setup
```bash
nlsql profile create my_sqlite_db

# Prompts:
# Database type: SQLite
# Host: (leave blank)
# Port: (leave blank)
# Database name: ./nlsql_demo.db
# Username: (leave blank)
# Password: (leave blank)

nlsql profile use my_sqlite_db
nlsql list tables
```

### 🔐 Notes on Security & Config
- 🔒 Passwords are stored in plain text inside profile files. For secure environments, consider using environment variables.
- 📁 Profiles are stored in: `~/.nlsql/profiles/`
- ✅ The active profile is stored in: `~/.nlsql/active_profile.txt`

## Usage

![image](https://github.com/user-attachments/assets/062da90e-5d3b-45c7-a654-341dd100abfe)

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
