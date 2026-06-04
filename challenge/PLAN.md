# PLAN.md (committed before reading CLARIFICATIONS.md or writing solution code)

## Architecture

Input → Enrich → Score → Output pipeline:

1. **Ingest**: Read `companies.csv`, parse each row into a lookup keyed on `company_name`.
2. **Provider fan-out**: For each company, query all three providers (registry, listing, enrichment) in parallel. A missing key in the data source counts as "not found" from that provider — not an error.
3. **Merge & normalize**: Combine provider results into a per-company candidate record. Normalize names for comparison (lowercase, strip honorifics/titles, apply a small nickname alias map — e.g. Bob → Robert).
4. **Score**: Compute a `confidence_score` (0–100) from cross-source agreement and data completeness (see Quality section).
5. **Emit**: Write one output row per company: `contact_name`, `contact_role`, `contact_email_or_phone`, `confidence_score`, `source`, `needs_human_review`.

**Components**:
- `loader` — reads CSV, yields company dicts
- `providers` — wraps the mock JSON, exposes `query(company_name)` → `{registry, listing, enrichment}`
- `merger` — cross-references results, normalizes names, selects best contact candidate
- `scorer` — applies confidence logic
- `writer` — outputs result CSV

---

**The system is split into two parts: a Python pipeline that processes the data, and a React UI that displays the results for human review.**

**The Python pipeline is made up of 5 functions, each in its own file. The data flows through them in order — `loader.py` reads the CSV, `providers.py` looks up each company in the mock JSON, `merger.py` combines what the three sources returned into one candidate, `scorer.py` calculates the confidence score, and `writer.py` writes everything out to `results.json`.**

**The React UI reads that `results.json` file and displays a table of all companies with their contact, confidence score, and source. Any row flagged as `needs_human_review` is highlighted. No backend server is needed.**

---

## Sources & strategy

**Registry**: Most authoritative. A registered owner/president has a legal paper trail that is hard to fake. Weakness: small businesses often have stale registrations; "Registered Agent" is a legal filing role and may not be the actual decision-maker.

**Listing**: Good for phone numbers and sometimes a name. Weakness: names are often informal, incomplete, or absent; the phone may be a generic business main line rather than a direct contact.

**Enrichment**: The only source for email addresses. Ships with its own `provider_confidence` score. Weakness: generic inboxes (info@, office@, sales@) don't identify a named individual, and the provider's confidence is a self-report — treat it as one signal, not the verdict.

**Cross-referencing strategy**: Name agreement across independent sources is the strongest positive signal. If registry and listing independently name the same person, that agreement is meaningful. If the enrichment email's initials plausibly match the registry name (e.g. `d.ortega` vs `Daniel Ortega`), confidence rises further. Conversely, name disagreement across sources is a flag, not a tiebreak.

**Expected failure modes**:
- Sole proprietors rarely appear in state registries.
- Listings may return only a business phone with no person attached.
- Enrichment may return nothing, or a plausible-but-generic inbox.
- Some companies will be unresolvable from any source — that is expected and handled explicitly, not papered over.

---

**Three sources are combined: registry, listing, and enrichment. Registry is the most trustworthy since it has a legal aspect to it. Each source has pros and cons, so combining them allows you to take the pros from each source and cross-reference them, getting even more confident in the accuracy of the data and thus a higher confidence score and accurate contacts.**

**At least if we write "not found" we know we have to manually look for the contact. But if it says `info@`, it might trick us into thinking we have the contact information. Bad data adds more problems — if it is added into making a confidence score, the confidence score is then inaccurate.**

**Failure modes: registry missing for sole proprietors; listing returns only a business phone with no name; enrichment returns a generic inbox or nothing; some companies will be unresolvable — handled as "cannot verify".**

---

## Quality

**Confidence scoring logic (additive, capped 0–100)**:

| Signal | Points |
|---|---|
| Registry returns a named person | +30 |
| Listing returns a named person | +15 |
| Registry + listing names agree (normalized) | +20 |
| Enrichment email is present | +15 |
| Enrichment email initials plausibly match registry name | +10 |
| Enrichment `provider_confidence` ≥ 70 | +10 |
| Only source is enrichment with `provider_confidence` < 50 | −20 |
| Name present only from listing, role unknown | −10 |

**Dedupe**: One output row per company. Within a company, if sources conflict on name (e.g. two different people named across registry vs listing), prefer registry (higher trust), note the conflict in the `source` field, and set `needs_human_review: true` regardless of the computed score.

**Provenance**: Every output field carries the `source_url(s)` from whichever provider(s) contributed it. Nothing is emitted without a traceable `mock://` URL. The `source` field is a pipe-delimited list when multiple providers contribute.

**Cannot-verify states**: If no provider returns any usable data, OR if the computed `confidence_score` falls below the review threshold: emit `needs_human_review: true` and leave contact fields null. Do not fabricate a contact.

**False-positive risk**:
- "Registered Agent" is a legal filing designation — downweight this role relative to Owner/President/CFO.
- Generic email addresses (info@, office@, sales@) do not identify a person. Include them if they're the only lead, but cap confidence at 50 and flag for human review. They are a business contact, not a decision-maker contact.
- Role-less names from listings (e.g. "Jeff (manager)") are weaker than named-role entries from registry.

---

**The confidence score is based on cross-referencing across sources. The more sources that agree on the same person, the higher the confidence score. For example, if both registry and listing return "Daniel Ortega", that agreement makes us more confident it is Daniel Ortega than if only one source said so.**

**After the pipeline runs, the system automatically flags certain contacts as `needs_human_review: true` when confidence is low. A human then reviews only those flagged rows to determine if the contact is real — not every row.**

**For dedupe, if two sources return the same person for the same company, a function removes the duplicate so the contact only appears once in the output. If two sources return different names for the same company, both are flagged for human review regardless of confidence score and a human determines which contact is correct.**

**For provenance, every contact in the output carries the `source_url` from the mock source it came from, traceable back to the exact entry in `enrichment_responses.json`. This means if someone asks why a contact was returned, you can point to the exact source that produced it. Nothing is emitted without a traceable source.**

**If no source returns any data for a company, the merger detects this and sets `needs_human_review: true` directly. The `contact_name`, `contact_role`, and `contact_email_or_phone` fields are left null. No confidence score is calculated — there is nothing to score.**

**As for false-positive risk, the system could return a contact that looks legitimate but is not useful. For example, enrichment returning a generic email like `info@`, `sales@`, or `contact@` — these are not named individuals and should not be treated as real contacts. Another risk is the "Registered Agent" role from registry — this is a legal filing designation, not the actual decision-maker, so it could score high but still be the wrong person to contact.**

---

## Privacy / compliance

**Will do**:
- Query only mocked providers — no real scraping, no live PII harvested.
- Retain full provenance on every field so any contact can be challenged, traced, and removed.
- Flag uncertain contacts for human review before any outreach is initiated.
- Treat "cannot verify" as a valid, first-class output state — not a gap to fill with guesswork.

**Will NOT do**:
- Scrape personal social media profiles (LinkedIn, Facebook) or non-public sources.
- Infer or reconstruct PII beyond what providers return.
- Pass contacts to outreach pipelines below the confidence threshold without a human sign-off.
- Store contact data beyond the operational purpose of this AR collections run.

**Real-world considerations (noted, not implemented in this mock challenge)**:
- TCPA compliance for any phone outreach (prior express consent requirements).
- CAN-SPAM for email (unsubscribe mechanism, physical address required).
- State-level privacy laws — e.g. CCPA for California-based accounts.
- Data retention limits: contact records should expire or be deleted once the collection is resolved or the account is written off.

**Data retention — once the collections run is done and accounts are resolved, contact data should be deleted and not held onto indefinitely.**

**TCPA requires consent before cold calling someone's phone. CAN-SPAM has rules around email outreach.**

**If you are not confident it is the right decision-maker, outreach should not be initiated. This is enforced by the `needs_human_review` flag.**

---

## Clarifying questions

**1. What is the confidence threshold for `needs_human_review`?**
   - Why it matters: the threshold directly controls how many contacts get flagged for human review vs. passed through automatically. Using the wrong threshold means either too many contacts require manual work, or low quality contacts slip through.
   - Default assumption: 60 — contacts scoring below 60 are flagged for human review.
   - What changes: a higher threshold means more rows get flagged; a lower threshold means fewer rows get flagged and more contacts pass through automatically.

**2. Is a "Registered Agent" an acceptable contact to reach out to, or do we need an actual owner or decision-maker?**
   - Why it matters: some companies only have a Registered Agent in the registry — this is a legal filing role, not necessarily the person who handles payments. Reaching out to the wrong person wastes a collections call and could seem unprofessional.
   - Default assumption: since the data is there, we include it as a contact but flag it for human review rather than passing it through automatically.
   - What changes: if AgentCollect confirms only owners and decision-makers are acceptable, we would exclude Registered Agent entries entirely and treat those companies as "cannot verify."

**3. Should the system return one contact per company or multiple?**
   - Why it matters: some companies may have more than one valid decision-maker — for example an owner and a CFO. Returning only one could mean missing a better contact. On the other hand, if there is no clear best contact, it is unclear whether to return the weakest option or nothing at all.
   - Default assumption: return one contact per company, prioritizing the highest confidence candidate.
   - What changes: if multiple contacts per company are acceptable, the output structure changes to allow one-to-many rows per company, and the scoring logic would rank candidates rather than pick one.
