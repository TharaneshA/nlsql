import requests
import json

def call_gemini_api(prompt, api_key, temperature=0.2):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature
        }
    }
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        headers=headers,
        data=json.dumps(data)
    )
    if response.status_code != 200:
        raise Exception(f"Gemini API error: {response.status_code} {response.text}")
    result = response.json()
    try:
        sql = result.get('candidates', [])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    except (IndexError, KeyError) as e:
        raise Exception(f"API response format error: {str(e)}. Full response: {json.dumps(result, indent=2)}")
    return sql.strip()

def generate_sql(nl_query, schema, api_key, temperature=0.2, history=None):
    """Send a prompt to Gemini API to translate NL to SQL."""
    if not api_key or len(api_key) < 20:
        raise ValueError("Invalid Gemini API key. Please check your configuration.")
    
    # Validate API connectivity
    try:
        test_response = call_gemini_api("Return ONLY the word 'success'", api_key)
        if 'success' not in test_response.lower():
            raise ValueError("API validation failed - unexpected response format")
    except Exception as test_error:
        raise ValueError(f"API validation failed: {str(test_error)}")

    # Build prompt with schema and history context
    prompt = build_prompt(nl_query, schema, history)
    return call_gemini_api(prompt, api_key, temperature)

def build_prompt(nl_query, schema, history=None):
    """Construct the prompt for Gemini API including schema context, sample data, and conversation history."""
    # Format schema information
    tables_info = ""
    columns_info = ""
    relationships_info = ""
    constraints_info = ""
    indexes_info = ""
    sample_data = ""
    
    # Format sample data if available
    if isinstance(schema, dict) and "sample_data" in schema and schema["sample_data"]:
        sample_tables = []
        for table_name, table_data in schema["sample_data"].items():
            if "rows" in table_data and table_data["rows"]:
                sample_rows = json.dumps(table_data["rows"][:3], indent=2)  # Limit to 3 rows
                sample_tables.append(f"Table: {table_name}\nSample Data:\n{sample_rows}")
        
        if sample_tables:
            sample_data = "\n\n- Sample Data (for context):\n" + "\n\n".join(sample_tables)
    
    # Extract and format schema details
    if isinstance(schema, dict) and "tables" in schema:
        if isinstance(schema["tables"], dict):
            # Detailed schema format
            tables_info = "\n  - Tables: " + ", ".join(schema["tables"].keys())
            
            # Extract column information
            all_columns = []
            for table, table_info in schema["tables"].items():
                if "columns" in table_info and table_info["columns"]:
                    table_columns = []
                    for col in table_info["columns"]:
                        if isinstance(col, dict) and "Field" in col:
                            # MySQL format
                            col_info = f"{table}.{col['Field']} ({col.get('Type', 'unknown')})"
                            table_columns.append(col_info)
                        elif isinstance(col, dict) and "column_name" in col:
                            # PostgreSQL format
                            col_info = f"{table}.{col['column_name']} ({col.get('data_type', 'unknown')})"
                            table_columns.append(col_info)
                        elif isinstance(col, tuple) and len(col) >= 3:
                            # SQLite format
                            col_info = f"{table}.{col[1]} ({col[2]})"
                            table_columns.append(col_info)
                    all_columns.extend(table_columns)
            
            if all_columns:
                columns_info = "\n  - Columns: \n    - " + "\n    - ".join(all_columns)
            
            # Extract relationship information
            all_relationships = []
            for table, table_info in schema["tables"].items():
                if "foreign_keys" in table_info and table_info["foreign_keys"]:
                    for fk in table_info["foreign_keys"]:
                        if isinstance(fk, dict) and "COLUMN_NAME" in fk and "REFERENCED_TABLE_NAME" in fk:
                            # MySQL format
                            rel_info = f"{table}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}"
                            all_relationships.append(rel_info)
                        elif isinstance(fk, dict) and "column_name" in fk and "referenced_table" in fk:
                            # PostgreSQL format
                            rel_info = f"{table}.{fk['column_name']} -> {fk['referenced_table']}.{fk['referenced_column']}"
                            all_relationships.append(rel_info)
                        elif isinstance(fk, tuple) and len(fk) >= 4:
                            # SQLite format
                            rel_info = f"{table}.{fk[3]} -> {fk[2]}.{fk[4]}"
                            all_relationships.append(rel_info)
            
            if all_relationships:
                relationships_info = "\n  - Relationships: \n    - " + "\n    - ".join(all_relationships)
        else:
            # Simple schema format (just table names)
            tables_info = "\n  - Tables: " + ", ".join(schema["tables"])
    else:
        # Fallback for unknown schema format
        schema_str = json.dumps(schema, indent=2)
        tables_info = f"\n  - Schema: {schema_str}"
    
    # Format conversation history if provided
    formatted_history = ""
    if history and isinstance(history, list) and len(history) > 0:
        history_entries = []
        for entry in history[-5:]:  # Use last 5 entries at most
            if isinstance(entry, dict):
                timestamp = entry.get("timestamp", "").split("T")[0] if "timestamp" in entry else ""
                question = entry.get("question", "")
                sql = entry.get("sql", "")
                if question and sql:
                    history_entry = f"[{timestamp}] Question: {question}\nSQL: {sql}"
                    history_entries.append(history_entry)
        
        if history_entries:
            formatted_history = "\n\nCONVERSATION HISTORY:\n" + "\n\n".join(history_entries)
    
    # Build the comprehensive prompt
    prompt = f"""You are a helpful assistant designed to generate accurate SQL queries based on natural language questions about the given database schema. You'll analyze both the database structure and content to produce well-formed, efficient SQL queries.\n\nCURRENT QUERY:\n{nl_query}\n\nDATABASE INFORMATION:\n- Schema Information:{tables_info}{columns_info}{relationships_info}{constraints_info}{indexes_info}\n{sample_data}{formatted_history}\n\nINSTRUCTIONS:\n1. **Analyze the query**: Understand the user's natural language question about the database and its data.\n2. **Generate the SQL query**: Based on the analysis, generate an accurate SQL query that satisfies the user's request. Follow best practices for SQL query formation, ensuring clarity, performance, and security.\n   - **Match the user's query**: Generate a SQL query that answers the user's question based on the schema and data.\n   - **Adhere to best practices**:\n     - **Use proper indexing**: Ensure queries use indexed columns when applicable to improve performance.\n     - **Avoid SQL injection**: Always prefer parameterized queries where needed (for external use).\n     - **Ensure data integrity**: Respect the database constraints and avoid any operations that could violate them.\n   - **Optimize the query**: Ensure the query is efficient, especially for large datasets. Consider JOIN optimization, using LIMIT, and avoiding subqueries where possible.\n3. If the query is unclear or ambiguous, provide the most likely interpretation based on the schema.\n\nYour response should directly provide the most efficient, accurate SQL query based on the user's natural language query while maintaining clarity and security.\n\nSQL:\n"""
    
    return prompt