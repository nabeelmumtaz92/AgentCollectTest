import re

NICKNAMES = {
    'bob': 'robert', 'bill': 'william', 'will': 'william',
    'jim': 'james', 'joe': 'joseph', 'mike': 'michael',
    'tom': 'thomas', 'dan': 'daniel', 'dave': 'david',
    'steve': 'stephen', 'sam': 'samuel', 'matt': 'matthew',
    'nick': 'nicholas', 'rick': 'richard', 'liz': 'elizabeth',
}

def normalize_name(name):
    if not name:
        return None
    name = re.sub(r'\s+', ' ', name.lower().strip())
    parts = name.split()
    parts = [NICKNAMES.get(p, p) for p in parts]
    return ' '.join(parts)

def names_compatible(a, b):
    if not a or not b:
        return False
    if a == b:
        return True
    parts_a = a.split()
    parts_b = b.split()
    # last names must match
    if parts_a[-1] != parts_b[-1]:
        return False
    # first name or initial match
    if parts_a[0] == parts_b[0]:
        return True
    if parts_a[0][0] == parts_b[0][0]:
        return True
    return False

def merge(company_name, provider_data):
    registry = provider_data.get('registry', {})
    listing = provider_data.get('listing', {})
    enrichment = provider_data.get('enrichment', {})

    has_data = bool(registry or listing or enrichment)

    registry_name = registry.get('name')
    registry_role = registry.get('role')
    listing_name = listing.get('name')
    listing_phone = listing.get('phone')
    enrichment_email = enrichment.get('email')
    enrichment_phone = enrichment.get('phone')
    enrichment_conf = enrichment.get('provider_confidence', 0)

    norm_registry = normalize_name(registry_name)
    norm_listing = normalize_name(listing_name)

    conflict = bool(
        norm_registry and norm_listing and
        not names_compatible(norm_registry, norm_listing)
    )

    agree = bool(
        norm_registry and norm_listing and
        names_compatible(norm_registry, norm_listing)
    )

    # prefer registry name, fall back to listing
    contact_name = registry_name or listing_name or ''
    contact_role = registry_role or ''

    # prefer email, fall back to phone
    contact_email_or_phone = enrichment_email or listing_phone or enrichment_phone or ''

    # collect source_urls only for sources that contributed something
    sources = []
    if registry.get('source_url') and registry_name:
        sources.append(registry['source_url'])
    if listing.get('source_url') and (listing_name or listing_phone):
        sources.append(listing['source_url'])
    if enrichment.get('source_url') and (enrichment_email or enrichment_phone):
        sources.append(enrichment['source_url'])

    # check if enrichment email initials match registry name
    email_matches_registry = False
    if enrichment_email and registry_name:
        parts = registry_name.lower().split()
        if parts:
            first_initial = parts[0][0]
            if f'{first_initial}.' in enrichment_email.lower():
                email_matches_registry = True

    return {
        'company_name': company_name,
        'contact_name': contact_name,
        'contact_role': contact_role,
        'contact_email_or_phone': contact_email_or_phone,
        'source': ' | '.join(sources),
        'has_data': has_data,
        'conflict': conflict,
        'registry_name': registry_name,
        'listing_name': listing_name,
        'agree': agree,
        'enrichment_email': enrichment_email,
        'enrichment_provider_confidence': enrichment_conf,
        'email_matches_registry': email_matches_registry,
    }
