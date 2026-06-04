import json

def load_mock_data(filepath):
    with open(filepath, encoding='utf-8') as f:
        return json.load(f)

def query(company_name, mock_data):
    return mock_data.get(company_name, {})
