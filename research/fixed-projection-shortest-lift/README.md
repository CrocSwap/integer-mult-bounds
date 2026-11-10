# The fixed PR5430 projection has exact lift length 36

The word

    374717236747275473071030571727164702

is a universal restored eight-source singleton path of length 36. Deleting its
twelve coordinate-7 calls gives exactly Nicholas Stone's PR5430 parent
`341236425430103051216402`. Together with that predecessor's cited lower bound,
this settles the exact minimum **36** for closed paths with this fixed
projected state set. Attainment was previously unclaimed. The construction
search stopped at this first verified word.

Claim type: finite construction certificate and scoped optimality corollary
using a cited theorem. This contribution was produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed. No new kappa
or selected-frontier change is claimed.

## Evidence

[PROOF.md](PROOF.md) states the contract, derives arbitrary-dirty XOR semantics
and explains the dependence of optimality on PR5430. The new verifier directly
checks the construction, without importing or replaying a predecessor verifier.

- All 36 prefix states are distinct, and their pair differences cover all
  256 masks. A separate direct interval algorithm covers the same 256 masks.
- The coordinate counts are `(4,4,4,4,4,2,2,12)`, so the path closes.
  Exactly twelve projected states have both layers and twelve have one.
- Literal execution checks all 512 assignments to eight scalar sources and
  the dirty accumulator, with all 256 interval recoveries per assignment:
  131,072 checked recoveries. Every source is preserved and the accumulator
  returns to its initial value.
- Eleven rejection controls cover malformed domains, a missing switch,
  restoration without universality, projection without lift universality and
  a corrupted recovery interval. Checks remain enabled under optimized Python.

The lower bound is credited to [Nicholas Stone / PR5430](https://github.com/CrocSwap/integer-mult-bounds/pull/5430),
not independently audited here. The new evidence is the attaining word and
its complete direct certificate. No earlier universal-word exclusion or
65,805-set predecessor census was replayed.

## Reproduce

From the repository root, with CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/fixed-projection-shortest-lift
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/fixed-projection-shortest-lift/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/fixed-projection-shortest-lift/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/fixed-projection-shortest-lift --check-source-history
```

Other machines may substitute their CPython 3.12 path. Expected direct marker:

    PASS_FIXED_PROJECTION_SHORTEST_LIFT length=36 differences=256 dirty_recoveries=131072 controls=11

The verifier emits a generated receipt binding its recomputed results and
interval-table digest to SHA256 hashes of all six package files. It writes no
files and needs neither Git nor network. Provenance checking separately needs
Git history. No receipt is handwritten or committed.

## Limits and expansion decision

This is a local connector result. It does not improve the global eight-source
bound, classify seven-source parents or claim that the fixed projection is a
competitive global construction. The exact minimum follows using the cited
predecessor theorem; finite construction checks alone establish the upper bound.
The selected record and all five framework assumptions are unchanged.

The arbitrary-width payload statement is algebraic. Actual observation storage,
COPY/ERASE, native maps, source access, independent target delivery, restoration
wrappers, physical owners, full recursive prices, precision/tapes, compiler
admission and analytic transfer remain outside scope. No complete supplier,
selected cold replay, proof-kernel build or physical caller is supplied.

The family decision is **stop this fixed-projection length question**. The
complete construction bill beyond the abstract 36 singleton calls is unknown,
not zero. A further family expansion requires a different parent or a physical
consumer and its full budget, rather than more insertion searches on this word.

## Open next questions

- Can a different seven-source optimal parent admit a lift shorter than 32
  calls? First publish its complete projected state set and an insertion word,
  then check all 256 differences. The missing object is such a new construction;
  this fixed parent cannot supply it.
- Can an actual consumer use the interval table with a favorable complete
  observation and restoration bill? First specify which accumulator values
  it retains and when. No physical consumer or storage tariff is supplied.

## Credit and provenance

Nicholas Stone / PR5430 supplies the fixed parent, unique-difference matching
obstruction and static lifting context. conorholds / PR3058 supplies the
seven-source optimum cited in that package; Ross Richardson / PR943 supplies
the singleton prefix-walk model; Douglas Colkitt / PR1185 supplies the Gray
construction context. Nick Petalas / PR5234 supplies the retained eight-source
lower-bound context. All predecessor attribution remains unchanged. The new
contribution is this attaining word, its certificate and the resulting local
optimality corollary. New material is Apache-2.0.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The bit-new-register-model card is explicitly changed to this
fixed-projection connector construction; it meets no complete native-supplier
acceptance gate. [Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363537).
SOURCES.json pins the source README as historical provenance, with no runtime
input dependency. Live claims, reservations, open/account PRs, exact-word and
general-object searches of merged PRs and committed READMEs were checked.
Sparse cached notes, arbitrary historical diffs and unpublished work limit
coverage. No exhaustive novelty claim is made.

## Verifier constraints

Functions stay below 60 physical lines. There is no recursion, dynamic source
import, subprocess, network operation or output-file creation. Word length is
bounded by 64 and dimension by eight. The main construction has 36 states,
256 table entries and 512 scalar assignments. Every loop has a fixed finite
bound derived from these limits. Input contracts use explicit exceptions and
all checks survive -O. Normal and optimized commands use warning-as-error mode.

Power-of-ten rule 3 deviation: CPython allocates managed integers and containers
while checking. The bounds above limit live data; each of six file reads is
capped at one MiB. This is a bounded research verifier, not a fixed-allocation
runtime. Syntax and function-size inspection supplement warning-strict execution.
Physical allocation and cancellation contracts would require an actual runtime
implementation.
