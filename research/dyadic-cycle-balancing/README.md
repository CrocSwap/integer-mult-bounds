# Exact binary scale range for cyclic balancing

This contribution was produced by Nick Petalas. Claim type: scoped all-length
proof with exact finite corroboration. No new kappa or supplier is claimed.

For a weighted cyclic recurrence y_i-a_i y_(i-1)=x_i and a prescribed cap
beta>0, define

```text
d_i = ceil(log_2(|a_i|/beta)).
```

Dyadic diagonal balancing is possible exactly when sum_i d_i<=0. Its exact
minimum binary scale span is

```text
H = max(0, largest sum of d_i on a proper cyclic interval).
```

The maximum uses intervals of lengths 1 through L-1, including intervals
crossing the chosen origin. For L=1, H=0. A maximum-suffix-sum constructor
attains H. [PROOF.md](PROOF.md) proves the criterion, minimum and constructor
for every cycle length, and gives the exact change of variables.

The least diagonal condition number is therefore 2^H. After normalizing the
smallest scale exponent to zero, direct exact rescaling of arbitrary inputs
on a binary grid needs H additional fractional bits on a common grid.
Reverse scaling amplifies a uniform error by at most 2^H, sharply.

This answers the scale-range part of the balancing question in Sricharan
Vagvala / theon199's [PR1481](https://github.com/CrocSwap/integer-mult-bounds/pull/1481),
Open next question 2. For its two-coordinate coefficient family
`a=(2^k,2^(-k-2))` at cap `1/2`, the exact span is k+1. The attaining
coefficients are both 1/2, but their binary scaling condition number is
2^(k+1). Balancing alone cannot supply a uniform grid or conditioning
guarantee independent of k.

There is a separate quantization obstruction within the same theorem.
`a=(3/5,2/5)` has product 6/25<1/4 and admits real diagonal balancing to
cap 1/2, but its integer demands are (1,0). No dyadic balancing attains
that cap. This is an exact infeasibility proof, not a search failure.

## Evidence and reproduction

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dyadic-cycle-balancing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dyadic-cycle-balancing/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-cycle-balancing
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-cycle-balancing --check-source-history
```

Another installed CPython 3.12 path may replace the local path. Run the last
command after committing. Expected markers are `PASS_DYADIC_CYCLE_BALANCING`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.

The fixed standalone verifier checks:

- Every 19,530 demand vector in {-2,-1,0,1,2}^L for L=1,...,6,
  including 10,886 feasible constructors. For all 445 feasible cases through
  length four, a separate literal box enumeration rejects every one of the
  5,428 vectors with strictly smaller candidate span. Translation makes
  this box exhaustive for smaller spans. Infeasible positive-total cases
  use the theorem's summation obstruction, not an unbounded search.
- All 5,600 rational coefficient/cap cases at lengths one through four,
  using seven magnitudes and two caps. The 2,159 feasible cases check every
  basis column of the literal conjugacy, 8,255 columns and 32,005 entries.
  Alternating coefficient signs are retained. Singular cyclic systems are
  permitted because the balancing/conjugacy claim does not require inversion.
- 1,110 binary-grid contexts, 25,000 literal coordinate rescalings, and
  1,110 sharp denominator and reverse-error witnesses.
- 402 exact logarithmic ceiling boundary checks, 64 members of the
  expansive family, one maximum-capacity constructor and 17 invalid-input
  or semantic controls. These include zero-total cycles, wraparound
  intervals, a false smaller span and the real-versus-dyadic obstruction.

Counts are enumerated by the verifier. Each execution emits a generated
stdout receipt binding all six package files by SHA256. It writes no files;
there is no handwritten or frozen receipt. Explicit exception checks remain
enabled under optimized Python. The universal claim rests on the written
proof, with these finite checks as corroboration.

## Scope, provenance and credit

The `uniform-transfer-audit` card changes to a self-contained algebraic
precision side result. No selected caller or framework assumption is
discharged. PR1481's complete physical balancing invoice remains open.
Relative grid span and norm transfer do not prove an arbitrary rounded
algorithm needs H additional bits. Nonuniform grids, different solvers,
non-dyadic scales and separately priced representations can change that
question. The proof permits complex phases; finite conjugacy fixtures use
real rational coefficients and signs.

Physical scale instructions, reversible source acquisition, arbitrary dirty
restoration, temporary arithmetic, numerical heights of a complete solver,
fixed-tape movement, storage, coefficient access and the complete recursive
invoice remain unproved. No predecessor verifier, selected scientific cold
replay, Lean or Docker check is run. Independent human and formal proof-kernel
review are unclaimed. The selected frontier remains unchanged.

Credit Sricharan Vagvala / theon199, PR1481, for the explicit balancing
question and weighted expansive-cycle setting; Chafik Boukhalfa, PR628 and
PR905, for the retained weighted scan; Charles Bethin, PR764, for the
contraction-based precision context; and the predecessor's retained kernel
and precision lineage. Difference constraints, longest-path potentials,
diagonal similarity and binary grid arithmetic are classical. No general
optimization or literature priority is claimed. New material is Apache-2.0.

[SOURCES.json](SOURCES.json) pins the source question, originating catalogue
and selected record as historical provenance at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. There are no scientific runtime
inputs outside this package. [TASK.json](TASK.json) records the scope change,
overlap limitations and [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362963).
Live open/account PRs, handoff claims, local reservations, distinctive main
README searches and merged-PR searches were checked. Sparse local notes,
arbitrary historical diffs and unpublished work remain coverage limits.
No absence of matches establishes novelty.

## Verifier constraints

The constructor accepts 1 through 64 edges with integer demands of absolute
value at most 4,096. Rational ceiling arguments have at most 1,024 bits in
each numerator/denominator. The theorem has no such bounds. Constructor
loops use at most 64*63 edge additions; the largest integer span checked
is 131,072, without constructing a number with that many exponent bits.
The exact finite optimization, coefficient and grid domains above bound
the scientific driver. Functions stay below 60 physical lines. There is
no recursion, subprocess, network, dynamic code, external import or write.
Only the six local package files are read for the receipt.

Python's managed allocation and runtime dispatch require bounded deviations
from fixed-allocation and direct-call constraints. Integers, Fractions,
tuples and JSON containers allocate during this one-shot check. Fixed domains
and the constructor caps bound live data; no service or unbounded search is
provided. The rejection helper has only the three named local function
targets. Normal and optimized warning-strict runs exercise the complete
fixed domains and capacity controls. A native fixed-allocation port or an
external-input frontend would need a separate capacity and parsing review.

## Open next questions

1. Can nonuniform coordinate grids turn this minimum-span balancing into a
   fully paid reversible cyclic inverse? First specify exact scale/read/
   return instructions, per-coordinate grids and the rounded error recurrence.
   Physical restoration, movement and the complete cost remain blockers.
2. For a named source coefficient table, does the optimum H fit its actual
   precision and storage allowance? First pin that table, cap and caller,
   compute the exact demands, and price all conversions. This abstract theorem
   supplies no selected-supplier instance or free scaling operation.
