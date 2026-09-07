---
name: ai-native-proof-ledger
description: >
  Design, implement, audit, or review verifiable history for ordinary SaaS,
  mobile, and serverless apps — tamper-evident audit trails, hash chains,
  Merkle transparency logs, witnessed checkpoints, external timestamp/chain
  anchoring, attestations, verifiable databases, consortium ledgers, and
  AI-agent action receipts. Use when a user asks to make history or audit
  logs tamper-evident or independently verifiable, anchor records to a
  blockchain, add proof/receipts/dispute bundles, choose between
  OpenTimestamps / EAS / immudb / Tessera / Rekor / Fabric / ChainMaker-style
  options, or review "blockchain" claims in a product. Do NOT use for
  crypto token/NFT features, mining, or trading — and do NOT use when the
  user only needs ordinary application logging with no external
  verification promise.
version: 1.0.0
author: Liz (lizliz.xyz)
license: MIT
disable-model-invocation: true
---

# ai-native-proof-ledger

Build verifiable history, not blockchain branding. The app database stays the
source of operational truth; the proof layer is an **append-only projection**;
every anchoring/witnessing provider is **replaceable**. Core evidence:
`references/landscape-2026.md` (dated 2026-09-08; re-run its §10 queries
before production use).

## 0. Quick start

```text
Design:    "Make our projects/work-items/agent-action history tamper-evident
            and customer-verifiable." → run §1 gate, pick ladder level (§3),
            implement per §5, ship verifier.
Implement: "We chose L2/L3 — build it." → implementation-patterns.md end to end.
Audit:     "Review our tamper-evidence claims / proof layer." →
           review-checklist.md; verdict per property.
Verify:    "Check this proof bundle." → patterns §8 verifier flow.
```

State before starting: who must be able to verify (internal audit, customer,
external auditor, court), against what trust roots, retention horizon, and
which claims will be made publicly (rubric in review-checklist.md §1).

## 1. Threat-model gate (run first; refuse to skip)

Answer in writing, per feature:

1. **Adversary**: careless code? rogue insider/admin? compromised signer?
   operator itself lying (split-view)? external party forging history?
2. **Who verifies, without trusting the operator?** If the answer is
   "nobody can", you are building a logging format — say so and consider
   stopping (kill criteria below).
3. **Which properties are actually promised**: event integrity, order,
   authorship, existence time, non-equivocation, availability,
   confidentiality, truthfulness. A mechanism buys only its own rows
   (landscape §2). Truthfulness is bought by *cross-party validation*, never
   by cryptography.
4. **PII**: any personal data in payloads, attrs, or digests? Hashes of
   personal data are personal data (EDPB 02/2025, v2.0 2026-07-07). If PII
   must be erasable, design mutable-source + supersession + keyed
   digests/crypto-shredding now (patterns §12), not later.
5. **Kill criteria — if any is true, recommend NOT building** (or L0 only):
   - no external party ever needs to verify history;
   - the value is marketing ("blockchain") rather than a named verifier and
     dispute process;
   - data is mutable-by-nature and corrections outnumber immutable facts;
   - the operator would never accept an independent witness (then
     non-equivocation is unattainable and claims must stay "signed");
   - honest alternative (ordinary audit log + backups + access controls)
     satisfies every stated requirement.

6. **7-day fastest real-world validation** (typical B2B SaaS; run before
   committing to L2+):
   - **D1**: pick one high-value, PII-light event type (e.g., work-item
     approval); write the threat gate answers; get one named external
     verifier to agree to check a proof.
   - **D2**: implement L1 (canonical envelope + chain) for that type only;
     golden-vector test green.
   - **D3**: add L2 batching + KMS-signed checkpoint; tamper test (byte
     flip, history rewrite) detected.
   - **D4**: publish checkpoints (object-lock bucket or signed commits) and
     get the external verifier to run the offline verifier once.
   - **D5**: if the verifier cannot complete without your help — that is a
     finding, not a bug fix; iterate once.
   - **D6**: add an anchor receipt (OTS) on one checkpoint; verify offline.
   - **D7**: decide with evidence: did the verifier actually re-verify
     without trusting you? If nobody will verify, or the layer changed no
     user-visible outcome, invoke kill criteria — ship L0 + honest claim
     language instead.

## 2. Anti-triggers (do not do these)

- No token/NFT/tokenomics detours; no mining; "Proof of Work performed"
  means signed receipts of agent work, nothing to do with PoW.
- No "blockchain = truth": a chain records what operators feed it. Luckin
  Coffee fabricated $300M+ in sales and employees concealed it partly by
  *creating a fake operations database* (SEC LR-24987, 2020-12-16) —
  ledger ≠ truth.
- Do not recommend a dependency when WebCrypto + ~100 lines is stronger and
  simpler; equally, do not pretend native SHA-256 provides
  canonicalization, sequencing, signatures, Merkle proofs, witnesses, or
  anchoring.
- Do not claim "tamper-proof/immutable"; claim tamper-evidence with named
  verifiers (rubric).
- Do not store PII on proof artifacts; do not treat hash-of-PII as anonymous.

## 3. Mechanism ladder (pick the lowest level that answers the gate)

| Level | Mechanism | Guarantee gained | NOT guaranteed | Trust model | Min viable implementation | Ops burden | Exit path | Verification test |
|---|---|---|---|---|---|---|---|---|
| **L0** | Ordinary audit log | completeness vs accidents | any tamper evidence | operator only | structured events, retention | trivial | export CSV | none |
| **L1** | Canonical append-only hash chain (per tenant) | event integrity + order detectable | vs whole-history rewrite; authorship; existence | operator's keys | envelope (patterns §1), JCS, SHA-256 chain, INSERT-only tables | low | chain is data; rebuild from app DB | recompute hashes; golden vectors |
| **L2** | Merkle batches + signed checkpoints | L1 + cheap per-event inclusion proofs + tamper evidence vs history rewrite by *DB admins* (checkpoint mismatches) | split-view by operator; existence | operator signing key (KMS) | RFC 6962-style tree; C2SP-format checkpoint notes; KMS Ed25519/P-256 | low-med | checkpoints are self-contained artifacts | path proof → root; checkpoint sig vs registry-as-of-time |
| **L3** | Published + witnessed checkpoints | L2 + non-equivocation (operator can't show different histories) | existence time; truthfulness | + ≥1 independent witness (quorum policy) | publish notes (object-lock bucket/signed commits); C2SP tlog-witness or partner auditor; monitor for forks | med | add/remove witnesses via registry; mirror anywhere | cosig quorum verify; fork monitor alarm drill |
| **L4** | External anchoring / standard attestations | L2/3 + externally provable existence time (and third-party authorship when using EAS-style attestations) | truthfulness; confidentiality | + anchor provider (TSA/Bitcoin/an L2) | AnchorAdapter (patterns §7): OTS (free, ~60 min typical, can stall in high-fee windows), RFC 3161 TSA (legal grade, per-call cost), EAS offchain+onchain anchor (wallet/RPC burden) | med | provider swap = new receipts; chain unchanged | offline receipt verify |
| **L5** | Consortium/permissioned consensus (Fabric v3.1.5, ChainMaker v2.3.10, Besu 26.x as stacks) | multi-org shared state; each member independently validates | truthfulness (members can collude to record false facts); simplicity | ≥3 orgs, independent admin domains, joint governance | only when a real consortium exists (see below) | high | export to generic schema (patterns §9/§13) | per-member recompute; governance review |

**Real vs theater at L5:** ≥3 organizations with independent interests run
validators in their own admin domains; upgrade/key policies are jointly
governed; each member can recompute and audit. One owner running three nodes
(a "shared edition" BaaS, a vendor-operated 4-node chain) is a vendor service
— call it that; its claims cap at "provider-operated".

**Composition rule:** levels stack (L1→L4 is the common SaaS shape) but are
additive capabilities, not a universal security ranking: L2 + L4 without L3
is valid when you need existence time but have no independent witness yet
(you get anchoring without non-equivocation — say so in claims). Re-derive
the level from the gate whenever requirements change; never start at L5
because "blockchain" was in the brief.

## 4. Property → mechanism map (quote this in designs)

| Property | Only provided by |
|---|---|
| Event integrity | hash chain / Merkle proofs (L1+) |
| Order | seq + prev-hash chaining (L1+); NOT timestamps |
| Authorship | signature over canonical envelope; key registry as-of-time (L1+ signed variant / L2+) |
| Existence time | external anchor: RFC 3161 TSA, OpenTimestamps (Bitcoin), onchain tx (L4) |
| Non-equivocation | published checkpoints + independent witnesses (L3+) |
| Availability | YOUR ops: exports, mirrors, DR — no ledger provides it |
| Confidentiality | off-chain PII + encryption — never from chains/anchors |
| Truthfulness | cross-party validation, external corroboration, audits — not crypto |

## 5. Implementation protocol (L1→L4 default shape)

1. **Envelope & canonicalization**: pin envelope `v`; canonicalize with RFC
   8785 JCS (or deterministic CBOR); domain-separate every hash/signature
   (`patterns §1–2`). Golden-vector tests in CI.
2. **Chain per tenant**: single sequencer per chain (queue/actor/advisory
   lock); `UNIQUE(chain_id, seq)`; `request_id` idempotency; INSERT-only
   roles (`patterns §9–10`).
3. **Sign**: actor signatures via KMS-held keys (agents never hold raw keys,
   `patterns §6, §11`); key registry with as-of-time verification and a
   rotation + compromise runbook.
4. **Batch & checkpoint**: Merkle batch every N events/minutes; C2SP-style
   checkpoint note signed by KMS; store note bytes verbatim.
5. **Publish & witness**: object-lock bucket / signed commits; ≥1 independent
   witness (C2SP tlog-witness or partner auditor — the WhatsApp/Cloudflare KT
   split is the template); fork monitor with alarms.
6. **Anchor (optional)**: adapter for OTS / RFC 3161 / EAS or direct chain
   root anchoring; receipts stored, offline-verifiable; provider-swappable.
7. **Verify**: self-contained proof bundle + offline verifier flow
   (`patterns §8`); customer-facing verify endpoint/CLI/badge that states the
   achieved level, never a stronger one.
8. **Privacy & retention**: PII off-chain; keyed digests; supersession/
   correction events; retention prunes with `retention.pruned` markers;
   erasure = payload+key deletion with documented residual risk
   (`patterns §12`; EDPB 02/2025).
9. **Test**: tamper, truncation, fork, rotation, anchor-corruption,
   idempotency, offline-verification suites (`patterns §14`).

### High-risk confirmation gates — pause and get explicit human sign-off before:
- writing any payload (even hashed) containing personal data onto an
  external/public anchor or chain;
- choosing L5 (consortium) or migrating to/from a ledger DB (QLDB is past
  end of support 2025-07-31; Azure Managed CCF deprecated 2025-07-31 — moving
  *off* these is usually right, moving *onto* a new one needs the gate);
- any irreversible external action: publishing checkpoints/witness endpoints
  publicly, deploying contracts (EAS schema registry is permanent), onchain
  anchoring with real funds;
- public claim language ("independently verifiable", "anchored",
  "audit-grade") going into marketing or contracts — route through the
  review-checklist rubric and, for legal claims, counsel.

## 6. Verification & reporting checklist (before saying "done")

- [ ] Gate (§1) answered in writing; kill criteria evaluated; level chosen
      and justified; level *achieved* = level *claimed*.
- [ ] Offline verification works: fresh machine, no app-DB access, bundle
      verifies (patterns §14.7).
- [ ] Tamper suite green: byte-flip, gap, history-rewrite, fork, key
      rotation, corrupt anchor all detected.
- [ ] Idempotency: duplicate submits produce one event; sequencer crash
      leaves detectable gap, alarms fire.
- [ ] Keys in KMS; agents request signatures; rotation drill documented.
- [ ] Privacy: PII audit of payloads/attrs/digests; erasure path tested;
      DPIA noted where required.
- [ ] Claim rubric passed on all user-facing text; no "tamper-proof";
      verifier independence stated ("verified against checkpoints
      published to X and cosigned by witness Y").
- [ ] Ops: backup of checkpoints+registry+witness sigs cross-region;
      monitoring on checkpoint cadence and anchor failures.
- [ ] Report format: chosen level → implemented mechanisms → verified
      properties (integrity/order/authorship/existence/non-equivocation) →
      explicitly NOT covered (truthfulness, availability, confidentiality
      where applicable) → how to verify (artifact + command) → expiry/recheck
      date for any time-sensitive choice.

## 7. References

- `references/landscape-2026.md` — dated evidence: Tessera/Rekor/C2SP,
  OTS, immudb/QLDB/Azure CL, EAS, Hypercore, Fabric/Besu/ChainMaker,
  Luckin case study (primary sources), EDPB/AI Act/NIST, AP2/MCP,
  library versions, query matrix, re-research commands.
- `references/implementation-patterns.md` — envelope, canonicalization,
  chain/Merkle/checkpoint/witness/anchor, SQL schemas, concurrency,
  keys/rotation, privacy, verifier flow, migration, tests.
- `references/review-checklist.md` — adversarial audit + claim rubric.

**Expiry clause:** versions, EOL/deprecation statuses, protocol revisions
(MCP 2025-11-25), and regulatory dates in landscape-2026.md were verified
2026-09-07/08 and go stale fast. Re-run landscape §10 before any production
decision; treat any new deprecation notice or spec revision as a trigger to
re-check the ladder guidance.
