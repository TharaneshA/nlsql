import typer
from utils.config import setup_config, load_config
from db.connector import MySQLConnector
from ai.translator import generate_sql
from utils.formatting import print_sql, print_result
import getpass

app = typer.Typer()

@app.command()
def config():
    """Interactive configuration setup"""
    setup_config()
    print("\nConfiguration completed successfully!")

@app.command()
def query(
    question: str = typer.Argument(..., help="Natural language question to translate to SQL"),
    execute: bool = typer.Option(False, "-e", help="Execute the generated SQL query")
):
    """Process natural language questions into SQL"""
    config = load_config()
    db = MySQLConnector(config)
    schema = db.get_schema()
    
    print(f"\nTranslating: {question}")
    sql_query = generate_sql(question, schema, config['gemini_api_key'])
    print_sql(sql_query)
    
    if execute:
        password = getpass.getpass("Database password: ") or config['password']
        db.connect(password=password)
        result = db.execute_query(sql_query)
        print_result(result)

if __name__ == "__main__":
    app()