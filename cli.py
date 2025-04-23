import typer
from utils.config import setup_config, load_config
from db.connector import MySQLConnector
from ai.translator import generate_sql
from utils.formatting import print_sql, print_result
import getpass

app = typer.Typer(add_completion=False, help="Natural Language to SQL CLI Tool.\n\nQuick query with default settings:\n  nlsql 'show all users'\nEdit query before execution:\n  nlsql 'find top selling products last month' -E -e\nOutput as CSV for further processing:\n  nlsql 'list overdue invoices' -e -o csv > overdue.csv\nForce schema refresh and execute query:\n  nlsql 'count orders by customer' -r -e\n\nUse --help for all options and commands.")

@app.command()
def config():
    """Interactive configuration setup"""
    setup_config()
    print("\nConfiguration completed successfully!")

@app.command()
def query(
    question: str = typer.Argument(..., help="Natural language question to translate to SQL"),
    execute: bool = typer.Option(False, "-e", help="Execute the generated SQL query"),
    edit: bool = typer.Option(False, "-E", help="Edit the generated SQL before execution"),
    output: str = typer.Option("table", "-o", help="Output format: table, csv, json"),
    refresh: bool = typer.Option(False, "-r", help="Force schema refresh before query"),
    demo: bool = typer.Option(False, "--demo", help="Run in demo mode (no DB connection)")
):
    """Process natural language questions into SQL"""
    config = load_config()
    schema = None
    if demo:
        # Demo schema (example)
        schema = {"tables": ["users", "orders", "products"]}
        print("[Demo Mode] Using sample schema: users, orders, products")
    else:
        db = MySQLConnector(config)
        schema = db.get_schema(force_refresh=refresh)
    print(f"\nTranslating: {question}")
    sql_query = generate_sql(question, schema, config.get('gemini_api_key', ''))
    print_sql(sql_query)
    if edit:
        print("\n--- Edit SQL (type new SQL and press Enter, or leave blank to keep) ---")
        new_sql = input("Edit SQL: ").strip()
        if new_sql:
            sql_query = new_sql
    if execute:
        if demo:
            print("[Demo Mode] Execution skipped.")
            return
        password = getpass.getpass("Database password: ") or config.get('password', '')
        db.connect(password=password)
        result, columns = db.execute_query(sql_query)
        print_result(result, columns, output_format=output)

@app.callback()
def main(
    question: str = typer.Argument(None, help="Natural language question to translate to SQL (quick mode)", show_default=False),
    execute: bool = typer.Option(False, "-e", help="Execute the generated SQL query"),
    edit: bool = typer.Option(False, "-E", help="Edit the generated SQL before execution"),
    output: str = typer.Option("table", "-o", help="Output format: table, csv, json"),
    refresh: bool = typer.Option(False, "-r", help="Force schema refresh before query"),
    demo: bool = typer.Option(False, "--demo", help="Run in demo mode (no DB connection)")
):
    """NLSQL - Natural Language to SQL CLI Tool"""
    if question:
        # Direct question mode
        ctx = typer.get_current_context()
        ctx.invoke(query, question=question, execute=execute, edit=edit, output=output, refresh=refresh, demo=demo)

if __name__ == "__main__":
    app()