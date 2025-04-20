import requests
import json

def generate_sql(nl_query, schema, api_key, temperature=0.2):
    """Send a prompt to Gemini API to translate NL to SQL."""
    prompt = build_prompt(nl_query, schema)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gemini-pro",
        "prompt": prompt,
        "temperature": temperature
    }
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateText",
        headers=headers,
        data=json.dumps(data)
    )
    if response.status_code != 200:
        raise Exception(f"Gemini API error: {response.status_code} {response.text}")
    result = response.json()
    # Extract SQL from response (assuming response contains 'candidates')
    sql = result.get('candidates', [{}])[0].get('output', '').strip()
    return sql

def build_prompt(nl_query, schema):
    """Construct the prompt for Gemini API including schema context."""
    schema_str = json.dumps(schema, indent=2)
    prompt = (
        "You are an expert SQL assistant. Given the following database schema and a natural language query, "
        "generate the most appropriate SQL statement.\n"
        f"Schema: {schema_str}\n"
        f"Query: {nl_query}\n"
        "SQL:"
    )
    return prompt