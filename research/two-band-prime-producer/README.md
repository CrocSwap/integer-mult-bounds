# A smaller setup bound for the many-axis prime producer

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped constructive complexity proof with exact finite
corroboration. A two-scale producer retains ToikY's
[PR4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029) prime
bands, ordered source output, scratch erasure and O(D ell+ell) backing,
while reducing its written setup bound from O(r^2 ell^2+D ell) to

    O((r/d+1) sqrt(r) ell^2+D ell),  r=2^ell, D=d-1.

On the predecessor's abundance domain, ell>=2^32 and 2<=d<=ell^334,
this is O(r^(3/2) ell^2/d+D ell). The new producer scans each target
scale once, stops at its quota and tests divisors only through the square
boundary. The complete two-band candidate count is at most r/(8d)+2.
Two sequential prime tables preserve arbitrary flag order with no repeated
search for each axis. [PROOF.md](PROOF.md) includes endpoint arithmetic,
all loop bounds, fixed-tape implementation costs, output and head returns.

This is a partial algorithmic step toward PR4029 Open next question 1.
Its prime-abundance theorem and band-to-guard implications are cited
premises, not replayed or audited. Square-root primality testing is classical;
the contribution is the explicit space-preserving producer and complete
bound at this source contract. The inherited setup was already subleading,
so no new kappa or selected-frontier change follows.

## New evidence

The bounded reference in [verify.py](verify.py) accepts ell<=16 and D<=32.
Its verifier checks its own construction against a new Eratosthenes oracle,
independent integer band predicates and literal output-word decoding.

- All 65,535 integers from 2 through 65,536 agree with the sieve. The
  divisor loops execute 1,531,519 remainders and 1,538,061 square comparisons.
- All 8,192 endpoint fixtures use target=2..257 and d=2..33, including
  integral and nonintegral band endpoints.
- All 1,270 requests at ell=3..12 and D=1..7 include every supplied binary
  flag stream and the implicit last full-scale flag. There are 83 successes
  with 370 emitted source words and 1,187 explicitly checked insufficient
  supply failures. Successful requests execute 2,671 candidate tests,
  30,011 remainders, 30,381 square comparisons and 17,894 stream head moves.
- Thirteen malformed/semantic controls reject. Three prime/square capacity
  controls pass, and one extra exhausted request signals insufficient supply.

For ell=12 with supplied flags (0,1,0), output is
(1913,3823,1931,3833). It uses 31 candidate tests, 359 remainders,
363 square comparisons and 198 stream head moves. The reference explicitly
copies and blanks bit-cell table pages. Its stream-copy move count is
4D ell+2(D-1), excluding separately paid arithmetic and table preparation.

Counts are enumerated operation counts, not measured runtime improvements.
The universal theorem rests on the written proof. The finite interpreter
uses host integers and does not execute the predecessor's encoded arithmetic,
production_axis, scientific verifier or an astronomical prime search.

## Reproduce

From the worktree root with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-band-prime-producer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-band-prime-producer/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-band-prime-producer
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-band-prime-producer --check-source-history
```

Other machines may substitute their CPython 3.12 executable. The two direct
commands also work in a Git-free copy of these six files and write no files.
They print PASS_TWO_BAND_PRIME_PRODUCER in a generated JSON receipt bound
to SHA256 hashes of every package file. Registered replay runs both commands;
metadata and exact-history checks authenticate the provenance pins separately.
No handwritten result receipt is committed.

## Scope, credit and overlap

Scientific base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority revision 8, selected PR6030. [TASK.json](TASK.json) records the
change from uniform-transfer-audit to this setup side result and structured
next questions. [SOURCES.json](SOURCES.json) binds historical provenance,
with no runtime scientific input or predecessor import.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362373).

Credit ToikY for PR4029's source domain, bands, abundance, ordered source
contract and original construction; Cinna Davis / PR3319 and the
source08/Harvey--van der Hoeven lineage for trial division and source
selection; Jose Manuel / jmbarrancoml / PR3935 for TensorPlan's source-word
layout and implicit last flag; Tekalign / tekuuu / PR4024 for the encoded
CRT premise; Chafik Boukhalfa and JosieElliston for fine-prime context;
Fiori, Kadiri and Swidinsky for the imported analytic theorem. These sources'
files and deeper credits are unchanged. No literature priority is claimed
for trial division, interval floors or sequential table consumption.

Nick Petalas / PR5149 and PR5152 supply earlier cutoff and product-loss
improvements, which this package does not extend. Matarener's fine-prime
audit uses square-root testing in a different prime band. Dugongue's
prime-free native grid uses a different Word RAM/composite-axis contract.
Neither is a deliverable or dependency of this construction. Live claims,
local reservations, recent account work, main README terms, open/merged PR
bodies and the cached card search were inspected. Sparse local notes,
arbitrary historical diffs and unpublished work remain coverage limits.

This result supplies no literal encoded instruction trace, complete
TensorPlan consumer, production_common proof, Gaussian error bound, native
operator, physical reserve, compiler admission, rounded multiplier or new
kappa. Erasure is ordinary erasure of owned scratch. All five selected
framework assumptions retain their status. No selected cold replay, native
suite, Lean or Docker run is claimed. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

1. Can this algorithm be emitted and admitted at the actual encoded
   TensorPlan/CRT interface? Start by lowering square comparison and binary
   long division to one named tape backend, including all scratch and head
   returns. A literal arithmetic trace and full consumer are still missing.
2. Can a complete changed transform reduce the dominant work? Start with
   its full native, precision, routing and recovery bill. Prime setup alone
   cannot improve kappa because it was already subleading.

## Verifier constraints

There is no recursion, network, subprocess, dynamic source loading or input
file beyond the six fixed package files. The largest function has 30 lines.
Every domain and loop has an explicit finite bound. Rejection controls call
only the fixed local functions listed in check_controls; this bounded
dispatch is a Power of Ten rule 9 deviation. Explicit requirements stay
enabled under optimization. Warning-strict normal/optimized replay and AST
inspection supply the available diagnostics; no separate type checker is
claimed.

Power of Ten rule 3 deviation: Python allocates integers and containers during
checking. The sieve has 65,537 cells, production dimensions are at most 32,
each reference tape/output has at most 512 bit cells, and the file reader
reads at most 1,048,577 bytes per fixed file before rejecting excess size.
One request is live at a time. These capacities bound the reference; they do
not make its Python allocations a fixed-storage implementation.
