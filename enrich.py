import json
import os
import math

# --- CONFIGURATION CONSTANTS ---
CONFIDENCE_THRESHOLD = 70

# Priority weights based on target personas
ROLE_PRIORITIES = {
    'ap manager': 4,
    'accounts payable': 4,
    'owner': 3,
    'founder': 3,
    'cfo': 2,
    'finance lead': 2,
    'office manager': 1,
    'default': 1
}

def get_role_priority(role: str) -> int:
    """Normalizes roles to evaluate priority weights accurately."""
    if not role:
        return ROLE_PRIORITIES['default']
    normalized = str(role).lower().strip()
    return ROLE_PRIORITIES.get(normalized, ROLE_PRIORITIES['default'])

def process_company_enrichment(company_name: str, company_fixtures: dict) -> dict:
    """Core Orchestrator to Process a Single Company Entry."""
    # Structural Initialization for Output Structure
    result = {
        "company_name": company_name,
        "contact_name": "",
        "contact_role": "",
        "contact_email_or_phone": "",
        "confidence_score": 0,
        "source": [],
        "needs_human_review": True
    }

    # Safe Guardrail: Handle 100% missing rows gracefully (Cannot-Verify State)
    if not company_fixtures:
        return result

    registry = company_fixtures.get('registry')
    listing = company_fixtures.get('listing')
    enrichment = company_fixtures.get('enrichment')

    detected_name = ""
    detected_role = ""
    contact_channel = ""

    source_urls = []
    signals_matched = 0
    cross_provider_agreement = False

    # 1. Process Registry Vector
    if registry and registry.get('name'):
        detected_name = registry['name']
        detected_role = registry.get('role', 'Executive')
        source_urls.append(registry['source_url'])
        signals_matched += 1

    # 2. Process Web Listings Vector
    if listing:
        if listing.get('source_url'):
            source_urls.append(listing['source_url'])
        
        if listing.get('name'):
            signals_matched += 1
            # If names match across independent vectors, confirm consensus
            if detected_name and detected_name.lower() == listing['name'].lower():
                cross_provider_agreement = True
            elif not detected_name:
                detected_name = listing['name']
                detected_role = "Contact"
        
        if listing.get('phone') and not contact_channel:
            contact_channel = listing['phone']

    # 3. Process Telemetry Enrichment Vector
    if enrichment:
        if enrichment.get('source_url'):
            source_urls.append(enrichment['source_url'])
        
        enrichment_channel = enrichment.get('email') or enrichment.get('phone')
        if enrichment_channel:
            signals_matched += 1
            # Channel preference strategy: Prioritize validated email metrics
            if enrichment.get('email'):
                contact_channel = enrichment['email']
            elif not contact_channel:
                contact_channel = enrichment['phone']

    # --- CONFIDENCE SCORING LOGIC MATRICES ---
    score = 0

    if signals_matched > 0:
        # Baseline allocation for raw discovery matches
        score += 40
        
        # Scale points linearly based on multi-source discovery vectors
        score += (signals_matched - 1) * 15
        
        # Add premium score for independent identity alignment
        if cross_provider_agreement:
            score += 20

        # Incorporate telemetry confidence parameters safely if present
        if enrichment and enrichment.get('provider_confidence'):
            score += (enrichment['provider_confidence'] * 0.2)

        # Apply role relevance adjustments based on target guidelines
        priority = get_role_priority(detected_role)
        score += (priority * 2)

        # Normalize value caps beneath explicit ceilings
        score = min(math.floor(score), 100)

    # --- ENFORCE STRICT EVALUATION CUTOFFS ---
    result["source"] = source_urls
    result["confidence_score"] = score

    if score >= CONFIDENCE_THRESHOLD and detected_name and contact_channel:
        result["contact_name"] = detected_name
        result["contact_role"] = detected_role
        result["contact_email_or_phone"] = contact_channel
        result["needs_human_review"] = False
    else:
        # Strict compliance zero-out fallback layout
        result["contact_name"] = ""
        result["contact_role"] = ""
        result["contact_email_or_phone"] = ""
        result["needs_human_review"] = True

    return result

def main():
    # Automatically resolves directory paths relative to the file position
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mock_file_path = os.path.join(base_dir, 'challenge', 'mocks', 'enrichment_responses.json')
    
    if not os.path.exists(mock_file_path):
        print(f"Error: Missing fixture path at {mock_file_path}")
        return

    with open(mock_file_path, 'r', encoding='utf-8') as f:
        raw_fixtures = json.load(f)
    
    target_companies = list(raw_fixtures.keys())

    print(f"Processing minimal working slice over {len(target_companies)} mock rows in Python...\n")
    
    processed_output = []
    
    # Text-based terminal layout dashboard
    header_fmt = "{:<25} | {:<15} | {:<5} | {:<12} | {:<s}"
    print(header_fmt.format("Company", "Contact", "Score", "Review Req.", "Sources Tracked"))
    print("-" * 75)

    for company in target_companies:
        res = process_company_enrichment(company, raw_fixtures[company])
        processed_output.append(res)
        
        print(header_fmt.format(
            company[:25],
            res['contact_name'] if res['contact_name'] else '[OMITTED]',
            res['confidence_score'],
            "TRUE" if res['needs_human_review'] else "FALSE",
            str(len(res['source']))
        ))

    # Save output dataset cleanly at the root directory
    output_destination = os.path.join(base_dir, 'enriched_contacts_output.json')
    with open(output_destination, 'w', encoding='utf-8') as f:
        json.dump(processed_output, indent=2, ensure_ascii=False, fp=f)
        
    print(f"\nProcessed dataset written cleanly to: {output_destination}")

if __name__ == "__main__":
    main()