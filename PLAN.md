PLAN: Enterprise Contact Finder Engine

An architectural blueprint for a resilient, multi-source contact enrichment pipeline that balances automated verification with deterministic fallback tracking.

1. System Architecture

The system will be built as a decoupled, asynchronous pipeline using an Enrichment Coordinator pattern. This isolates rate-limiting, handles varying provider latencies, and enforces strict provenance trailing.

Plaintext

[Input: companies.csv]
│
▼
┌───────────────┐
│ Input Parser │ ──► Standardizes company_name & malformed address blocks
└───────────────┘
│
▼
┌───────────────┐
│ Enrichment │ ──► Dispatches parallel/waterfall worker jobs to
│ Coordinator │ Mock Search, LinkedIn/Firmographic, and Domain Providers
└───────────────┘
│
├──────────────────────┬──────────────────────┐
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Provider 1 │ │ Provider 2 │ │ Provider 3 │
└─────────────┘ └─────────────┘ └─────────────┘
│ │ │
└──────────────────────┼──────────────────────┘
│ (Raw Payloads + Provenance Meta)
▼
┌───────────────┐
│ Resolution & │ ──► Resolves duplicates, computes confidence,
│ Scoring Node │ and assigns flags (needs_human_review)
└───────────────┘
│
▼
[Output Dataset]

Execution Flow:

Ingestion & Sanitization: Parse input rows, strip legal entities (LLC, Inc., PTY Ltd), and geocode/normalize mailing addresses to establish distinct search parameters.

Parallel/Waterfall Dispatcher: Query firmographic, domain-discovery, and B2B profile mock engines.

Resolution & Merging Layer: Consolidate disparate multi-source payloads matching the target company identity.

Scoring & Evaluation Engine: Weigh source reliability, flag cross-verification points, and determine human intervention triggers.

2. Sources & Strategy

To bypass single-source blind spots, we utilize a tiered waterfall strategy combining three distinct data vectors:

Firmographic / Entity Resolution Registry (Mock Provider A): Used to resolve the localized company_name + address into an official corporate domain name and verified executive roster.

B2B Professional Graphs (Mock Provider B): Used to isolate specific localized decision-makers (e.g., Owner, CFO, AP Manager) tied to that corporate entity.

Contact Telemetry Engine (Mock Provider C): Used to uncover actionable operational endpoints (direct email structure/phone numbers) matching the isolated target identity.

3. Quality, Provenance, & Uncertainty Management

Data Provenance (Traceability)
Every enriched record contains a structural provenance_chain array. We never overwrite values without tracking their origin.

JSON
"provenance_chain": [
{"field": "contact_name", "source": "Mock_B2B_Graph_API", "timestamp": "2026-06-05T12:00:00Z"},
{"field": "contact_email", "source": "Mock_Email_Verifier", "timestamp": "2026-06-05T12:01:00Z"}
]

Confidence Scoring Logic Matrix

Confidence score starts at 0 and scales up dynamically based on cross-verification rules:

Base Match (+40 pts): Direct target profile discovery matching company metadata.

Cross-Provider Consensus (+30 pts): Separate independent sources yield identical names/roles.

Format/Domain Validation (+20 pts): Email handles accurately match the verified company domain format.

Direct Match Penalties (-25 pts): Name matching generic titles (e.g., "Support", "Info") or stale data structures.

Handling "Cannot-Verify" and False-Positives

The "Cannot-Verify" State: If zero sources return records, or the combined score lands beneath our processing threshold, the record is safely written out with empty contact strings, a low confidence flag, and needs_human_review: true. We never hallucinate placeholders.

False-Positive Mitigation: If two sources yield highly conflicting decision-makers (e.g., two different owners), the confidence score is automatically halved, instantly dropping it into the manual evaluation queue.

4. Privacy & Compliance Bounds

What We WILL Do: Restrict data footprint collection strictly to B2B corporate contact targets. Keep data elements localized to corporate workspaces.

What We WILL NOT Do: We will not store, log, or scan PII belonging to non-business individuals, scrapers running outside corporate API terms, or look up residential data points.

5. Decision-Value Clarifying Questions

Question 1: What is the strict hierarchical order of preferred decision-making personas?
Why it matters: In logistics small-businesses, the "Owner" frequently acts as the CFO, whereas in larger firms, an "Accounts Payable Manager" handles invoice processing directly. Knowing the premium role order changes how we rank targets.

Default Assumption: Owner > CFO > AP Manager > Office Manager.

Design Delta: If the response prioritizes AP Managers over Owners, our data merging layer will favor an explicit AP contact payload over an executive profile match when both exist.

Question 2: What is the hard numeric threshold score for triggering needs_human_review?

Why it matters: This directly drives the balance between operational overhead (cost of human eyes checking files) and financial risk (the impact of sending a collection notice to the wrong person).

Default Assumption: Confidence threshold is set to 70 / 100. Any calculation scoring below this marks needs_human_review = true.

Design Delta: Determines the conditional break threshold in our resolution engine.

Question 3: Are we prioritizing Outreach Reachability (Quantity) or Data Accuracy (Precision)?

Why it matters: If precision is paramount, any record missing independent cross-verification must be flagged for manual review. If outreach speed is paramount, we relax constraints to output the highest-probability contact instantly.

Default Assumption: Strict Data Accuracy (High Precision). Unverified data defaults to human routing.

Design Delta: Toggles whether single-source records without domain validation require manual checking or can pass automatically to production pipelines.
