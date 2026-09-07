# Implementation patterns — generic proof ledger

Language-neutral unless noted; TypeScript + WebCrypto is used for pseudocode
because it runs in Node, browsers, mobile (via HMAC/WebCrypto bindings), and
most edge isolates. **Invariants are the contract; code is illustration.**

Cross-references: mechanism choices and evidence → `landscape-2026.md`;
audit checklist and claim wording → `review-checklist.md`.

---

## 0. Language-neutral invariants (the real spec)

1. **I1 Canonical bytes**: any hashed/signed value is serialized by a pinned,
   deterministic encoding. Two honest implementations must produce identical
   bytes for identical logical data — forever. Pin the encoding version in
   the record itself.
2. **I2 Domain separation**: every hash/signature input starts with a
   constant tag (`"pl/chain/v1"`, `"pl/batch/v1"`, `"pl/checkpoint/v1"`).
   Never sign raw concatenations that could be replayed as another type.
3. **I3 Append-only**: proof-layer tables accept `INSERT` only. No UPDATE/DELETE
   grants, no ORM upserts; corrections are new superseding events.
4. **I4 Single sequence per chain**: `(chain_id, seq)` is UNIQUE and gap-free
   as observed; `entry.prev_hash` links to `hash(entry at seq-1)`. A missing
   or mismatched link is a detectable violation, not a silent fix-up.
5. **I5 PII off-chain**: payloads containing personal data live in the
   mutable app DB; the proof layer stores only digests, commitments, and
   opaque references. Hashes of personal data are still personal data
   (EDPB 02/2025) — prefer hashes of *salted digests* or of non-personal
   artifact IDs.
6. **I6 Keys ≠ code**: signing keys live in a KMS/HSM (or OS keystore on
   mobile) behind an authorization policy. Application code and agents
   request signatures; they never hold raw private keys.
7. **I7 Verification is a separate code path**: the verifier must not import
   the writer's business logic. It consumes canonical bytes + proofs only.
8. **I8 Everything is replaceable**: app DB = operational truth; proof layer =
   append-only projection; anchoring provider = swappable adapter. Exiting a
   provider must be a config change + re-anchored checkpoint, never a rewrite
   of history.

---

## 1. Canonical event envelope

```jsonc
{
  "v": 1,                        // envelope schema version (I1)
  "type": "workitem.status_changed",
  "chain_id": "tenant-7f3a/main", // one logical chain per tenant/scope
  "seq": 1042,                    // assigned by the sequencer (I4)
  "ts": "2026-09-08T09:15:00.000Z",
  "actor": {                      // WHO asserted this (authorship)
    "kind": "agent|user|service",
    "id": "agent:repo-analyzer#7",
    "key_id": "k-2026-06"         // resolves via key registry (§6)
  },
  "subject": { "kind": "workitem", "id": "wi_928" },
  "payload_digest": "sha256:9f1c…",   // digest of OFF-CHAIN payload (I5)
  "payload_ref": "appdb://workitems/wi_928@rev41",
  "prev": { "seq": 1041, "hash": "sha256:0ab3…" },
  "attrs": { "schema": "workitem.v3", "locale": "en" }
}
```

Rules:
- The **payload** stays in the app DB. The envelope carries its digest plus a
  resolvable reference. Where the payload itself is immutable evidence
  (exported PDF, screenshot), store its digest + content-addressed copy and
  treat that copy as an artifact with its own retention rule.
- `actor.kind=agent` events MUST record the tool/skill invocation id and, for
  irreversible actions, the human-approval reference (see §11).
- Corrections/rectifications are new events: `type: "*.corrected"` with
  `supersedes: {seq, hash}` (§9.3). Nothing is rewritten (I3).

## 2. Canonicalization

- **Default: RFC 8785 JSON Canonicalization Scheme (JCS)**
  (https://www.rfc-editor.org/rfc/rfc8785) — UTF-8, sorted keys, shortest
  float form, no whitespace. Available in TS via `canonicalize`
  (RFC 8785) packages; implementable in ~200 lines for a JSON subset. If your
  runtime is CBOR-native (device/IoT), use RFC 8949 core deterministic
  encoding instead — pin one, don't mix.
- Before hashing: `bytes = utf8(jcs(envelope))`. The `v` field pins the
  encoding so future changes are explicit.
- Floats: avoid. IDs and money as strings/ints. (JCS handles floats
  deterministically, but avoiding them removes a whole bug class.)
- Invariant to test: `hash(canonicalize(x))` must equal a stored golden
  vector; fuzz unicode/number edge cases against RFC 8785 Appendix tests.

## 3. Hash chain (L1)

```ts
const H = (tag: string, b: Uint8Array) =>
  crypto.subtle.digest("SHA-256", concat(utf8(tag), b));

entryHash = H("pl/entry/v1", concat(utf8(chain_id), u64be(seq), u64be(prev_len), utf8(prev_hash_hex), canonicalBytes));
```

- SHA-256 via WebCrypto (native, FIPS-validated in most stacks) or
  `@noble/hashes` for BLAKE3/SHA-512 needs. Do not hand-roll hashes.
- `prev_hash` binds order; `seq` makes gaps detectable even if someone
  recomputes hashes (a recomputed chain is still a *different* chain —
  checkpoints are what make that visible, §4/§5).
- Store: `hash`, `chain_id`, `seq`, `ts`, canonical bytes (or their digest +
  envelope JSON), signature (§5 if L2+).

**What L1 gives:** per-writer event integrity + order + tamper-evidence vs
accidental edits and unsophisticated tampering. It does NOT stop a DB admin
from rewriting the whole chain unless checkpoints (§4) are signed/published.

## 4. Merkle batches + signed checkpoints (L2)

Batch events (e.g., every N events or T minutes) into a Merkle tree using
RFC 6962-style node hashing (leaf prefix `0x00`, node prefix `0x01`):

```ts
leaf(i)   = H("pl/leaf/v1", entryBytes_i);           // 0x00-equivalent via tag
node(l,r) = H("pl/node/v1", concat(l, r));
```

Checkpoint (C2SP `tlog-checkpoint` text format — copy it; it's designed for
this and supported by witnesses):

```
example.com/proof/tenant-7f3a/main
41207
b5bb9d8014a0f9b1d61e21e796d78dccdf1352f23cd32812f4850b878ae4944c
— example.com/proof k2026 8f2a…(Ed25519 sig)
```

- Sign the checkpoint body with Ed25519 (or ECDSA P-256 if FIPS-only
  environments demand it) via KMS. Keep the raw signed note text — it is the
  verification artifact.
- Inclusion proof for event `seq` = Merkle path from its batch leaf to the
  checkpoint root + (batch range, seq→leaf mapping). Consistency proof links
  checkpoint N to N+1. Both are tiny (log₂ N) and cheap to serve.
- Batching choice: 1–10 min or 100–1000 events. Smaller = fresher proofs;
  larger = fewer checkpoints to witness/anchor.
- **Tree format — pick ONE, copy it verbatim.** If checkpoints will be
  C2SP/RFC 6962-style (recommended, witness-compatible), implement the
  Merkle Tree Hash exactly per RFC 6962 §2.1
  (https://www.rfc-editor.org/rfc/rfc6962#section-2.1): the recursive MTH
  with the odd-node split at `k = largest power of two < n`. That split is
  what makes inclusion AND consistency proofs well-defined; a hand-rolled
  "balanced" variant breaks consistency proofs between arbitrary sizes.
- `@openzeppelin/merkle-tree` uses a different "standard" tree (sorted pairs,
  no 0x00/0x01 domain separation) — its proofs do NOT verify against an
  RFC 6962/C2SP root. Use it for app-local Merkle features (allowlists,
  revocation trees for EAS), not for your published checkpoints.
- Full transparency-log infrastructure (Tessera, rekor-tiles) is for L3+
  (§5) — you don't need a log server to do L2.

## 5. Publication & witnessing (L3)

A signed checkpoint still allows the operator to show different histories to
different parties (split-view). Fix by making checkpoints *observable*:

1. **Mirror**: publish every checkpoint (note text + signatures) to
   append-only public-ish storage: object storage with versioning +
   object lock, a static site/CDN, or your transparency log. A mirror *you*
   operate raises the cost of silent rewriting and protects against
   accidents — it is **not** an independent witness, because the operator
   controls it. Non-equivocation comes only from witnesses you don't
   control (next item).
2. **Witnesses**: ≥1 independent party cosigns each checkpoint after checking
   consistency with the last one it saw (C2SP `tlog-witness` protocol; the
   WhatsApp/Cloudflare KT deployment is the production template — operator
   and auditor are different companies). A verifier that sees a quorum of
   witness cosignatures is protected against split-view.
3. **Monitors/gossip**: a cron job (or your users' verifier) watches for two
   inconsistent checkpoints with the same origin — this is the alarm.
4. Simplest credible ops: publish checkpoints to GitHub (signed commits) or
   an append-only S3 bucket *and* have one external partner run a witness.
   Formal option: run a log with Tessera and join a witness network.

## 6. Keys, signing, rotation

- **Algorithms**: Ed25519 (fast, small) default; ECDSA P-256 where FIPS
  compliance requires; ML-DSA-44 only where the C2SP/cosignature stack is
  used (spec recommends it for PQC-readiness). Version every key (`key_id`).
- **Holding keys**: cloud KMS (AWS KMS / GCP KMS / Azure Key Vault), or
  `age`/PKCS#11/HSM for self-hosted. Serverless/edge: sign via KMS API
  (network hop per signature is acceptable at checkpoint cadence; batch
  entries under one checkpoint signature).
- **Key registry table** (mutable, versioned): `key_id, alg, public_key,
  valid_from, valid_to, revoked_at, trust_notes`. Verification trusts the
  *registry state as of the event time* — never a "current keys" view.
- **Rotation**: new key `valid_from` = rotation time; old key stays valid for
  verification of old checkpoints. Re-signing history is forbidden; instead
  the *next* checkpoint is signed by the new key and carries the previous
  checkpoint's hash + old-key signature (cross-sign the handover).
- **Compromised key**: rotate; publish a signed statement naming the
  compromise window; verifiers treat events in that window as
  authorship-uncertain. This is why authorship claims must say "signed by
  key K" not "done by person P".

## 7. External anchoring adapters (L4)

Interface:

```ts
interface AnchorAdapter {
  anchor(checkpoint: Checkpoint): Promise<AnchorReceipt>;
  receipt(receipt_id: string): Promise<AnchorReceipt | null>; // for upgraders
  verify(receipt: AnchorReceipt): Promise<boolean>;           // offline-verifiable preferred
}
```

- **OpenTimestamps** (https://opentimestamps.org/, existence-time, free): submit
  `sha256(checkpoint)` to
  calendars; upgrade to a Bitcoin-attested `.ots` proof (~60 min typical;
  can stall hours–days in high-fee windows — calendars batch on a budget;
  official Python CLI v0.7.2 is the maintained path; the official npm
  `opentimestamps` is stale since 2021 — evaluate TS third-party clients for
  maintenance status before adopting). Verification is offline against a
  Bitcoin block header (light-client via Esplora endpoints is common).
- **RFC 3161 TSA** (legal-grade existence time): timestamp the checkpoint
  hash with a qualified TSA (eIDAS qualified timestamps carry legal
  presumption in the EU; cheap per-call). Costs per stamp; retention is
  governed by the TSA's practice statement (ETSI EN 319 421-1) — check
  replay/verification horizons before relying on long-tail disputes. Good
  when disputes go to court.
- **Ethereum-ecosystem anchoring / attestations**:
  - *Root anchoring*: store `sha256(checkpoint)` via a plain transaction or
    an EAS **offchain attestation** whose revocation/status tree is anchored
    onchain — L2 gas is typically cents-to-dollars per batch (verify current
    gas before committing); you also carry wallet/RPC/key-management burden.
  - *EAS onchain attestations*: only when you need composability with the
    onchain ecosystem (schemas, resolvers, revocations). It proves "address A
    asserted X at block B" — authorship of the *assertion*, not truth of it.
- **Direct chain writes** (e.g., per-event): almost never justified for SaaS
  (cost/latency/PII-permanence); anchor checkpoints, not events.
- All adapters are swappable (I8): the proof bundle records
  `anchor: {provider, receipt, verified_at}`; switching providers adds new
  receipts for newer checkpoints and never invalidates old ones.

## 8. Proof bundle (what a verifier receives)

```
proof-bundle:
  envelope          (canonical JSON of the event, v-pinned)
  entry_hash        sha256:…
  batch: { range:[seq0,seq1], merkle_root, leaf_index, path:[…] }
  checkpoint: { note_text, signatures:[{key_id, sig}] }        // L2
  witness_cosignatures: [{name, key_id, sig, ts}]               // L3
  anchor: { provider:"ots|rfc3161|eas", receipt: … }            // L4
  chain_head_ref: { checkpoint_at_export, consistency_proof }   // freshness
```

Verifier flow (pure, offline where possible):
1. Recompute `entry_hash` from envelope bytes (I1) — payload digest check
   against app DB happens app-side.
2. Verify Merkle path to `merkle_root` under the batch.
3. Parse checkpoint note; verify the log signature against the key registry
   **as of checkpoint time**; verify consistency proof to the exported head.
4. Verify witness cosignatures (quorum policy) — else claim level = L2.
5. Verify anchor receipt (e.g., OTS proof vs block header) — else no
   existence-time claim.
6. Output a verdict per property: integrity ✓/✗, order ✓, authorship
   {key K}, existence ≤T, non-equivocation {witnessed, N of M}, availability
   n/a, truthfulness **not covered**.

## 9. Storage schema (generic SQL)

```sql
-- proof layer: INSERT-only (I3)
CREATE TABLE proof_events (
  chain_id   TEXT NOT NULL,
  seq        BIGINT NOT NULL,
  ts         TIMESTAMPTZ NOT NULL,
  type       TEXT NOT NULL,
  actor_kind TEXT NOT NULL,
  actor_id   TEXT NOT NULL,
  key_id     TEXT NOT NULL,
  payload_digest TEXT NOT NULL,        -- digest only (I5)
  payload_ref    TEXT NOT NULL,
  supersedes_seq BIGINT NULL,          -- rectification pointer
  canonical_hash TEXT NOT NULL,        -- entry_hash (§3)
  envelope       JSONB NOT NULL,       -- canonical envelope (v-pinned)
  signature      BYTEA NULL,           -- per-event sig if used (optional; L2 checkpoints usually suffice)
  PRIMARY KEY (chain_id, seq),
  UNIQUE (chain_id, canonical_hash)
);

CREATE TABLE proof_checkpoints (
  chain_id TEXT NOT NULL,
  size     BIGINT NOT NULL,            -- seq at checkpoint
  root_hash TEXT NOT NULL,
  note_text TEXT NOT NULL,             -- exact signed bytes (C2SP format)
  key_id   TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (chain_id, size),
  UNIQUE (chain_id, root_hash)
);

CREATE TABLE proof_anchors (           -- L4 receipts; provider-swappable
  chain_id TEXT NOT NULL, size BIGINT NOT NULL,
  provider TEXT NOT NULL, receipt_id TEXT NOT NULL,
  receipt   JSONB NOT NULL, verified_at TIMESTAMPTZ NULL,
  PRIMARY KEY (chain_id, size, provider)
);

CREATE TABLE proof_keys (              -- mutable by design (registry)
  key_id TEXT PRIMARY KEY, alg TEXT NOT NULL, public_key TEXT NOT NULL,
  valid_from TIMESTAMPTZ NOT NULL, valid_to TIMESTAMPTZ NULL,
  revoked_at TIMESTAMPTZ NULL, notes TEXT
);

CREATE TABLE proof_witnesses (         -- cosignatures collected (L3)
  chain_id TEXT NOT NULL, size BIGINT NOT NULL,
  witness_name TEXT NOT NULL, key_id TEXT NOT NULL,
  sig TEXT NOT NULL, ts TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (chain_id, size, witness_name)
);
```

- Enforce INSERT-only: separate DB role for the proof writer without
  UPDATE/DELETE; app-layer guards too. Admin-level rewrite is the threat the
  checkpoint/witness layer detects — don't pretend SQL grants stop admins.
- **No-DB variant** (small tenants/serverless): the chain *is* the envelope
  list (e.g., per-tenant append-only files / object keys
  `chains/<tenant>/000041.jsonl` + `checkpoints/<size>.note`), Merkle batch
  computed on write. Same invariants; different storage.

## 10. Concurrency, idempotency, sequencing

- **One sequencer per chain.** In serverless: a queue/actor per tenant (e.g.,
  SQS FIFO with content-based dedupe, Cloudflare-style Durable Object, or a
  Postgres advisory lock) assigns `seq` and computes `prev_hash`
  transactionally:
  ```sql
  INSERT INTO proof_events(chain_id, seq, …)
  VALUES (:chain,
    (SELECT COALESCE(MAX(seq),0)+1 FROM proof_events WHERE chain_id=:chain),
    …);
  ```
  with the `UNIQUE (chain_id, seq)` constraint as the backstop; retry on
  conflict (idempotent because envelope content is identical).
- **Idempotency key**: every agent action carries a client-generated
  `request_id`; a `UNIQUE (chain_id, request_id)` on a mapping table (or on
  `proof_events.attrs`) makes retries safe. Duplicate submission = return the
  original receipt; never a second event.
- **Ordering guarantee honesty**: chain order = sequencer acceptance order.
  Concurrent user edits serialize at the sequencer; the app DB's row version
  remains the business truth. Clock skew only affects `ts` display, not
  order (order is `seq`, not timestamp).
- **Gap repair**: if a crash leaves a gap (possible only with broken
  constraints), the *next* checkpoint will not cover the gap — alarms fire.
  Recovery is an operational runbook, never a silent fill (I4).
- **Batching job**: idempotent — recomputing a batch for `size` must produce
  byte-identical output; store `proof_checkpoints` with UNIQUE
  `(chain_id, size)`.

## 11. AI-agent actor model (authorship for agents)

- Agents are **first-class actors**: `actor:{kind:"agent", id, key_id}`.
  Per-agent or per-agent-class keys (KMS-held); agents request signatures,
  never hold material (I6). Lost/leaked agent key = rotate + compromise
  statement (§6), and its events remain attributable to the key, not the
  human.
- **Human confirmation**: irreversible, financial, or out-of-scope actions
  require a `human_approval` event signed by a user-kind actor, referenced by
  the agent event (`approval_ref`). AP2 formalizes this pattern as open/closed
  mandates with `cnf`-bound agent keys — copy the shape even outside payments.
- **Tool-call provenance**: record `tool`, `tool_call_id`, input digest,
  output digest, and model/artifact identity (e.g., Sigstore-signed model
  version) in `attrs`. "Proof of work performed" = the signed receipt chain +
  checkpoint; it demonstrates *what the system recorded*, not that the task
  was done well (truthfulness stays out of scope).
- **Policy gates**: agent signing requests pass a policy check (scope, rate,
  allowed `type`s). Policy-as-code (OPA/CEL-style) evaluated before KMS sign;
  denials are themselves logged events.
- **Replay safety**: `request_id` idempotency (§10) + optional nonce in
  envelope for one-shot actions; verifiers reject duplicates.

## 12. Privacy, retention, GDPR interactions

- PII lives off-chain (I5). Event digests of personal data are still personal
  data (EDPB 02/2025): prefer digests of non-personal identifiers, or
  HMAC/keyed digests with per-tenant keys, so the on-proof value is unlinkable
  once the off-chain mapping is deleted (document the residual-risk analysis;
  DPIA where required). **State the tradeoff honestly:** a keyed/salted
  digest can no longer be recomputed by an external verifier who doesn't
  hold the key — the chain still proves the digest bytes are unaltered, but
  binding a fresh payload to that digest is only checkable on the operator's
  side. Document who holds digest keys and adjust the wording of any
  "independently verifiable" claim accordingly.
- **Rectification**: new `*.corrected` event with `supersedes_seq`; old event
  remains (that's the point of tamper-evidence); the *current view* resolves
  supersession chains. Expose "current as of T" queries app-side.
- **Erasure** (Art. 17): delete the off-chain payload + keyed-salt; the
  residual is a digest that no longer identifies anyone (assess honestly;
  EDPB: effectiveness must be shown). **Crypto-shredding** (destroy the
  per-record key of encrypted payloads) is the strong form; tradeoff: the
  proof of *what was changed* survives, content does not — state this in the
  product's privacy notice.
- **Retention**: define per-event-class retention; expiry jobs delete
  payloads + can publish a final "retention horizon" checkpoint that seals
  what remains. Log the deletion as an event (`type:"retention.pruned"`,
  referencing seq ranges) so the ledger explains its own holes.
- **Tenant isolation**: separate chains per tenant (`chain_id`), separate
  KMS keys where commercially warranted; bundle exports never mix tenants.

## 13. Migration, rollback, exit

- **Forward-only.** Schema changes bump envelope `v` and chain `type`
  schemas; old verifier versions keep working (they ignore unknown attrs,
  fail on unknown `v` — explicit, not silent).
- **Provider exit** (I8): stop anchoring with old provider, start with new;
  record both in `proof_anchors`; the chain itself is unchanged. Witnesses:
  add new witness keys via checkpoint extension lines + registry updates.
- **Ledger-DB exit** (e.g., leaving a managed ledger): export chain +
  checkpoints to the generic schema (§9); verify an end-to-end proof from the
  export; then cut over. This is why checkpoints must be *self-contained
  artifacts*, not provider-internal objects.
- **Disaster recovery**: checkpoints + key registry + witness signatures are
  the crown jewels — back them up cross-region with object lock; the event
  bodies can be rebuilt from app DB + envelopes only if envelopes were
  exported; otherwise the chain is reconstructible from checkpoints only
  down to the last covered size (state this in your DR doc honestly).
- **Rollback of code**: proof layer is append-only; a bad release is fixed by
  a new release, not by unwinding events. If a bug wrote wrong *content*,
  emit correction events (§12).

## 14. Verification tests (minimum suite)

1. **Golden vectors**: known envelope → expected canonical bytes + hash
   (commit the vectors; prevents accidental canonicalization drift).
2. **Tamper tests**: flip a payload byte → entry hash mismatch; drop an event
   → seq gap detected; rewrite history → consistency proof from pre-rewrite
   checkpoint fails.
3. **Fork/split-view drill**: sign two inconsistent checkpoints in a test →
   monitor must alarm; verifier with witness quorum must reject both.
4. **Key rotation test**: rotate mid-history; verify old and new checkpoints
   against registry-as-of-time.
5. **Anchor test**: OTS/TSA receipt verifies against public data; corrupt
   receipt fails.
6. **Load/idempotency**: duplicate submits (same `request_id`) produce one
   event; concurrent writers serialize without gaps.
7. **Offline verification**: bundle verifies on a machine with no access to
   the app DB (this is the product promise — test it literally).
