# Joint helper-end and gate-frame ceiling for the selected k8 word

**Scoped negative result, no new kappa.** Simultaneously shrinking any of
the 78 restricted helper ends to nested subspaces, while changing every
A/B/early-cleanup gate frame, still gives

    a < 0.001690198050303,
    kappa < 1690198050303/1001690198050303 ≈ 0.001687346101213.

The favorable ceiling can rise by less than **0.00852%**, far below the
5% target. Scalar operations/order, entrances, centre cut, target levels,
early/full cleanup membership and the coverage/guard contract are fixed.

This changes both the fixed-gate-frame premise of Arham Tahir's
[PR1583](https://github.com/CrocSwap/integer-mult-bounds/pull/1583) and the
fixed-endpoint premise of [PR1671](https://github.com/CrocSwap/integer-mult-bounds/pull/1671).
Alexander Schwartzman's PR1030 and Cinna Davis's retained PR1090 already
construct particular smaller ends. The new contribution is the complete
joint optimization bound, with variable local mass fully recharged as idle.

## Evidence

The [proof](PROOF.md) gives the precise quantified domain and cost argument.
The selected R480 word is bound by SLOT-PINS-k8 and decompressed SHA256
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
The stale R492 predecessor is excluded using the retained lineage analysis.

- All 5,413 gate frames are covered; 1,741 have more than one choice.
- Of 78 restricted ends, 32 are forced and 46 have two complete subspace
  choices. The other 402 helpers retain full ends because of full cleanup.
- All 106 low-end cone relations are represented explicitly as zero-charge
  containment edges. The full model has 135 components, 18,033 LP rows and
  23,456 columns, each checked with exact rational dual coefficients.
- An integral assignment matches every dual objective at the ceiling
  endpoint and the 5% target. It contracts ends 574,575,580,581 and gives
  `{1:2400,2:446,3:416,4:142,5:82,8:8}`, local mass 5,582 and idle mass 1,650.
- A separate bitset/covector implementation reconstructs every domain,
  edge and cone, then checks the dual signs and ceiling with integer-root
  arithmetic, importing no primary frame/LP/moment code.
- The unchanged native auditor accepts the baseline, retained PR1090
  two-end witness and four-end attaining word on **704 columns in both
  orientations**, including dirty state and restoration.

The receipt brackets the best favorable primitive ceiling between
0.001690198050302 and 0.001690198050303. This does not assert frame/end
optimality at every exponent or a realizable fractional idle packing.
Different legal choices in different invocations are covered by summing
the per-call lower bound.

Shrinking the ends releases four rank units into idle work. Keeping the
old idle mass 1,646 would incorrectly pass the 5% target; the exact control
exposes this false positive. Using rank-excess prices relative to rank-51
idle packing makes the coupled objective correct for varying local mass.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py \
  --package research/selected-k8-endpoint-contractions
```

This runs the primary, separate implementation and control suite. Both
checkers preserve all guards under `-O`; unchanged legacy code is compiled
with its assertions enabled. Normal replay is read-only. The explicit
`verify.py --write-expected` option regenerates the deterministic receipt.
DUALS and PRIMAL identities use canonical parsed payloads, not gzip bytes.

The registered replay passed on CPython 3.12.3 (`/usr/bin/python3.12`),
including all 18 control groups. Both checkers also passed on CPython
3.14.4 with `-I -O -B` from a relocated, read-only package; all files
remained unchanged. The canonical receipt SHA256 is
`4b9847122d6cd93b61eaa391fa1a67191824e287fe2d828cb0f38ff6b5f1658f`.

`nominate.py` is optional discovery code adapted from navinor's credited
HiGHS generator. It used highspy 1.15.1, NumPy 2.5.4 and SciPy 1.18.1 in an
isolated environment. DISCOVERY.json contains noncertifying numerical
diagnostics. Acceptance requires no solver dependency.

## Scope and coordination

Single random nonce `27a9e1612f686c5cfc60b3fb45d023cb`, revision-3
`complex-mechanisms / complex-new-helper-inventory`, no reroll. Base main
`15d2aca0385b61596155e8421140d08d27e543af`. The prescribed baseline-source,
ceiling and lever controls passed. An initial optimistic budget waived
all climbs of the 78 affected helpers, retained other local work and
recharged idle mass; its a ceiling below 0.001826483000117 left headroom
for the complete constraint screen. It was not a realizable assignment.
[Discussion1674](https://github.com/CrocSwap/integer-mult-bounds/discussions/1674)
records the scoped claim and outcome; TASK.json retains the card and pins.

The publication refresh covered 433 open PRs at 16:32:27 UTC and 622
Discussions at 16:33:41 UTC on 2026-10-14, with complete pagination.
PR1583, PR1090 and PR1671 retained their exact heads and are now merged.
Search covers metadata, not arbitrary code, and is not a novelty certificate.
Main at `01a65937ece11b56d515c81f039464ae3043c1c1` preserved all 12
mathematical inputs and the selected record, with no package collision.
Its changed package runner passed a fresh full CPython 3.12 registered replay.
The other changed guidance adds an E8 scope map and CI invalidation details.

Ross Richardson's intervening `selected-k8-uniform-frame-audit` extends
PR1671 uniformly over a power-price interval with fixed ends. It is
complementary to this variable-end result and is not a certificate input.
The helper-450 emitted audits and the source-independent full-cleanup
obstruction also have distinct scopes; TASK.json records that review.

Published as [PR1995](https://github.com/CrocSwap/integer-mult-bounds/pull/1995).
Mathematical commit: `73e323159d65c974debb180189694fd59144da5f`.

This is the card's bounded endpoint-contract obstruction. It does not
supply a construction passing its acceptance gate. No whole hosted
supplier, selected cold replay, global invoice, all-size compiler,
precision/tape or analytic-transfer theorem is claimed. Remaining packing
headroom below this ceiling is not claimed eliminated. Nonnested end
changes, entrances, scalar chronology, cleanup membership, new helpers,
shared centre work and changed coverage laws remain outside scope.
The 704-column checks are exact local scalar/frame audits. Emitted native
programs and phase/wrapper admission were not replayed.

## Open next questions

1. **Nonnested ends or changed entrances.** Pin one actual endpoint pair,
   derive complete frame and cone constraints, and price its whole profile.
   These changes can escape the interval domains above; dirty-state
   correctness and the complete hosting invoice remain obligations.
2. **Change a scalar dependency or early-cleanup cut.** Recompute the
   complete frame intervals and full ceiling for one declared rewrite.
   It needs enough charged headroom to meet the target, plus a valid
   changed-word contract.
3. **Host the attaining four-end word.** First compare its exact annotations
   against existing rank-seven-end constructions, then test one whole-helper
   owner placement. Local optimality supplies no global improvement by
   itself; the available ceiling gain is tiny and the full native/global,
   precision and outer obligations have not been replayed.

## Credit

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Retains navinor's frame method; chafreaky/PR557, ntedvs/PR776 and Rohan
Guliani/PR815; Alexander Schwartzman/PR1030 and Cinna Davis/PR1090;
Arham Tahir/PR1583; Douglas Colkitt/PR1240 and Sagar Thakrar/PR1012;
the Jeremy Kothe/Rohan Arun/Hao Yan/icekylinx construction lineage and
woklerx word reconciliation. See NOTICE.md and exact SOURCES.json pins.
Apache-2.0; no independent human or full formal verification is asserted.
