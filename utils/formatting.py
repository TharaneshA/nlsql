import pandas as pd
import sys
import json
import typer
from pathlib import Path

def highlight_sql(sql):
    # Simple syntax highlighting for SQL (can be improved with pygments)
    try:
        import pygments
        from pygments.lexers import SqlLexer
        from pygments.formatters import TerminalFormatter
        return pygments.highlight(sql, SqlLexer(), TerminalFormatter())
    except ImportError:
        # Fallback to simple highlighting
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
            'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'GROUP BY', 'ORDER BY', 'LIMIT',
            'AND', 'OR', 'NOT', 'AS', 'IN', 'IS', 'NULL', 'DISTINCT', 'COUNT', 'AVG', 'SUM', 'MIN', 'MAX'
        ]
        for kw in keywords:
            sql = sql.replace(kw, f'\033[1;34m{kw}\033[0m')
        return sql

def print_sql(sql):
    typer.echo(highlight_sql(sql))

def print_result(result, columns, output_format='table', limit=100, file=None):
    """Print query results in various formats"""
    df = pd.DataFrame(result, columns=columns)
    
    if len(df) > limit and limit > 0:
        df = df.head(limit)
        typer.echo(f"Showing first {limit} rows...")
    
    if file:
        # Export to file
        file_path = Path(file)
        ext = file_path.suffix.lower()
        
        if ext == '.csv':
            df.to_csv(file_path, index=False)
        elif ext == '.json':
            df.to_json(file_path, orient='records', indent=2)
        elif ext == '.xlsx':
            df.to_excel(file_path, index=False)
        elif ext == '.md':
            markdown_content = df.to_markdown(index=False)
            if markdown_content is not None:
                with open(file_path, 'w') as f:
                    f.write(markdown_content)
            else:
                # Fallback if to_markdown returns None
                with open(file_path, 'w') as f:
                    f.write(str(df))
        else:
            # Default to CSV
            df.to_csv(file_path, index=False)
        
        typer.echo(f"Results exported to {file_path}")
        return
    
    # Print to console
    if output_format == 'table':
        try:
            markdown_content = df.to_markdown(index=False)
            if markdown_content is not None:
                typer.echo(markdown_content)
            else:
                typer.echo(str(df))
        except ImportError:
            typer.echo(df)
    elif output_format == 'json':
        typer.echo(df.to_json(orient='records', indent=2))
    elif output_format == 'csv':
        df.to_csv(sys.stdout, index=False)
    else:
        typer.echo(df)

def print_profile_info(profile):
    """Print formatted profile information"""
    typer.echo(f"Profile Type: {profile['type']}")
    typer.echo(f"Host: {profile['host']}")
    typer.echo(f"Port: {profile['port']}")
    typer.echo(f"Database: {profile['database']}")
    typer.echo(f"Username: {profile['username']}")
    # Don't print password

def print_table_schema(table_name, columns):
    """Print formatted table schema"""
    typer.echo(f"\nTable: {table_name}")
    typer.echo("-" * (len(table_name) + 7))
    
    df = pd.DataFrame(columns)
    try:
        markdown_content = df.to_markdown(index=False)
        if markdown_content is not None:
            typer.echo(markdown_content)
        else:
            typer.echo(str(df))
    except ImportError:
        typer.echo(df)

def print_history_entry(entry, index=None):
    """Print a formatted history entry"""
    timestamp = entry.get("timestamp", "").split("T")[0]
    question = entry.get("question", "")
    executed = "[executed]" if entry.get("executed", False) else ""
    
    if index is not None:
        typer.echo(f"{index}. [{timestamp}] {executed} {question}")
    else:
        typer.echo(f"[{timestamp}] {executed} {question}")

def export_results(results, columns, file_path, format='csv'):
    """Export query results to a file"""
    df = pd.DataFrame(results, columns=columns)
    path = Path(file_path)
    
    if format == 'csv' or path.suffix.lower() == '.csv':
        df.to_csv(path, index=False)
    elif format == 'json' or path.suffix.lower() == '.json':
        df.to_json(path, orient='records', indent=2)
    elif format == 'excel' or path.suffix.lower() in ['.xlsx', '.xls']:
        df.to_excel(path, index=False)
    else:
        # Default to CSV
        df.to_csv(path, index=False)
    
    return path