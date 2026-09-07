# Proof-ledger landscape — OSINT & due-diligence report (as of 2026-09-07)

Companion to `SKILL.md` in this pack. This file is the dated evidence base for
mechanism choices. Every time-sensitive claim carries its access date (all items
accessed **2026-09-07/08** unless noted). Re-run the re-research queries in §10
before relying on versions, deployment status, or dates older than ~90 days.

---

## 1. Executive conclusions

1. **The mechanism ladder, not blockchain, is the 2026 mainstream.** The most
   active, best-maintained infrastructure is *transparency-log* infrastructure
   (Merkle append-only logs + signed checkpoints + independent witnesses):
   Tessera (GA), Rekor v2 (GA, opt-in), C2SP specs (stable v1.0.0), and two
   production-scale proofs of the pattern (Certificate Transparency; WhatsApp
   key transparency with Cloudflare as independent auditor). Public-chain
   anchoring is a cheap add-on for existence-time (OpenTimestamps), not a trust
   substrate by itself.
2. **Managed "ledger databases" are a churn zone.** AWS QLDB reached end of
   support **2025-07-31**; Azure **deprecated Managed CCF** (docs 2025-07-31)
   and moved customers to Azure confidential ledger. Do not build a product's
   trust story on a single-vendor ledger DB whose EOL is announced mid-life;
   design the proof layer as a replaceable projection (see
   `implementation-patterns.md` §9).
3. **Hashes beside data ≠ tamper-evidence.** Verified counterexamples:
   CloudTrail digest chains are signed with keys **held by AWS** (first-party);
   Luckin's fraud included a **fake operations database** — every self-hosted
   chain records whatever the operator feeds it. Independent verification
   (witnesses, external anchors, external auditors, third-party data) is what
   upgrades L1→L3.
4. **For AI agents specifically:** deterministic canonical event envelopes +
   per-actor signing keys (ideally KMS-held, never in the agent's own hands) +
   signed mandates/receipts are converging into standards (AP2 → FIDO Alliance
   2026-04-28; "Verifiable Intent" with Mastercard; MCP spec 2025-11-25).
   "Proof of work performed" = signed receipts + witnessed checkpoints;
   it is unrelated to mining Proof-of-Work.
5. **Privacy is a hard gate, now with regulator guidance.** EDPB Guidelines
   02/2025 (final v2.0 adopted **2026-07-07**): hashes of personal data remain
   personal data; store PII off-chain by design; erasure must be engineered
   (mutable source + supersession/tombstone + off-chain crypto-shredding);
   if you don't need blockchain-grade integrity, "look at other tools".
6. **Consortium chains are real only with real independence.** Fabric v3.1.5
   and ChainMaker v2.3.x are actively maintained, but a consortium of one
   owner with three nodes is a single point of trust with worse ops than a
   signed log. Minimum credible setup: ≥3 organizations with independent
   admin domains, jointly governed upgrade policy, each org able to audit
   independently (see §7).

---

## 2. Definitions used (property vocabulary)

These words are kept strict; the review checklist (`review-checklist.md`)
enforces them:

| Property | Precise meaning | Provided by (only by) |
|---|---|---|
| Event integrity | Bytes of an event are unmodified since recorded | Canonical hash chain / Merkle tree incl. proof |
| Order (within writer) | Events are sequenced, gaps/rewrites detectable | Sequence numbers inside hash chain |
| Authorship | A specific key asserted this event | Signature over canonical envelope |
| Existence time | Data existed by time T, provable to outsiders | External anchor (RFC 3161 TSA, OTS/Bitcoin, chain tx) |
| Non-equivocation | Signer cannot show different histories to different parties | Published checkpoints + witnesses / gossip (CT-style) |
| Availability | Verifiers can obtain data+proofs later | Your ops (mirrors, exports); ledgers do NOT give this |
| Confidentiality | Unauthorized parties can't read | Off-chain storage, encryption; chains/anchors give none |
| Truthfulness | The recorded event matches real-world facts | Nothing cryptographic; only cross-party validation, attestation design, audits |

**Core falsifier for any proposal:** name which row above each mechanism buys,
and who can check it *without trusting the operator*. If the answer is
"nobody", the mechanism is a logging format, not a trust mechanism.

---

## 3. Query matrix (search log, all accessed 2026-09-07/08)

| # | Query / action | Source type | Proves | Does NOT prove |
|---|---|---|---|---|
| Q1 | "Google Tessera transparency log Trillian successor" | vendor blog + repo | Tessera is the tlog-tiles successor; Trillian maintenance mode | nothing about non-CT ecosystems' adoption |
| Q2 | GitHub API `transparency-dev/tessera/releases/latest` | primary repo | latest release v1.0.4 (accessed 2026-09-07) | production deployments list |
| Q3 | "Sigstore Rekor v2 GA" + "Rekor evolution" (blog 2026-06-28) | vendor blog (primary) | Rekor v2 GA 2025-10-10; public-good stays on v1 default as of 2026-06; shard rotation via TUF | your own instance's requirements |
| Q4 | c2sp.org spec pages (tlog-tiles, tlog-checkpoint, signed-note, tlog-witness, tlog-cosignature) | standards body (primary) | wire formats, Ed25519 + ML-DSA-44 cosignatures, witness protocol | production witness availability |
| Q5 | opentimestamps.org + GitHub repos + npm `opentimestamps` | primary | official clients; npm JS lib last publish 2021-01-29 (stale); ops risk issue #116 (2026-06: digests pending >11 days in high-fee windows) | future calendar reliability |
| Q6 | GitHub API `codenotary/immudb` + LICENSE file | primary repo | v1.11.2 (2026-09-03), BUSL-1.1 (prod use OK, no competing hosted offering), 9k stars, active | third-party security audits of immudb (none public found) |
| Q7 | QLDB end-of-support notice (developer guide; note: the HTML guide page has been pulled — the notice is quoted verbatim in the archived devguide and the migration blog) + official migration blog + aws-samples migration repo | primary (AWS) | QLDB EOS 2025-07-31; official migration target Aurora PostgreSQL; no ledger semantics there | any "QLDB replacement" from AWS |
| Q8 | learn.microsoft.com confidential-ledger docs + Managed CCF migration page | primary (Microsoft) | Managed CCF deprecated (2025-07-31 docs); Azure confidential ledger current; ledger = 3+ instances in TEEs; receipts; CCF OSS | cross-cloud portability, pricing at your volume |
| Q9 | EAS docs site + eas-sdk npm | primary | onchain/offchain attestation flows, EIP-712, revocation, schemas; SDK 2.10.0 (2026-08-27) | your gas cost (varies); key-management burden |
| Q10 | holepunchto/hypercore README + docs.pears.com (2026-07) | primary repo | Hypercore v10 LTS signed append-only logs; multi-signer manifest/quorum; Pear rebrand | enterprise support offering |
| Q11 | docs.chainmaker.org.cn version table | primary (CN) | ChainMaker v2.3.10 docs (2026-08-31), active, 国密, TBFT/MAXBFT | independent security audits; western ecosystem |
| Q12 | hyperledger/fabric releases + LF Decentralized Trust 2026 annual review | primary | Fabric v3.1.5 (2026-06-18), v2.5 LTS, quarterly cadence | your consortium's governance maturity |
| Q13 | SEC Litigation Release LR-24987 (2020-12-16) + SEC press 2020-319 + SDNY final judgment (Justia) + Luckin investor PR | primary (regulator/court/company) | Luckin facts in §6 below | any blockchain claims (none in SEC docs) |
| Q14 | 3news.cn (2022-10-31) report of Luckin SVP presentation; Q2-2022 earnings-call mention | secondary press | Luckin's "区块链业财增信" project on ChainMaker; phase 1 self-anchoring, phase 2 third-party cross-checks | company primary transcript — treat as UNVERIFIED-first-party |
| Q15 | EDPB Guidelines 02/2025 PDF (v2.0, 2026-07-07) + adoption news 2025-04-14 | primary (regulator) | positions in §8.1 | binding law (guidelines ≠ regulation) |
| Q16 | NIST CSRC log-management pages | primary | SP 800-92r1 still Draft (IPD 2023-10-11; page updated 2025-11-20); SP 800-92 (2006) final | final r1 text |
| Q17 | modelcontextprotocol.io versioning + changelogs | primary | current MCP revision 2025-11-25 | future revisions (recheck) |
| Q18 | sigstore/model-transparency releases + PyPI | primary | model-signing 1.1.1 (2025-10-10), Apache-2.0, in-toto bundles | adoption numbers |
| Q19 | digital-strategy.ec.europa.eu AI Act pages + enforcement page (updated 2026-08-24) | primary (EU) | dates in §8.2 | your classification (get legal advice) |
| Q20 | Google blog 2026-04-28 (AP2 → FIDO), ap2-protocol.org, AP2 spec, a2a-x402 spec v0.2 | primary | AP2 v0.2, mandates as SD-JWT VDCs, agent key `cnf` claim, receipts; "Verifiable Intent" (Mastercard) donated to FIDO | production deployments |
| Q21 | npm registry API: @noble/hashes, @noble/curves, @openzeppelin/merkle-tree, merkletreejs, eas-sdk | primary registry | versions/licenses in §5 table | code-level review of each |
| Q22 | engineering.fb.com WhatsApp KT (2023-04-13); Cloudflare blog (2024-09-24); NCC Group AKD review | primary vendor + audit firm | KT deployed at scale with independent auditor (Plexi); NCC Group implementation review 2023 | long-term auditor continuity commitments |
| Q23 | docs.aws.amazon.com CloudTrail log-file validation pages | primary (AWS) | hourly SHA-256 digest files, SHA256withRSA signed by **AWS-held** keys, chained digests | any third-party verifiability beyond AWS's own keys |

Known gaps (stated honestly): we did not find public third-party security
audits for immudb or for the OTS calendar fleet; we did not verify EAS gas
prices at write time; C2SP witness-network operational status (which
independent witnesses are up) was not enumerated — treat witness availability
as a deployment-time check.

---

## 4. Transparency-log stack (L2/L3 core infrastructure)

### 4.1 Tessera — `transparency-dev/tessera`
- **What:** Go library for tile-based transparency logs (C2SP tlog-tiles).
- **Status:** GA announced 2025-09-22; production-ready since beta v0.2.0
  (2025-06-12). Latest release **v1.0.4** (accessed 2026-09-07). Witness
  support ✅; drivers: GCP, AWS, MySQL, POSIX.
- **Why it matters:** this is the maintained successor lineage of Trillian
  (`google/trillian` is explicitly in **maintenance mode**, repo notice;
  3.7k stars, last push 2026-09-02). CT, Sigstore, Go checksum db, Pixel
  Binary Transparency are the lineage's deployments.
- **Limits:** Go-only; you run the log (storage + signer + witness gossip are
  your ops). License Apache-2.0.
- URLs: https://github.com/transparency-dev/tessera ·
  https://blog.transparency.dev/introducing-trillian-tessera ·
  https://github.com/google/trillian

### 4.2 Rekor v1 / v2 — Sigstore
- **What:** public signature-transparency logs; v2 = `sigstore/rekor-tiles`
  on Tessera.
- **Timeline (primary blog):** alpha 2025-04-17 → GA **2025-10-10** →
  2026-06-28 "Rekor evolution": public-good instance **keeps Rekor v1 as the
  default signing log** for the foreseeable future (PQC transition pending);
  Rekor v2 runs in production (99.5% SLO), opt-in; log shard URLs rotate
  ~6 months and are distributed via TUF `SigningConfig` — never hardcode
  shard URLs. Cosign 2.6.0+ and Go/Python/Java clients support v2.
- **Lesson for SaaS:** even the most mature transparency ecosystem ships
  shard rotation + TUF-style config distribution; copy that pattern
  (checkpoint URLs and keys must be rotatable config, not constants).
- URLs: https://blog.sigstore.dev/rekor-v2-alpha/ ·
  https://blog.sigstore.dev/rekor-v2-ga/ ·
  https://blog.sigstore.dev/rekor-evolution/ ·
  https://github.com/sigstore/rekor-tiles

### 4.3 C2SP specs (the wire formats to copy)
- `tlog-checkpoint` v1.0.0: origin / size / root-hash lines (RFC 6962 tree);
  logs MUST NOT sign inconsistent checkpoints; ML-DSA-44 cosignatures
  recommended (PQC-ready).
- `signed-note` v1.0.0: text format, signature types incl. Ed25519 (0x01),
  ECDSA P-256 (0x02), timestamped cosignatures (0x04/0x06 ML-DSA-44).
- `tlog-tiles`: static HTTP API for tiles/entry-bundles — cheap to serve from
  object storage/CDN (this is why "static CT" works on static hosting).
- `tlog-witness`: HTTP protocol for witness cosigning (`add-checkpoint` with
  consistency proof; witness tracks max consistent size per origin).
- `tlog-cosignature` v1: "as of time T, largest consistent tree head I
  observed for origin O has root R" — the precise non-equivocation primitive.
- URLs: https://c2sp.org/tlog-tiles · https://c2sp.org/tlog-checkpoint ·
  https://c2sp.org/signed-note · https://github.com/C2SP/C2SP

### 4.4 Production existence proof of witnessing — WhatsApp KT + Cloudflare Plexi
- WhatsApp deployed key transparency (Auditable Key Directory; CONIKS /
  SEEMless / Parakeet lineage) in production, blog 2023-04-13; NCC Group
  implementation review of AKD (2023, findings fixed).
- Cloudflare operates an independent **auditor** ("Plexi") that cross-signs
  epochs and publishes verification results (blog 2024-09-24). Pattern to
  copy: log operator ≠ witness; witnesses keep only latest consistent
  checkpoint per origin — cheap, scalable, privacy-preserving.
- URLs: https://engineering.fb.com/2023/04/13/security/whatsapp-key-transparency/ ·
  https://blog.cloudflare.com/key-transparency/

### 4.5 Small TS libs for your own L1/L2 (not the log itself)
- `@noble/hashes` **2.4.0** (2026-08-27), MIT, zero deps — SHA-2/SHA-3/BLAKE.
- `@noble/curves` **2.4.0** (2026-08-27), MIT — Ed25519/P-256 etc.
- `@openzeppelin/merkle-tree` **1.0.8** (2025-02-19), MIT, 536 stars; solid
  standard Merkle trees (used by EAS SDK ≥1.0.7); not a transparency log.
- `merkletreejs` **0.6.0** (2025-09-15), MIT — popular but depends on
  `crypto-js` (check your supply-chain policy).
- **Honest default:** a correct RFC 6962-style Merkle tree is ~80 lines
  (leaf/node domain separation); hand-rolling with `@noble/hashes` is often
  the *stronger* choice because the verification code you ship is the audit
  surface. Do NOT pull a framework to hash.
- Registry access date: 2026-09-07.

---

## 5. Verifiable / immutable DBs and managed ledgers

| Option | Status 2026-09 (accessed 2026-09-07) | License / model | Trust upgrade over L1 | Verdict |
|---|---|---|---|---|
| **immudb** (`codenotary/immudb`) | v1.11.2 (2026-09-03), active, 9.0k stars | **BUSL-1.1** (prod use OK; may not offer competing hosted/embedded product) | Inclusion/consistency proofs + server signing of state; still **single-operator** | Good self-hosted L1/L2 substrate; adds DB-level proofs, not multi-party trust |
| **AWS QLDB** | **End of support 2025-07-31** (official notice: "Existing customers will be able to use Amazon QLDB until end of support on 07/31/2025" — quoted verbatim in the QLDB developer guide as retrieved 2026-09-07; the HTML guide page now 404s, evidence preserved in the migration blog + migration repo); official migration path: Aurora PostgreSQL via aws-samples tooling. URLs: https://aws.amazon.com/blogs/database/migrate-an-amazon-qldb-ledger-to-amazon-aurora-postgresql/ · https://github.com/aws-samples/example-qldb-ledger-migration | — | — | Do not start here; if you're on it, migrate and keep proofs app-level |
| **Azure confidential ledger** | Current; Confidential Computing Ledger platform (customer-managed workload); **Managed CCF deprecated** (docs 2025-07-31) | managed | CCF consensus across **3+ enclaved instances** + receipts; TEE attestation | Credible single-vendor option when TEE-anchored trust is acceptable; still one cloud operator |
| **CloudTrail digest validation** (pattern reference) | current official docs | managed | Hourly SHA-256 digests, SHA256withRSA **signed by AWS**, digest chaining | Teaches the right mechanics but key = provider's; claims must say "AWS-signed", not "independently verifiable" |
| **immudb-style + your L3 checkpoint** | — | — | Combining an embeddable log with external witnessing is usually cheaper than any of the above | Recommended default shape |

**Database integrity ≠ multi-party consensus.** A ledger DB proves "these
bytes, once written by the operator, were not altered since" to whoever trusts
the operator's key. Only witnesses, external anchors, or genuinely independent
consortium members upgrade who can check it.

---

## 6. Case study: Luckin Coffee (verified facts vs retellings)

**Verified, primary sources (SEC / court / company):**
- SEC Litigation Release **LR-24987**, 2020-12-16; *SEC v. Luckin Coffee Inc.*,
  No. 1:20-cv-10631 (S.D.N.Y.): Luckin agreed to pay a **$180M penalty**,
  without admitting or denying, to settle charges of materially misstating
  revenue/expenses/net loss. The complaint alleges that from at least **April
  2019 through January 2020** Luckin "intentionally fabricated more than
  $300 million in retail sales" via related parties under three purchasing
  schemes, and that employees concealed the fraud by inflating expenses by
  more than **$190M**, **creating a fake operations database**, and altering
  accounting and bank records. Revenue overstated ~28% (Q2 2019) and ~45%
  (Q3 2019); >$864M raised during the fraud period.
- SEC press release 2020-319 (same date) adds: misconduct was **discovered in
  the course of the annual external audit**; Luckin self-reported,
  cooperated, terminated personnel.
- Final judgment (S.D.N.Y., 2021-02-04, Justia copy) confirms the $180M civil
  penalty and permanent injunctions (10(b), 17(a), 13(a), 13(b)(2)).
- ADSs traded on Nasdaq until 2020-07-13 (per SEC release); Cayman provisional
  liquidation (Joint Provisional Liquidators appointed 2020-07-15).
- URLs: https://www.sec.gov/enforcement-litigation/litigation-releases/lr-24987 ·
  https://www.sec.gov/newsroom/press-releases/2020-319 ·
  https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1:2020cv10631/550751/14/ ·
  https://investor.luckincoffee.com/news-releases/news-release-details/luckin-coffee-reaches-settlement-us-securities-and-exchange

**Secondary, label as such:** Chinese industry press (3news.cn, 2022-10-31)
reports that Luckin's SVP presented a "区块链业财增信" (blockchain
business-finance credibility) project — first disclosed on the **Q2 2022
earnings call** per that report — implemented on **ChainMaker**, phase 1 =
on-chain anchoring of key self-operated/franchise sales data (self-attestation),
phase 2 = bring payment/delivery/supplier **third parties on-chain** for
cross-verification. We did not locate the primary transcript; treat as
UNVERIFIED-first-party. URL: https://www.3news.cn/pindao/2022/1031/102022_780914.html

**What the case actually teaches (supported by the primary facts):**
1. The fraud included a **fake operations database**. Any hash chain, Merkle
   log, or blockchain operated by the same humans would have faithfully
   anchored the fabricated data. Ledger ≠ truth (oracle problem).
2. Detection came from **independent external audit**, not from internal
   cryptography. The value is cross-checking *between independent parties*,
   which is exactly what phase 2 of Luckin's (reported) roadmap concedes.
3. Press retellings that claim "blockchain would have prevented Luckin" are
   unsupported by the primary record. Do not cite such claims.
4. A single company running a consortium-shaped chain is one owner with three
   nodes — the trust model is unchanged even if the tech stack says
   "blockchain".

---

## 7. Consortium / permissioned ledgers (L5)

- **Hyperledger Fabric** (LF Decentralized Trust): v3.1.5 released
  **2026-06-18**; v2.5 LTS maintained; quarterly maintenance cadence; 2026
  annual review reports v3.x in active production use. URLs:
  https://github.com/hyperledger/fabric/releases ·
  https://lf-decentralized-trust.github.io/governance/project-updates/2026/2026-annual-Hyperledger-Fabric/
- **Besu**: now under `besu-eth/besu`; releases 26.x roughly monthly
  (26.8.1 current, 2026-09-01; recent 26.x releases fixed security
  vulnerabilities) — patch-fast culture, treat as a fast-moving
  dependency. URL: https://github.com/besu-eth/besu/releases
- **ChainMaker (长安链)**: docs v2.3.10 (2026-08-31) show active development;
  built by Beijing Academy of Blockchain and Edge Computing (微芯研究院) with
  Tsinghua/BUAA/Tencent/Baidu/JD; 国密 (SM2/SM3/SM4) support; consensus
  TBFT/MAXBFT/RAFT; used in CN supply-chain-finance / traceability programs.
  Ecosystem is China-centric; SDKs Go/Java/Node/Python. URLs:
  https://docs.chainmaker.org.cn/ · https://chainmaker.org.cn/
- **When L5 is real:** ≥3 organizations with independent administrative
  domains and business reasons to check each other; jointly governed upgrade
  and key policies; every member runs validators and can independently
  verify (recompute) the ledger; a written dispute process. **When it is
  theater:** one vendor or one company owns all nodes ("BaaS shared edition"
  offerings — e.g., AntChain traceability shared edition docs describe
  4 nodes uniformly operated by the vendor — are a vendor service, not a
  consortium you control).

---

## 8. Regulation & compliance (dated, with recheck duty)

### 8.1 EDPB Guidelines 02/2025 — personal data through blockchain
- v1.0 adopted 2025-04-08 (public consultation); **final v2.0 adopted
  2026-07-07**. URLs: https://www.edpb.europa.eu/documents/guideline/guidelines-on-processing-of-personal-data-through-blockchain-technologies_en ·
  PDF: https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202502_blockchain_v2_en.pdf
- Positions SaaS architects must honor:
  - Personal data (incl. **salted/keyed hashes** and, generally, anything
    linkable) should not be written on-chain; store payloads off-chain
    (their Recommendation: off-chain storage).
  - Erasure/rectification must be engineered from design phase; "technical
    impossibility" is not a defense. Mutable source of truth + append-only
    supersession/tombstone events is the compliant shape.
  - Cryptographic commitments and crypto-shredding are discussed as
    mitigation techniques; effectiveness must be demonstrated per case.
  - DPIA expected for high-risk processing. If blockchain-grade integrity is
    not actually needed, EDPB explicitly suggests using other tools — a
    regulatory nudge matching this skill's kill criteria.

### 8.2 EU AI Act (Regulation (EU) 2024/1689) — dates as enforced 2026-09
Primary: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai ·
https://digital-strategy.ec.europa.eu/en/policies/enforcement-ai-act (updated 2026-08-24).
- GPAI provider obligations applicable since **2025-08-02**; Commission/AI
  Office **enforcement powers active since 2026-08-02** (fines up to €15M/3%).
- Article 50 transparency duties (incl. machine-readable marking of synthetic
  content) apply from **2026-08-02** (grace until 2026-12-02 only for
  systems placed on market before 2026-08-02).
- Digital Omnibus (adopted 2026-06-16) moved Annex III high-risk obligations
  to **2027-12-02** (Annex I embedded: 2028-08-02). Article 12 (automatic
  logging by design, over the system lifetime; Art. 18: ~10-year retention
  floor) binds high-risk systems at those dates.
- **Skill relevance:** log-by-design + tamper-evidence ("append-only storage,
  signed event streams, or Merkle-anchored batches") is the practical answer
  assessors expect for log integrity; our L1–L3 ladder is the generic
  implementation. Re-check classification with counsel; do not self-scope.

### 8.3 NIST
- SP 800-92r1 "Cybersecurity Log Management Planning Guide" is **still an
  initial public draft** (IPD 2023-10-11; CSRC page updated 2025-11-20 still
  lists Draft). Cite SP 800-92 (2006) as final; track r1 finalization.
  URL: https://csrc.nist.gov/Projects/log-management/publications

---

## 9. AI-native angle (2026 evidence)

- **MCP**: current spec revision **2025-11-25** (versioning doc; recheck for
  newer revisions). URL: https://modelcontextprotocol.io/docs/2025-06-18/learn/versioning
- **AP2 (Agent Payments Protocol)**: announced 2025-09-16 by Google +
  payments industry; **donated to the FIDO Alliance 2026-04-28**; AP2 v0.2
  adds "Human Not Present" flows. Mandates = SD-JWT-based Verifiable Digital
  Credentials (open/closed Checkout & Payment mandates), agent key bound via
  `cnf` claim, merchant/processor **signed receipts**, mandate hash-chaining
  for dispute evidence. URLs: https://ap2-protocol.org/ ·
  https://github.com/google-agentic-commerce/AP2/blob/main/docs/ap2/specification.md ·
  https://blog.google/products-and-platforms/platforms/google-pay/agent-payments-protocol-fido-alliance/
- **Verifiable Intent** (Google + Mastercard, donated to FIDO 2026-04-28):
  "tamper-proof log of user-authorized agent actions" — same shape as our
  L1–L3 ladder, but scoped to agent commerce. Track it; do not invent a
  proprietary substitute if it fits.
- **x402 / A2A extension** (Coinbase et al.): on-chain payment payloads with
  nonce replay protection; useful as an *example* of signed, replay-safe
  agent payments. URL: https://github.com/google-agentic-commerce/a2a-x402/blob/main/spec/v0.2/spec.md
- **Model/artifact signing**: Sigstore `model-transparency`
  (`model-signing` 1.1.1, 2025-10-10, Apache-2.0) signs ML models as
  in-toto statements via Sigstore bundles (plus raw-key/cert/PKCS#11 modes).
  Use for "which model/weights produced this decision" provenance.
  URLs: https://github.com/sigstore/model-transparency ·
  https://pypi.org/project/model-signing/
- **Design invariants** (implementation details in
  `implementation-patterns.md` §11): agents are **actors with their own
  identities**, not root signers; every irreversible action = deterministic
  canonical envelope + human confirmation where mandated; signing keys in
  KMS/cloud HSM with policy, never in agent context; "proof of work
  performed" = signed receipts + witnessed checkpoint of the work log —
  nothing to do with mining PoW.

## 10. Expiry clause & re-research queries

This report is **valid for ~90 days** from 2026-09-08 for version/deployment
claims (standards and settled history — CT, RFC numbers, Luckin SEC record —
do not expire). Before each production use, re-run:

```bash
# releases
gh api repos/transparency-dev/tessera/releases/latest --jq .tag_name
gh api repos/sigstore/rekor-tiles/releases/latest --jq .tag_name
gh api repos/codenotary/immudb/releases/latest --jq '.tag_name'
gh api repos/hyperledger/fabric/releases/latest --jq .tag_name
gh api repos/holepunchto/hypercore/releases/latest --jq .tag_name
# npm pins
npm view @noble/hashes version; npm view @noble/curves version
npm view @openzeppelin/merkle-tree version; npm view @ethereum-attestation-service/eas-sdk version
# protocol versions
curl -s https://modelcontextprotocol.io/docs/2025-06-18/learn/versioning | grep -i "current protocol version"
# EOL / deprecation sweeps
curl -s https://csrc.nist.gov/Projects/log-management/publications | grep -i "800-92"
curl -s https://learn.microsoft.com/en-us/azure/confidential-ledger/overview | grep -i -m2 "deprecat\|GA"
# search: "AWS QLDB end of support", "Azure confidential ledger", "Rekor v2 default",
#   "AP2 FIDO Alliance", "Verifiable Intent FIDO", "EDPB blockchain guidelines v2",
#   "MCP specification" latest revision, "AI Act Article 12" 2027
```

Treat any changed release, any new "deprecation" notice, and any MCP/AP2
revision as a trigger to re-read §4–§9 and update the ladder guidance.
