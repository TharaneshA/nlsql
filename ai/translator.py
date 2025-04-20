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

def generate_sql(nl_query, schema, api_key, temperature=0.2):
    if not api_key or len(api_key) < 20:
        raise ValueError("Invalid Gemini API key. Please check your configuration.")
    
    # Validate API connectivity
    try:
        test_response = call_gemini_api("Return ONLY the word 'success'", api_key)
        if 'success' not in test_response.lower():
            raise ValueError("API validation failed - unexpected response format")
    except Exception as test_error:
        raise ValueError(f"API validation failed: {str(test_error)}")

    """Send a prompt to Gemini API to translate NL to SQL."""
    prompt = build_prompt(nl_query, schema)
    return call_gemini_api(prompt, api_key, temperature)
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
    # Extract SQL from response (Gemini API v1 format)
    try:
        sql = result.get('candidates', [])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
    except (IndexError, KeyError) as e:
        raise Exception(f"API response format error: {str(e)}. Full response: {json.dumps(result, indent=2)}")
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