# Sharp growth inside a restoring unit-shear word

This contribution was produced by Nick Petalas. Claim type: scoped written
proof with exact finite corroboration. Apache-2.0. No new kappa is claimed.

For any finite number n>=2 of arbitrary dirty rows, take a word of at most
L gates `x_i += epsilon*x_j`, with i!=j and epsilon in {-1,1}, whose complete
endpoint is the identity. The exact largest possible intermediate values are

```
largest absolute matrix coefficient = F_(floor(L/2)+1)
largest absolute row sum            = F_(floor(L/2)+2)
```

Here F_0=0 and F_1=1. Two rows attain both bounds: alternate positive ADDs
for floor(L/2) steps, then execute the literal inverse. Extra dirty rows
cannot improve the maxima. At cut k of a length-ell loop, replace floor(L/2)
by min(k,ell-k) in the upper bounds.

For initial magnitudes at most H, the sharp universal intermediate cap is
`H*F_(floor(L/2)+2)`. The [proof](PROOF.md) also gives its exact signed-width
guard. The new step uses the restoring suffix to bound the same prefix from
the opposite end. Standard top-two Fibonacci majorization supplies the
one-way estimate. No global literature-priority claim is made.

The changed card scope is explicit in [TASK.json](TASK.json). This is a
scalar precision side result, without selected-caller binding. It does not
audit a predecessor, admit a supplier or change the selected frontier.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/restored-unit-shear-growth
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/restored-unit-shear-growth/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/restored-unit-shear-growth/oracle.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/restored-unit-shear-growth --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path. The
registered normal and optimized runs print PASS_RESTORED_UNIT_SHEAR_GROWTH.
Direct oracle replay prints PASS_RESTORED_SHEAR_LITERAL_CUBE.

The matrix census enumerates all 87,381 two-row words through length eight
and all 271,453 three-row words through length five. It finds 2,689 and 577
identity words, respectively, and checks each cut. The independent oracle
uses literal integer cube corners, with no matrix-model import. It enumerates
5,461 two-row words through length six and 22,621 three-row words through
length four; every common identity count and maximum row norm agrees.
Empty exact-length classes have null maxima in the generated receipt.

The replay checks 387 attaining loops at even budgets through 256, 128 odd
budget attainers, 231 literal magnitude/width guards and 12 controls. The
controls include invalid coefficients and indices, self-addition, inadequate
gate budgets, incomplete restoration and an undersized Fibonacci bound.
Explicit exceptions keep every check active under optimization. The receipt
binds every package file by SHA256 and is printed without writing files.

## Limits

The theorem uses an at-most gate budget and exact full identity restoration.
It excludes scales, coefficients beyond signed units, source insertions,
native operators and rounding. In particular, this is not an error bound
for rounded identity cycles or a bound on every arithmetic temporary. Real
selected callers contain excluded operations. Their source/frame/ownership,
physical tape, precision, compiler and analytic obligations remain separate.
No predecessor suite, selected cold replay, Lean or Docker build ran.
Independent human and formal proof-kernel review are unclaimed.

The reference model accepts at most eight rows and 256 gates. The proof has
no such dimension or length restriction. Every loop has a finite bound from
these limits or the fixed census domains. No recursion, network, subprocess
or dynamic evaluation is used. Functions stay below 60 physical lines.
Python allocation during integer arithmetic is a Power-of-Ten rule 3
deviation, bounded by the fixed domains and word lengths. The census streams
words and retains only one trace and per-length summaries. Warning-strict
normal and optimized replay supplies the available interpreted diagnostics;
no installed static type checker or linter was available. Explicit sibling
imports identify the two scientific modules; no predecessor is imported.

## Open next questions

1. Determine a sharp bound for one specified nonidentity endpoint. Begin
   with forward growth and inverse-suffix multiplication by the endpoint.
   This could cover useful scalar intervals, but no sharp classification
   or selected interval is bound here.
2. Derive an error bound for a stated rounded implementation using the
   exact inverse-prefix envelope. Specify every rounding point and increment
   model first. Exact restoration alone does not prove rounded restoration
   or dirt-independent increments.

## Sources and credit

Base: canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority
revision 8, selected PR6030. The selected record and catalogue are historical
provenance in [SOURCES.json](SOURCES.json), with no external scientific input.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361711)
records the original question. Live handoffs and reservations, open/account
PRs, main README and formula searches, merged PR searches and cached card
coverage were checked. Arbitrary historical diffs and unpublished work remain
outside that coverage.

Elementary row operations, induced matrix norms and Fibonacci majorization
are classical. The new scoped contribution is the sharp restoration-aware
application and its rerunnable verification, produced by Nick Petalas.
