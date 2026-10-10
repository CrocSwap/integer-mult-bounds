# gen4-collective-families-283

**Conditional κ = 181572923056461298166587 / (25·10²⁵) = 7.26291692225845·10⁻⁴** (+1.80·10⁻⁷, +0.0248% over PR #283's
7.26111344123733·10⁻⁴; +0.473% over PR #276's gen4 word).

PR #283 (Dugongue) composes, on PR #276's gen4 bit word, sixteen terminal sinks, 741 response-kernel pivots, PR #279's
880 retimings, 29 of PR #280's transported entrances and its 440 early restorations, and 220 target-prefix squares.
This package adds **91 collective response-kernel families — 87 quadruples and 4 triples — on helpers that no part of
PR #283's construction touches**, all at PR #283's own global cut, with its code unchanged except one contained block
of the bank allocator.

* **Families.** A dirty helper p (the pivot) whose complete F₂ target response is the sum of the responses of three
  (or two) other untouched helpers (the donors), all four (three) sharing a common nondegenerate entrance subspace E
  inside their first required frames; the pivot starts at E (its compensation reads deleted), each donor pays
  d += p at E after the cut and d −= p at the full frame. The 91 are all-equal first-frame families entering on
  nearly the whole intersection: (3, 3, 3, 3) with e = 2 × 49, (5, 5, 5, 5) with e = 4 × 10, and families of first
  dimension 10–17 with e = r − 1 or r − 2; entrance rank 456, 14 donors shared along nested chains. They were found by
  a census of the 13,944 plain helpers of the gen4 word (low-weight F₂ circuits among the 12,352 distinct responses:
  3,158 triangles and 23,421 quadruples; common-frame filter; φ-ledger packing; `discovery/`), which first produced
  a 695-entry selection on the bare gen4 word (model κ 7.24029·10⁻⁴) and then the 91 disjoint from PR #283's 1,612
  kernel helpers, 16 sinks and 60 transported candidates.
* **Checks.** PR #283's chain, unchanged: the nine PR #276 stages, the sink, kernel (832 pivots, entrance rank 2,530
  with the transports, 13,136 reads removed, 3,462 gates, one-stage mass 425,358 → 422,388, all columns forward and
  inverse with omitted-operation controls), retiming, transport, restoration and target-square stages, the
  independent legality and prefix audits (1,464,320 kernel equalities on 1,956 helpers), the global columns (23,434),
  the bank review (literal stock 2,549,300, normalized 509,860), the price, the fixed-prime price and the finite
  invoice; every receipt regenerated and pinned.
* **The one code change.** PR #283's `code/banks.cpp` tiles a residual-r role as four r-blocks plus (30 − r) rank-4
  blocks per bank; the 91 families need 30,060 rank-4 filler copies and PR #283 leaves 10,380. The allocator now
  lets a residual group that would exhaust the rank-4 pool use rank-3 fillers instead (4r + 4b + 12k = 120, b =
  (30 − r) mod 3), with both remainders asserted; when the pool suffices the allocation is byte for byte PR #283's.
  In this word only PR #283's own 29 rank-19 transported entrances switch (pattern [6 × 4, 3 × 32] in 870 banks).
  Without that change, 25 of the families fit the pool as is and give 7.26226544·10⁻⁴ (variant kept in
  `discovery/families283_subset_rows.json`).

| | PR #283 | this package |
|---|---:|---:|
| kernel pivots / entrance rank (with transports) | 741 / 2,074 | **832 / 2,530** |
| one-stage paid rank mass | 425,358 → 422,844 | 425,358 → **422,388** |
| literal stock (120 replicas) / normalized | 2,551,580 / 510,316 | **2,549,300 / 509,860** |
| κ (fixed-prime price) | 7.26111344123733·10⁻⁴ | **7.26291692225845·10⁻⁴** |

Conditional, finite construction under the same retained public all-size hypotheses as PR #276/#283 (no Lean
certificate); the bit side binds. [PROOF.md](PROOF.md) states the delta; PR #283's notes are kept unchanged
(`README-PR283.md`, `PROOF-PR283.md` with one sentence on the tiling extended, `KERNEL-BANK-PROOF.md`, `SINK-PROOF.md`,
`RETIMING-PROOF.md`, `TRANSPORT-PROOF.md`, `RESTORATION-PROOF.md`, `TARGET-PROOF.md`, `ENDPOINT-REVIEW.md`, `REVIEW.md`).

## Verify

    sudo apt-get install -y g++ libboost-dev
    python -m pip install -r research/gen4-collective-families-283/requirements.txt    # sympy 1.14.0
    python3 -B research/gen4-collective-families-283/verify.py --output /tmp/gen4-collective-replay   # about 16 minutes; fresh directory outside the package

PR #283's verifier, unchanged (`--cxx`, `--boost-include` as there): package hashes against `MANIFEST.json`, PR #276's
immutable package replayed from `vendor/`, every stage compiled and run, every receipt compared with `expected/`,
then the certificate `PASS_SOURCE_REGENERATED_COMPOSITION` with κ. The workflow runs it on Ubuntu (Python 3.11, 3.13).

## Files

PR #283's package with: `inputs/kernel-original.json` (its 746 rows + 91 appended, kind
`GEN4COLL_COLLECTIVE_FAMILY_…`), `inputs/kernel-remapped.json`, `code/banks.cpp` (the filler block), `expected/`
(regenerated), `RESULT.json`, `MANIFEST.json`, `discovery/` (census, packing, F₂ replay, overlap and the pin-generating
driver; not run by the verifier), `README.md`, `PROOF.md`, `NOTICE.md`.
