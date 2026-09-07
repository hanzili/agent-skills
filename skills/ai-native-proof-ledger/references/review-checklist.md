# Adversarial review checklist — verifiable history claims

For security reviewers, auditors, and agents reviewing an implementation or a
claim. Companion to `SKILL.md` §ladder and `implementation-patterns.md`.

---

## 1. Claim-language rubric (say exactly this, nothing stronger)

| Claim phrase | Minimum supporting mechanism | Forbidden unless |
|---|---|---|
| "Tamper-evident" | Hash chain + verifiable checkpoints; a verifier can detect alteration | — |
| "Tamper-proof" / "immutable" | **Never allowed** for app-level ledgers. Any storage layer can be rewritten by someone with enough privilege; only *detection* is sold | — |
| "Signed" | Signature over canonical bytes by key K; name the key/registry | payload canonicalization is pinned |
| "Independently verifiable" | Verifier can check integrity+order+authorship **without trusting the operator's current systems** (proof bundle + public keys) | proof artifacts are self-contained |
| "Witnessed / non-equivocation" | ≥1 independent witness cosignatures on checkpoints (quorum policy) | witness ≠ operator; split-view monitor exists |
| "Anchored" | External anchor receipt (OTS/RFC 3161/onchain) verifiable offline | receipt verifies; state what is anchored (a checkpoint hash, not "the data") |
| "Timestamped" | Time source named (system clock vs TSA vs block time) | distinguish recording time vs external existence time |
| "Consensus-backed" | Multi-org permissioned ledger with ≥3 independent orgs + governance doc | every org can audit independently |
| "Blockchain-secured" | Only with L4+ and a sentence naming which property the chain adds | otherwise ban the phrase |
| "Audit-grade" / "legally binding" | Named legal regime (eIDAS qualified timestamp, record retention rule) with counsel sign-off | never by default |
| "AI agent did X" | Event signed by agent key with approval_ref for irreversible steps | distinguish "key K signed" from "human did/approved" |

**The one-sentence test:** every public claim must survive
"*verified by whom, against what artifact, without trusting whom?*"

---

## 2. Adversarial checklist

Attack each item; "we hash everything" is not an answer to any of these.

### A. Whole-history recomputation
- [ ] If an attacker (or insider) rewrites events **and** recomputes all
      hashes from genesis, is anything broken? (Answer must be: checkpoints
      published/anchored earlier no longer match. If checkpoints are only in
      the same DB, the chain is decorative.)
- [ ] Is there at least one artifact outside the operator's direct write
      path: published checkpoint, witness cosignature, anchor receipt, or
      auditor export?

### B. Truncation / rollback
- [ ] Drop the tail: can a verifier detect a shorter history? (Checkpoint
      size + seq monotonicity + witness max-seen.)
- [ ] Roll back to an earlier checkpoint and resume: does the fork become
      visible (consistency proof failure / two heads)?

### C. Fork / equivocation
- [ ] Operator shows different histories to tenant A vs auditor B: what
      detects it? (Independent witness or monitor; single-witness minimum;
      quorum policy documented.)
- [ ] Are checkpoints and their signatures **immutable artifacts** (object
      lock / signed commits / anchored), not mutable rows?

### D. Compromised signer
- [ ] Where do signing keys live? KMS/HSM policy or raw env var?
      (Raw secret = fail.)
- [ ] Key compromise runbook: rotation, compromise-window statement, what
      happens to authorship claims in that window?
- [ ] Agents hold no signing keys (I6); signing goes through policy gates.

### E. Colluding witnesses
- [ ] Are witnesses independent of the operator (different org, different
      infra)? n colluding witnesses still bound by quorum M-of-N?
- [ ] Is the witness list + trust policy documented and versioned?

### F. Oracle problem (bad input)
- [ ] For each event type: who asserts the fact, and what *outside* that
      assertion corroborates it? (Payment provider receipt, carrier webhook,
      counterparty signature, user approval, cross-party anchor.)
- [ ] Does any marketing copy imply the ledger makes the *content* true?
      (Fail → fix copy; see rubric.)

### G. Availability & portability
- [ ] Can a customer leave with a proof bundle that verifies offline?
- [ ] DR: checkpoints + key registry + witness sigs backed up cross-region,
      immutable; rebuild path documented, with its limits stated.
- [ ] Verifier independence: verify endpoint/CLI doesn't call the writer's
      DB (I7).

### H. Privacy leakage
- [ ] PII off-chain (I5)? Check payloads, attrs, tool-call dumps, and
      *digests of personal data* (still personal data — EDPB 02/2025).
- [ ] Erasure design: keyed digests / crypto-shredding / supersession — and
      is the residual-risk story written down (DPIA if high-risk)?
- [ ] Cross-tenant isolation: separate chains; exports never mix tenants.

### I. Concurrency & idempotency
- [ ] Duplicate submits (retry storm) → one event (request_id UNIQUE)?
- [ ] Sequencer crash mid-batch → no silent gap; alarms fire?
- [ ] Clock-skew: order derived from seq, not timestamps?

### J. Crypto hygiene
- [ ] Canonicalization pinned & versioned (RFC 8785 or equivalent); golden
      vector tests in CI?
- [ ] Domain separation on every hash/signature input?
- [ ] Algorithm agility: alg + key_id recorded; verification uses
      registry-as-of-event-time; rotation drill exists?
- [ ] Signature verification failures **fail closed**; unknown algorithms
      rejected, not ignored?

### K. AI-agent specifics
- [ ] Agent actions carry actor identity, tool provenance, and — for
      irreversible actions — human approval reference?
- [ ] "Proof of work performed" copy never drifts into "proof the work was
      correct" or any mining-PoW confusion?
- [ ] Model/artifact versions referenced by digest (e.g., signed model
      manifest), not by name alone?

### L. Process
- [ ] Kill criteria written down (see SKILL.md §Threat gate): when would
      this layer be removed because it adds no independent trust?
- [ ] Claim wording reviewed against §1 rubric at least as often as deps
      are bumped.
- [ ] Re-research date on the landscape file not stale (>90 days = flag).

---

## 3. Verdict vocabulary for review reports

- **L0–L5** (mechanism level actually implemented, per SKILL.md ladder) —
  report the *achieved* level, not the designed one.
- **Verified / Verified-with-caveats / Not verifiable / Claim overstated** —
  per property (integrity, order, authorship, existence-time,
  non-equivocation, availability, confidentiality, truthfulness).
- Overclaims are findings, not style notes: "tamper-proof" anywhere in
  user-facing copy is a P1.
