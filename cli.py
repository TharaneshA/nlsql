import argparse
import sys
import json
from utils import config
from db.connector import MySQLConnector
from db.schema import get_schema
from ai.translator import generate_sql
from utils.formatting import print_sql, print_result
import getpass

def main():
    parser = argparse.ArgumentParser(
        description="Natural Language to SQL CLI Tool"
    )
    parser.add_argument(
        "question",
        type=str,
        nargs="?",
        help="Plain English database query"
    )
    parser.add_argument(
        "--database", "-d",
        type=str,
        help="Specify database name"
    )
    parser.add_argument(
        "--execute", "-e",
        action="store_true",
        help="Execute query after generation"
    )
    parser.add_argument(
        "--no-execute", "-n",
        action="store_true",
        help="Do not execute query after generation"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to config file for credentials"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (table, json, csv)"
    )
    parser.add_argument(
        "--refresh", "-r",
        action="store_true",
        help="Force schema refresh"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode without database connection"
    )
    args = parser.parse_args()

    if not args.question:
        parser.print_help()
        sys.exit(1)

    # Demo mode uses a sample schema instead of connecting to a database
    if args.demo:
        print("Running in demo mode with sample schema...")
        # Sample schema for demonstration
        schema = {
            "tables": {
                "users": {
                    "columns": [
                        {"Field": "id", "Type": "int", "Key": "PRI"},
                        {"Field": "username", "Type": "varchar(50)"},
                        {"Field": "email", "Type": "varchar(100)"},
                        {"Field": "created_at", "Type": "datetime"}
                    ],
                    "foreign_keys": []
                },
                "products": {
                    "columns": [
                        {"Field": "id", "Type": "int", "Key": "PRI"},
                        {"Field": "name", "Type": "varchar(100)"},
                        {"Field": "price", "Type": "decimal(10,2)"},
                        {"Field": "category_id", "Type": "int"}
                    ],
                    "foreign_keys": [
                        {"COLUMN_NAME": "category_id", "REFERENCED_TABLE_NAME": "categories", "REFERENCED_COLUMN_NAME": "id"}
                    ]
                },
                "categories": {
                    "columns": [
                        {"Field": "id", "Type": "int", "Key": "PRI"},
                        {"Field": "name", "Type": "varchar(50)"}
                    ],
                    "foreign_keys": []
                },
                "orders": {
                    "columns": [
                        {"Field": "id", "Type": "int", "Key": "PRI"},
                        {"Field": "user_id", "Type": "int"},
                        {"Field": "total", "Type": "decimal(10,2)"},
                        {"Field": "created_at", "Type": "datetime"}
                    ],
                    "foreign_keys": [
                        {"COLUMN_NAME": "user_id", "REFERENCED_TABLE_NAME": "users", "REFERENCED_COLUMN_NAME": "id"}
                    ]
                }
            }
        }
        # Use a default API key for demo mode
        cfg = {"gemini_api_key": ""}
    else:
        # Normal mode with database connection
        cfg = config.load_config(args.config)
        if args.database:
            cfg['database'] = args.database
        if not cfg.get('password'):
            try:
                cfg['password'] = getpass.getpass(f"Password for MySQL user '{cfg.get('user','root')}': ")
            except Exception:
                pass
        connector = MySQLConnector(cfg)
        try:
            schema = get_schema(connector, force_refresh=args.refresh)
        except Exception as e:
            print(f"Error extracting schema: {e}")
            sys.exit(2)
    try:
        sql = generate_sql(args.question, schema, cfg.get('gemini_api_key',''))
    except Exception as e:
        print(f"Error generating SQL: {e}")
        sys.exit(3)
    print("\nGenerated SQL:")
    print_sql(sql)
    do_execute = args.execute and not args.no_execute and not args.demo
    if args.demo:
        print("\nDemo mode: Query execution is not available in demo mode.")
    elif do_execute:
        confirm = input("\nExecute this query? [y/N]: ").strip().lower()
        if confirm != 'y':
            print("Query execution cancelled.")
            sys.exit(0)
        try:
            conn = connector.connect()
            cursor = conn.cursor()
            cursor.execute(sql)
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                result = cursor.fetchall()
                print_result(result, columns, output_format=args.output)
            else:
                print(f"Query OK, {cursor.rowcount} rows affected.")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Error executing SQL: {e}")
            sys.exit(4)
    else:
        print("\nUse -e to execute this query.")

if __name__ == "__main__":
    main()