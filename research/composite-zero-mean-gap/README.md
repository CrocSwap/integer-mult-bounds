# A smaller sufficient precision exponent for composite radices

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written analytic proof with exact finite corroboration.
No new kappa or selected-frontier change is claimed.

For every integer r >= 3, n = r-1, D = phi(r), ell = ceil(log2 r), the
cyclotomic coefficient heights of #1025/#1428 satisfy the new estimate

    sum_(k unit mod r) log H_k <= r log r (1+log r) + D log r.

Under the same nonzero-resultant hypothesis as #1428, this gives

    |P_k(z)| >= 2^(-d_new) for every primitive embedding k and |z|=1,
    d_new = 1+2ell+min(nDr, ceil(n[3r ell^2/4+(r+D)ell])).

It never increases #1428's sufficient exponent. At the certified mixed
radix 8978 = 2*67^2, the exponent is **13,531,624,611**, compared with
28,312,479,536 from that source's formula. These are sufficient analytic
exponents; no inverse at either precision was executed. The inherited
cyclic-operator implication gives the corresponding infinity-norm bound
`2^(2d_new+r+2)`.

The new step combines Hanson Sun / bbMisk's #1428 mixed-radix unit average
with Nick Petalas's older #5930 zero-mean logarithm, whose Fourier identity
already holds at every integer radix. The prime-power height application
in #5930 does not give this mixed-radix conclusion. The zero Fourier mean
removes an additive term, and its exact mass halves the leading old bound.
[PROOF.md](PROOF.md) states every hypothesis and the comparison argument.
The predecessor statements are cited premises, not audit deliverables.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/composite-zero-mean-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/composite-zero-mean-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/composite-zero-mean-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/composite-zero-mean-gap --check-source-history
```

Substitute another CPython 3.12 path elsewhere. Direct output is a generated
JSON receipt with `PASS_COMPOSITE_ZERO_MEAN_GAP` and SHA256 of all six files.
The checker writes nothing and needs no Git, network, external solver or
predecessor implementation. The metadata runner resolves provenance through
Git separately. Both registered commands execute the full verifier.

The new finite checks enclose actual height sums for all 100 primitive
embeddings at thirteen mixed radices from 6 through 30. Rational intervals
use Machin's identity, cosine Taylor remainders, integer square roots and
an atanh logarithm series, with outward rounding after arithmetic. They
also check 254 new natural-to-binary inequalities and 2,062 exponent cases,
including 1,964 strict improvements over the cited old formula. Cases are
counted executions and can repeat a radix. Eight invalid inputs reject;
one additional half-integer case checks the necessary ceiling. Normal and
optimized Python retain every explicit mathematical check.

## Scope, provenance and limits

Canonical base is e54523517d0f03e58352e647c403a5af3e525a57, priority revision 8,
selected #7000. The current selected-baseline orientation command passed for
source bindings only. The `uniform-transfer-audit` card changes scope to
this analytic precision-interface result; no selected assumption is discharged.
[TASK.json](TASK.json) records that change and [SOURCES.json](SOURCES.json)
pins the predecessor statements as historical provenance. There are no
external executable mathematical inputs.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19539388)
followed live open/account PR lists, recent handoffs, active Discussions,
local reservations, all-main README and merged searches. A dedicated #1428
source query found no account PR from the preceding seven days. Sparse
cached local notes and unpublished work limit overlap coverage; absence of
matches is not a novelty certificate.

A concurrent [prime-power harmonic claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19539414)
seeks a new unit-average envelope within prime powers. This result instead
uses the existing mixed-radix envelope and changes its logarithmic Fourier
input. No computations were added to check that separate proposed lemma.

The universal assertion is the written proof with cited premises, rather
than enumeration or proof-kernel acceptance. The height estimate is
unconditional; circle-gap and operator consequences retain the nonzero
resultant hypothesis. We cite #666/#1428's certified family `r=2p^a`,
prime p >= 5, without rechecking it. Other radices do not become certified
by exponent arithmetic. The coarse branch can prevent a strict improvement.

No paid solver, coefficient-preparation or rounding policy, restored dirty
workspace, physical word/caller, tape/stock cost, supplier admission or
complete multiplication theorem is supplied. All five framework assumptions
remain. Selected cold replay, native suites, Lean and Docker are unrun.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can one certified composite inverse execute at reduced precision with all
costs retained? Start with r=10 or r=134 and an explicit preparation and
inverse error recurrence. Paid coefficient work, rounding propagation,
scratch restoration and tape/caller costs remain blockers. The analytic
exponent alone establishes no executed or recursive saving.

## Credit and implementation constraints

Credit Chafik Boukhalfa / #1025 for averaged coefficient heights and precision;
Hanson Sun / bbMisk / #1428 for arbitrary-radix unit averaging and the conditional
gap/operator framework; Nick Petalas / #5930 for the all-radix zero-mean identity;
Ali Romman / #621 for the resultant/cofactor argument; and Jason Willems /
at1as / #666 for the certified composite nonvanishing family. Rohan Guliani /
#846, Charles Bethin / #764 and the retained exact-DFT/q-Pochhammer lineage
keep their context credit. Fourier inversion, geometric sums, Machin's
identity and interval Taylor/logarithm arithmetic are classical. The new
mixed-radix estimate, exponent substitution and checker were produced by
Nick Petalas. No predecessor files or credit lines are changed.

The checker includes actual coefficient-height enclosures as well as exponent
arithmetic. Functions stay below 60 lines and every loop has a finite domain.
Radices in the reference exponent function are at most 2^32,
factor trials at most 65,535, height instances at most 30, Taylor terms 24,
and logarithm terms 40. File inputs are trusted package sources, each checked
against a 256 KiB limit. Explicit exceptions remain enabled under optimization.
There is no recursion, subprocess, network, dynamic code generation or mutable
shared state. Python's bounded live Fraction/list/integer allocation is a rule-3
managed-runtime deviation; no fixed-allocation runtime is claimed. Warning-strict
normal/optimized execution and AST compilation provide local diagnostics.
No external static analyzer or formal kernel was run.
