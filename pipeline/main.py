import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from loader import load_companies
from providers import load_mock_data, query
from merger import merge
from scorer import score
from writer import write_results

CONFIDENCE_THRESHOLD = 70

COMPANIES_PATH = os.path.join(os.path.dirname(__file__), '..', 'challenge', 'data', 'companies.csv')
MOCK_PATH = os.path.join(os.path.dirname(__file__), '..', 'challenge', 'mocks', 'enrichment_responses.json')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'results.json')

def run():
    companies = load_companies(COMPANIES_PATH)
    mock_data = load_mock_data(MOCK_PATH)

    results = []
    for company in companies:
        name = company['company_name']
        provider_data = query(name, mock_data)
        merged = merge(name, provider_data)
        confidence = score(merged)

        needs_review = (
            not merged['has_data'] or
            confidence < CONFIDENCE_THRESHOLD or
            merged['conflict']
        )

        results.append({
            'company_name': name,
            'mailing_address': company['mailing_address'],
            'contact_name': merged['contact_name'],
            'contact_role': merged['contact_role'],
            'contact_email_or_phone': merged['contact_email_or_phone'] if not needs_review else '',
            'confidence_score': confidence if merged['has_data'] else None,
            'source': merged['source'],
            'needs_human_review': needs_review,
        })

    write_results(results, OUTPUT_PATH)
    print(f"Done. {len(results)} companies processed. Output: {OUTPUT_PATH}")

if __name__ == '__main__':
    run()
