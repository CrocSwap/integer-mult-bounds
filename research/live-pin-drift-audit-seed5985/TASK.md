# Task card — live-byte source-pin drift audit (written before substantial computation)

Task ID / proposed scope key: drawn card `replay-runtime` (track verifier-engineering,
chooser OS nonce `5985f17ee9293abc98cbb69a85efb569`, scope key `a76657a85478d269d19f`),
scope **refined** as recorded below.

Base commit; exact predecessor and dependency heads:
- Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (origin/main at draw).
- Predecessors (read-only, credited): `research/exclusion-support-masks` (commit
  `d8029ee0`, "faster ExclusionCircuit.verify leave-two-out supports"),
  `research/exclusion-embedding-masks` (commit `d7d8bfcb`, "fold
  ExclusionCircuit.verify_embedding reverse masks into #2001", PR
  https://github.com/CrocSwap/integer-mult-bounds/pull/2001 ),
  `research/shared-point-digest` (records the open question "Pin repair is
  outside this tooling change"), `research/git-provenance-stream` (registered
  pin-validation tooling precedent), `research/skip-clones` (smallest
  falsifying instance; Chafik Boukhalfa).

Concrete object and question:
Every live-byte source pin `{repo-relative path: sha256}` recorded in JSON
manifests in this repository at base `0fdd7d82`. Question: which recorded pins
no longer match the bytes their path currently holds, which registered package
checks and frozen replays can be reproduced rejecting on those mismatches, and
which later commits touched each pinned file after its manifest froze?

Scope status: refined; reason: the drawn card asks whether one measured replay
bottleneck can be sped up without dropping coverage. The ExclusionCircuit.verify
speedups are already merged; this audits their coverage-retention side effect
(the card's own scope-change trigger names skipping coverage) and supplies the
missing explicit dependency invalidation. No optimizer or fixture is compared.

Existing restriction being changed (or exact claim being audited):
Audited premise: `check_sources`-style and `research_package.py` live-byte pin
checks assume pinned source bytes remain unchanged after freeze. The two merged
speedups changed `scripts/exclusion_circuit.py` bytes.

Method; explicit parameter ranges/candidate alphabet:
Stdlib-only enumeration rule (stated exactly in the README): take the JSON
manifests from the git-tracked inventory (`git ls-files`, `.json` extension
matched case-insensitively, this package excluded); every mapping entry whose
key matches
`^[A-Za-z0-9_.+-]+(/[A-Za-z0-9_.+-]+)+$`, contains no `:`, and whose value
matches `^[0-9a-f]{64}$` is one candidate pin. A pin is **drifted** when its
target exists in the working tree and `sha256(target bytes)` differs; a pin is
**unresolved** when its target does not exist at the pinned key (an alternate
vendor path is not substituted). Provenance: `git log <freeze>..HEAD -- <path>`
where `<freeze>` is the last commit touching the manifest. Impact census:
`scripts/research_package.py --package <each research/*/ package with SOURCES.json>
--check-only` classified pass / working-source drift / other; plus the exact
reproduction of `research/skip-clones/clone_io.py:check_sources`.

Nearest overlapping PRs and why this adds something:
No open PR or claim covers pin repair (entry overlap, refined terms "exclusion_circuit",
"source pin drift", "pinned source changed", "stale pin", "leave-two-out", "pin
manifest", complete pagination 2026-10-14 20:42Z: 8 matches, all the
exclusion-mask tooling packages and `research/shared-point-digest`'s "Pin repair
is outside this tooling change" open question). This adds the complete drift
ledger and provenance that the acknowledged follow-up needs.

Optimistic full cost budget; required observable improvement:
Not a construction: the observable is a complete, deterministic ledger
(enumeration rule + counts + per-pin verdicts + per-file provenance), one
reproduced failing check, and rejected controls. No wall-time claim.

Success evidence; falsification test; time/compute cap:
Success: `verify.py` recomputes the ledger from scratch and prints PASS with
stable counts; the skip-clones failure reproduces byte-exact. Falsification
controls: a corrupted digest must register as drift; a fabricated drift record
must reject; a pin whose bytes match must report clean. One session; the census
runs once and its receipt is pinned.

Predecessor authors; intended artifact and reproduction command:
Predecessors: Douglas Colkitt (tooling, research_package.py), Chafik Boukhalfa
(research/skip-clones), the exclusion-mask tooling authors (PR
https://github.com/CrocSwap/integer-mult-bounds/pull/2001 and the two mask
packages), the shared-point-digest author (open question). Artifact:
`research/live-pin-drift-audit-seed5985/` with `verify.py` and pinned receipts.
Attribution: Aaron Wang, with help from opencode. Apache-2.0.

Session record: branch `research/agent-42-pin-drift-audit-5985f17e`. No advance
CLAIM was posted to the discussion board (the bounded audit ran within one
session); the completed result is reported as FINDING/DONE, not as a
retrospective reservation.
