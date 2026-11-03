# Subexponentially many axes in the fine prime band

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact endpoint certificates.
The many-axis prime band from [ToikY's PR4029](https://github.com/CrocSwap/integer-mult-bounds/pull/4029)
contains at least D=d-1 primes at either retained target scale whenever

```text
ell >= 2^18,       2 <= d <= 2^floor(sqrt(ell)/4).
```

This removes the polynomial dimension restriction in that analytic supply
argument. For every ell>=2^32 the new cap contains its entire old region
d<=ell^334. At ell=2^32 it also admits d=2^12000, while the old cap is
2^10688. The separate halo premise is retained. No new kappa is claimed.

[PROOF.md](PROOF.md) gives the interval reduction, new endpoint and
monotonicity argument, and the strict enlargement proof. The predecessor's
interval estimate and the Fiori–Kadiri–Swidinsky prime-counting theorem are
cited inputs. The new result is the dimension region, rather than an
audit of either predecessor or a prime-producer implementation.

## Reproduce

From repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/subexponential-prime-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/subexponential-prime-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/subexponential-prime-dimension
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/subexponential-prime-dimension --check-source-history
```

Another CPython 3.12 installation may replace that interpreter path. The
direct verifier prints a generated JSON record binding all six package
files, followed by `PASS_SUBEXPONENTIAL_PRIME_DIMENSION`. It writes nothing
and needs no Git, network or predecessor runtime input. The package and
source-history checks separately validate the recorded historical pins.

The checker uses exact fractions and integer powers. It checks the four
strict exponential partial sums, the stated endpoint and derivative
fractions, two alternative integer endpoint calculations, the polynomial
containment certificate and the strict enlarged-domain witness. It also
corroborates 24 dyadic endpoints and rejects nine invalid or unsupported
certificate parameters. Rejection of a smaller cutoff certificate does
not mean prime supply fails at that cutoff. The universal statement rests
on the written proof and imported analytic theorem.

## Scope and credit

The `uniform-transfer-audit` card changes to an analytic source-supply side
result connected to `analytic_recovery`. It discharges none of the five
selected assumptions in full. The selected PR6030 baseline returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; that is metadata orientation,
rather than a supplier replay. The working base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

Credit ToikY / PR4029, head `726c9a3a1dc58d2b1223dd681eb712255be407c1`,
for the exact band, caller binding, interval reduction and prior supply
domain. Credit Fiori, Kadiri and Swidinsky for their imported analytic
theorem; Jose Manuel / PR3935 for the tensor interface; Tekalign / PR4024
for the CRT source premise; unpaidmoon / PR4142 for the separate guard;
Cinna Davis, Chafik Boukhalfa, Josie Elliston, the source08 contributors,
Harvey–van der Hoeven and Agarwal–Cooley for the retained selector and
source-construction lineage. Nick Petalas's PR5149 and PR5152 concern the
older polynomial cutoff and product envelope. Their results are credited
context, without being replayed here. Classical exponential estimates and
monotonicity arguments retain their mathematical credit; no global
literature-priority claim is made.

Recent PR6444 improves a setup algorithm at the old abundance domain.
This result supplies a distinct analytic region and does not implement
its open encoded interface. No giant primes are computed. Encoded source
production, all-size physical tensor integration, numerical recovery,
stock, precision/tape, native and compiler obligations remain open or
inherited. No selected cold replay, Lean or Docker is run. Independent
human and formal proof-kernel review are unclaimed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372253)
records the same target. Live PRs and recent handoffs, current main and
merged object/formula/general-region searches, recent account work and
local reservations were checked. Arbitrary historical diffs and unpublished
work remain outside coverage. [TASK.json](TASK.json) records overlap
freshness and the explicit scope change. [SOURCES.json](SOURCES.json)
pins historical provenance; no predecessor code is imported or modified.

## Open next questions

1. Can the original endpoint errors admit a larger coefficient of sqrt(ell)
   in log(d), with an explicit cutoff? This would improve the analytic
   capacity. Start with both unweakened endpoint errors. A uniform error
   comparison and quota argument are still needed; no optimum is claimed.
2. Can a changed complete transform use the expanded dimension region to
   lower its dominant paid bill? Start by deriving that caller's precision,
   halo, source-loading and tensor cost laws. The present source-supply
   theorem alone neither supplies that caller nor changes kappa.

## Code inspection

The verifier has no recursion, subprocesses, writes or dynamic code
generation. Every function is under 60 lines. All loops have fixed caps:
ten series terms, four logarithm certificates, 24 endpoint probes, nine
rejection controls, or six package files of at most 256 KiB. Explicit
exceptions remain active under `-O`. Scalar certificate parameters are
validated before arithmetic. CPython's integer and container allocation
is a managed-runtime deviation from fixed-storage execution; root exponents
are capped at 32, and the largest alternative power is 8^38.
These caps belong to finite corroboration, not to the theorem. Warning-strict
normal and optimized checks provide the local diagnostics. No static
analyzer or literal fixed-storage execution is claimed.
