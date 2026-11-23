# Retimed packet storage and stopping audit

This independent source-bound audit of PR #8042 at
`dfd25d553a843a946ca0b94130a5ff8943e98fdd` follows a nonidentity covered packet
through its odd number of same-rank exchanges, retaining high representatives,
pending/answer prefixes, both basis routes and full-cohort entry/return.

The scoped path passes. Named pages, banks, stage-root files and different-stage
ancestor spools remain live and charged. Newly opened **rank-local transient**
spools close before the next same-stage edge. The coupled packet invariant is

\[
(p-p_0)+(a-a_0)+\ell=V,
\]

and the real compiler caller gives `V=W/B`, then `ell=V/Q` in covered mode.
The proof binds these equalities to arbitrary-depth suffix return and historical
address reuse. A Gaussian child must start after the historical parent high,
not after the current count of live slots.

## Contents

- [PROOF.md](PROOF.md): dominant storage argument, source binding, limitations
  and the original local-owner census handoff, addressed by the supplement below.
- [STOPPING.md](STOPPING.md): supplemental source predicate/serial-bit audit,
  conditional on entry-header and physical-field contracts.
- `audit_packets.py`: physical packet execution, independent matrix action
  oracle, dirty ancestor guards, recorded lifetimes and five source mutations.
- `audit_owner_windows.py`: historical slot holes, zero owners, differing child
  widths and a minimal rejected live-count-base mutation.
- `verify_stopping.py`: exact capped comparator, bounded serial-bit lowering,
  child-premise checks and failure controls.
- [formal/SOURCE-CORRESPONDENCE.md](formal/SOURCE-CORRESPONDENCE.md): a Lean
  4.36 proof of the actual capped-power predicate and failed-caller relation,
  with exact source correspondence and separate author/root kernel receipts.
- `SOURCE-BINDINGS.json` and `sources/pr8042/`: exact pinned source bytes and
  the original hash-checking predecessor bootstrap. No network is needed.
- `evidence/`: executed receipts, which corroborate the written argument.
- [census/OWNER-CENSUS.md](census/OWNER-CENSUS.md): the source-bound bound of
  115,058 owned fields per calendar context, including zero inputs, output
  copies, half-column loans and suspended parents. Its production `<2B`
  consequence retains the universal mass enclosure explicitly.
- [census/review/CROSS-REVIEW.md](census/review/CROSS-REVIEW.md): the separate
  interval, custody, source-syntax and free-first review. A location-only
  [adapter](census/review/PORTABLE-REPLAY.md) preserves its exact checker bytes.
- [bytes/PROOF.md](bytes/PROOF.md): complete local historical byte bounds for
  the wide owner route (`<8V`), padded type route (`<9V`) and production repair
  (`<=8V`), with the production-header hypothesis and generic-API boundary.
- [bytes/review/REVIEW.md](bytes/review/REVIEW.md): independent source proof,
  stream/permutation checks and the corrected distinction between the
  17-bit tag comparison and a symbolic 33-bit total-volume counterexample.
- [repair-bounds/review/SHARP-REPAIR.md](repair-bounds/review/SHARP-REPAIR.md):
  the sharper six-volume production repair bound across differing calls,
  with explicit per-call versus role-wise historical controls.
- [direct-scale/PROOF.md](direct-scale/PROOF.md) and its separate
  [review](direct-scale/review/REVIEW.md): direct scalar, ordinary-root and
  serial public-rectangle historical byte envelopes.
- [mass-enclosure/PROOF.md](mass-enclosure/PROOF.md) and its separate
  [review](mass-enclosure/review/CROSS-REVIEW.md): universal directed-rounding
  error for the literal mass routine and authenticated production callers.
- [mass-enclosure/OWNER-COROLLARY.md](mass-enclosure/OWNER-COROLLARY.md):
  the production `<2B` owner consequence with its local mass premise derived.

## Reviewed follow-ups

The complete `census/` and `bytes/` subtrees landed at
`5b9a3d018f74c835ef87db86ce824d8026257b6b` are retained byte-for-byte.
The subsequent results live in separate folders. Their numerical and
historical refinements supplement the earlier statements without silently
rewriting their proofs or independent reviews.

Production repair has a uniform historical bound `<=6V*`, including input
and replacement, across arbitrary differing calls of volume at most `V*`.
The literal correction key is injective before final validation. Each
radix bucket holds at most half the complete group-label set, and the
production header gives tag width `t<=a/2` relative to grouped payload
width `a`. With merely `t<=a`, six volumes is only a per-call consequence:
an actual all-bad/all-good pair reaches seven after role-wise maxima.

The direct scalar's 22 fixed roles use at most `(27521/3420)V* <9V*`
across arbitrary finite differing admitted calls. The author uses exact
residue periods; a separate reviewer proves the same all-width table with
a complete finite prefix and an analytic tail. Five named ordinary-root
roles use `<7V*`, and the two serial public-rectangle roles use `<18V_slab`.
The complete ternary service and stage-root fence remain explicit premises.

For the actual installed mass calls, the universal error proof gives
`Delta<2^24 N^-57<=2^-33<1/4`. Exact grade and constructor binding covers
both Gaussian and binary installations. Combining its count-rounding
corollary with the existing census proves the production `Arena.high<2B`
without retaining that local numerical-enclosure assumption. Other valid-call,
custody, funding, physical-storage and analytic contracts remain explicit;
none of the five canonical foundational assumptions is removed in full.

## Reproduce

Requires Python 3.11 or newer and `git` for the original source patch installer.
No third-party Python package is required.

```sh
python3 -B scripts/research_package.py --package research/retimed-packet-storage-audit
# Standalone equivalent, from repository root:
python3 -B research/retimed-packet-storage-audit/verify.py --output /tmp/retimed-audit-results
```

The original driver checks all retained source hashes, restores a fresh temporary
runtime and executes all three packet fixtures, six storage/ownership source
mutations and the stopping supplement. Expected final marker:
`PASS_RETIMED_STORAGE_AND_STOPPING_AUDIT`.

The registered replay also executes the consolidated owner/byte supplements
with a separate fresh offline restoration:

```sh
python3 -B research/retimed-packet-storage-audit/verify_supplements.py \
  --output /tmp/retimed-owner-byte-results
```

Expected marker: `PASS_RETIMED_OWNER_AND_BYTE_SUPPLEMENTS`. This runs both
author checkers and both separate review methods. The byte author driver runs
in a temporary package copy, and every new receipt goes to the chosen output
directory, preserving committed evidence. The original two replay engines
are unchanged. The four registered budgets are 420, 300, 180 and 300 seconds,
totaling at most 1,200 seconds. The supplements need no Lean installation
and do not rerun the formal supplement.

Replay only the separately reviewed follow-ups in another fresh offline
restoration:

```sh
python3 -IB research/retimed-packet-storage-audit/verify_followups.py \
  --output /tmp/retimed-repair-direct-mass-followups
```

Expected marker: `PASS_RETIMED_REPAIR_DIRECT_AND_MASS_FOLLOWUPS`. It runs
the independent sharp-repair checker, direct scalar author and reviewer,
mass author, and a path-only adapter for both frozen mass reviewers. The
adapter compiles the reviewers with `optimize=0` and requires the generated
numerical and production-binding receipts to match the accepted receipts
exactly. The mathematical induction and all-width arguments are separate
from finite execution; no production-size calendar is run.

`--quick` omits only the 2,834,352-record full-high oracle and is not the complete
retained receipt. Detailed per-packet traces go to the selected result directory.

Each packet fixture has one weighted-child depth: at `N=2` the child receives
one atom and stops. The 1/3/5 calls are siblings. Arbitrary depth follows from
the actual caller volume equations and suffix-stack induction. Cover enumeration
is inherited from the source; the payload action oracle is separate. The
Gaussian fixture exercises the actual allocator, not the enormous positive word.

The stopping appendix credits #8042's existing `OuterStop.lean`. It supplies
caller binding and a serial lowering with operation counts, without treating
Python big integers or wall-clock measurements as a tape-machine implementation.

The consolidated formal supplement proves the universal Boolean predicate,
including its low-bit branch and omitted final square. It uses only `import Lean`;
no Mathlib is needed. With an installed Lean 4.36.0 binary, replay it
independently of the Python-only registered packet runner:

```sh
python3 -B research/retimed-packet-storage-audit/formal/replay.py \
  --lean /absolute/path/to/lean --output /tmp/retimed-capped-power-review
```

This wrapper restores the same pinned runtime offline, checks the reviewed
proof hash, source AST and caller, and audits all fifteen kernel axiom reports.
The only dependencies reported are standard `propext`, `Quot.sound` and
`Classical.choice`. Python operational semantics and machine costs are not
formalized. The source inventory now also retains the unchanged predecessor
`OuterStop.lean`, for 26 original source files; earlier 25-file receipts describe
the original packet package before this addition.

No new kappa, activation threshold, global multiplier storage constant or
removal of a foundational physical premise is claimed. The package performs no remote
publication. Prepared for @CubeJerry with OpenAI assistance. Model cross-review
is not independent human review; kernel acceptance is limited to the stated
formal propositions.

## Open next questions

The Gaussian and binary owner censuses and their local production capacity
premises are now proved for the exact source under the stated successful-call
and custody contracts. The binary capacity bound supplies the former local
antecedent of the complete ordinary local/ancestor composition below. The
direct scalar/root/rectangle envelopes supplement the earlier local byte routes.
Header and private-control encoding, outer CRT/control allocations, the full
fixed-tape tariff and application of the retained outer recovery framework
remain open. Their concrete first steps are recorded in TASK.json. The original
proofs and reviews remain as historical checkpoints; in particular, the frozen
binary-census README's handoff predates the completed storage application and
independent application review linked below.

The standalone source export is self-contained and hash authenticated.
SOURCES.json pins catalogue/selected-record provenance; SOURCE-BINDINGS.json
binds the retained unmerged source bytes without relying on that foreign
commit being available in a clean checkout.

## Complete ordinary data-file coefficient

[JOINED-STORAGE.md](JOINED-STORAGE.md) combines the separately reviewed
[ancestor composition](composition/PROOF.md),
[complete 67-position local table](ordinary-local/PROOF.md), and
[warm-entry boundary](composition/ENTRY-HISTORY.md) at the same frozen #8042 source.
The local coefficient is `A(B)<=17+54/B`; the named-head coefficient is
`G(B,2)=6+123/(8(B-1))`. Exact substitution at the installed at-most-seven
stages gives `H_native<8261T<74349X`. Across a fixed installation's full
mixed native/cold history, the six separate public binary roles add at most
`3X_max`, giving `H_history<74352X_max` from an empty reservation. Initial
historical capacities receive their per-role maximum grant.

The frozen joined theorem records binary capacity `capacity<=2B` separately.
The binary census and production corollary below now derive that antecedent;
the Gaussian census remains a distinct result. These are ordinary data-file coefficients,
excluding borrowed caller backing, headers, private control, delimiters,
movement, outer Gaussian/CRT allocation and analytic recovery. The old
composition/local READMEs preserve their pre-join handoffs; this section and
the joined note record the completed substitution without changing frozen proofs.

The [independent joined review](ordinary-local/review/JOINED-REVIEW.md) checks
the exact substitution and history domain. The
[independent local review](ordinary-local/review/REVIEW.md) uses its own
interval interpreter and actual caller descriptors. The
[composition root review](composition/ROOT-REVIEW.md) checks the actual
named heads and same-stage/earlier-stage source boundaries. Model-assisted
review does not imply human or kernel acceptance.

```sh
python3 -B research/retimed-packet-storage-audit/verify_ordinary.py \
  --output /tmp/retimed-ordinary-data-byte-join
```

The standalone ordinary replay executes both author and independent methods
with normal/optimized parity, preserving all frozen receipts in place.
`check_joined.py` separately binds both component proofs, authenticates
all 23 retained source files and checks the exact rational coefficient.
Its final marker is `PASS_COMPLETE_ORDINARY_DATA_BYTE_JOIN`.

## Binary capacity closes the ordinary numerical antecedent

The [binary census](binary-census/PROOF.md) proves capacity <= B + 22339*sum_e count[e]*(104904*delay[e]+1), including opening and closing lifetimes. The [production corollary](binary-census/COROLLARY.md) combines that census with the accepted mass enclosure and literal delay loop to derive capacity<2B. Separate reviewers accepted both components.

The fixed source has 18,906 targets and 104,904 paid labels. Paid-cut-only accounting sees 2,803 private owners and misses the actual 3,433 peak during closing cleanup. The inclusive count charges the larger peak. Logical bank capacity is distinct from warm physical backing.

[STORAGE-APPLICATION.md](binary-census/STORAGE-APPLICATION.md) and its [separate application review](binary-application-review/APPLICATION-REVIEW.md) instantiate the unchanged ordinary data-file theorem: H_native<74349X and H_history<74352X_max, retaining initial per-role capacity. The numerical beta=2 antecedent is now derived. Legal caller, custody, erasure/return, fixed-role, header/control, fixed-tape and outer obligations remain explicit; no complete canonical assumption or selected kappa changes.

The fourth registered command now runs verify_storage_completion.py, combining ordinary and binary author/reviewer checks within the existing 300-second allowance. All receipts go outside the package and every package file must remain unchanged. Its final marker is `PASS_RETIMED_COMPLETE_ORDINARY_AND_BINARY_STORAGE`. Earlier frozen conditional proofs and receipts are historical; the application and later root receipt record the derived antecedent.
