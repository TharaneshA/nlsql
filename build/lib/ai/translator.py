import requests
import json

def generate_sql(nl_query, schema, api_key="AIzaSyCv2o2UCfKKpfSmKuy2i6HgkBr-TVPseqM", temperature=0.2):
    """Send a prompt to Gemini API to translate NL to SQL."""
    prompt = build_prompt(nl_query, schema)
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
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}",
        headers=headers,
        data=json.dumps(data)
    )
    if response.status_code != 200:
        raise Exception(f"Gemini API error: {response.status_code} {response.text}")
    result = response.json()
    # Extract SQL from response (Gemini API v1 format)
    try:
        sql = result.get('candidates', [])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    except (IndexError, KeyError):
        raise Exception(f"Failed to parse Gemini API response: {result}")
    return sql.strip()

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