import pandas as pd
import sys

def highlight_sql(sql):
    # Simple syntax highlighting for SQL (can be improved with pygments)
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
        'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'GROUP BY', 'ORDER BY', 'LIMIT',
        'AND', 'OR', 'NOT', 'AS', 'IN', 'IS', 'NULL', 'DISTINCT', 'COUNT', 'AVG', 'SUM', 'MIN', 'MAX'
    ]
    for kw in keywords:
        sql = sql.replace(kw, f'\033[1;34m{kw}\033[0m')
    return sql

def print_sql(sql):
    print(highlight_sql(sql))

def print_result(result, columns, output_format='table', limit=100):
    df = pd.DataFrame(result, columns=columns)
    if len(df) > limit:
        df = df.head(limit)
        print(f"Showing first {limit} rows...")
    if output_format == 'table':
        print(df.to_markdown(index=False))
    elif output_format == 'json':
        print(df.to_json(orient='records', indent=2))
    elif output_format == 'csv':
        df.to_csv(sys.stdout, index=False)
    else:
        print(df)