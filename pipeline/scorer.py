def score(merged):
    if not merged['has_data']:
        return 0

    points = 0

    if merged['registry_name']:
        points += 30

    if merged['listing_name']:
        points += 15

    if merged['agree']:
        points += 20

    if merged['enrichment_email']:
        points += 15

    if merged['email_matches_registry']:
        points += 10

    if merged['enrichment_provider_confidence'] >= 70:
        points += 10

    # penalty: enrichment is the only source and confidence is low
    only_enrichment = (
        not merged['registry_name'] and
        not merged['listing_name'] and
        merged['enrichment_email']
    )
    if only_enrichment and merged['enrichment_provider_confidence'] < 50:
        points -= 20

    # penalty: name only from listing with no role
    if merged['listing_name'] and not merged['registry_name'] and not merged['contact_role']:
        points -= 10

    # conflict between sources caps confidence
    if merged['conflict']:
        points = min(points, 50)

    return max(0, min(100, points))
