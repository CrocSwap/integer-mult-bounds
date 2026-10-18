# Historical prime-subset ceiling: source closure and harmonic reconciliation

**Research consolidation and independent arithmetic evidence; no new kappa.**

The archived common-subset prime-power certificate reproduces in full. Its five
`source_sha256` entries cover four of the sixteen local Python modules in the
producer's conservative import closure, plus its explanatory note. This package
pins forty source/input files, demonstrates a concrete serialization gap, and
independently corroborates the historical exclusion using harmonic sums instead
of either the producer's logarithm routine or floating-point calculations.

The exact base is **`407d52ff15b2217b6e22bce44728b4c3907b6515`**, assignment seed
**98**, research-consolidation track. At that base the selected conditional
result is PR942/T37, `1661960547713947/10^18`. This package concerns an older
construction family; it does not constrain that selected construction.

## Reproduce

From the repository root, with Python 3.11+ and only the standard library:

```sh
python3 -I -S -B research/prime-subset-reconciliation/verify.py
```

Expected final line:

```text
PASS_PRIME_SUBSET_RECONCILIATION 626 historical cases; 662 harmonic cases; tail h>=67; complete replay equal; no new kappa
```

The command verifies all source pins before predecessor execution, computes the
independent arithmetic, reproduces every original certificate field in an
isolated temporary directory, and executes the controlled serialization mutation
there. The reference output is absent before each producer execution. Runtime
local imports must lie within the pinned static closure. The deterministic exact
report must equal [RESULT.json](RESULT.json); `--out /a/fresh/report.json` writes
it to a new path instead. Existing output files are refused.

Normal and optimized execution are supported. The companion uses explicit
exceptions; its historical child process deliberately keeps assertions enabled.
No checkout file is regenerated or modified. JSON comparisons preserve types and
reject duplicate keys. Only object key order and whitespace are normalized.
The receipt hashes the complete source-manifest JSON canonically, so LF/CRLF
conversion of that new JSON container cannot change the mathematical receipt.
All immutable producer and upstream input hashes still bind exact file bytes.

Run the focused controls separately:

```sh
python3 -I -S -B research/prime-subset-reconciliation/test_reconciliation.py
python3 -B -m unittest discover -s tests -p test_prime_subset_limits.py -v
```

## Concrete dependency discrepancy

The original driver imports `prepare_layers.serializable`, but the historical
source inventory does not pin `scripts/prepare_layers.py`. In a temporary copy,
change its Fraction serialization from `str(value)` to `str(value + 1)`.
The producer still prints its original success marker and all five historical
source digests still match. The emitted target becomes `67108865/67108864`
instead of `1/67108864`; every other emitted Fraction is shifted too.

The new complete input binding detects this helper change before execution.
`RESULT.json` records the unchanged old digest fields and the exact target
difference of one. This is a controlled output-corruption demonstration and an
incomplete provenance binding, **not** a mathematical counterexample, a failed
committed audit, or corruption of the archived evidence. The original source
inventory is retained unchanged.

[SOURCE-PINS.json](SOURCE-PINS.json) pins the driver, all sixteen local modules,
the two written mathematical scopes, the original certificate and focused tests,
the upstream manifest and every file it checks. The imported upstream source is
unchanged at `adc7f1241b42e322a6451854ab7e4b4c146bf78a`. Fifteen local modules
appear in `sys.modules` during replay; the driver is executed by `runpy` and is
the sixteenth static entry. Twelve local modules are absent from the old source
inventory. Static closure includes function-local imports conservatively; it is
not a claim that every function in every module executes.

## Independent rational exclusion

Retain the historical hypotheses: prime-power `q>=2`, `k=2q-1`, `j=q-1`, all
`k`-subsets on a ground set of size `h`, the incidence center and indicator
frames, the shared three-stage rank ledger, distinct common-subset partial
outputs in a cancellation-free `c+u` side compiler, and `kappa<a_b/5`.

Write `n=C(h,k)`, `r=C(h,j)`, `M=C(k,j)`. The predecessor's written
support-reconstruction argument gives `S>=2*M*n`; the rank ledger gives

```text
eta_max = (n-6*r*h) / (2*h^3*(n+2*M*n+r)).
```

Nonpositive deficit cases cannot supply a positive saving. For the others,
the retained exponent formula and `-log(1-x)<x/(1-x)` give

```text
kappa < eta_max / (5*(1-eta_max)*log(h^3)).
```

Let `H_h=sum(j=1..h, 1/j)`. Integrating `1/t>1/j` over each interval
`[j-1,j]`, `j>=2`, proves

```text
log(h^3) > L_h = 3*(H_h-1).
```

Thus replacing the logarithm by `L_h` gives an upper bound with rational
arithmetic only. `independent.py` constructs prime powers by a prime sieve
followed by repeated powers, separately from the old `characteristic` function.
It checks all **662** admissible `(q,h)` cases with `2q-1<=h<67`, including
**325** positive-deficit cases. The largest rational upper bound is

```text
q=3, h=29:
36799615092240/4134187365781280125763
  approximately 8.901293491637769e-9 < 2^-26.
```

For the infinite tail, retain the transparent side-rank hypothesis `W>=4*n^3`
and `Delta<n^3`. These imply `eta<1/(4*h^3)` and therefore

```text
kappa < 1 / (5*(4*h^3-1)*L_h).
```

Both positive denominator factors increase with `h`. At `h=67` this upper
bound is exactly

```text
586754675813993273505638720/40123319207466471456941015465689083
  approximately 1.462378206498941e-8 < 2^-26.
```

Monotonicity therefore excludes every `h>=67`, for every prime power. The
finite domain covers the remaining admissible cases; `h<2q-1` is undefined
for this subset family. The harmonic tail is weaker than the original
logarithmic enclosure's `h>=65` tail. Its **36** additional finite rows close
that elementary bound, rather than reopen a construction search. Every one of
the original **626** rows has independently recomputed sign/count/deficit
fields; its **301** positive rows lie below the new rational envelope. Exact
historical logarithm values are covered by the complete predecessor replay.

## Verification scope and attribution

The infinite conclusion follows from the stated inequalities and monotonicity,
not finite enumeration alone. Incidence rank, distinct-output geometry,
transparent restoration/rank accounting and the historical Gaussian assembly
are inherited written hypotheses, not newly formalized here. There is no
general circuit lower bound, full Lean multiplication proof, measured runtime
claim, construction improvement or impossibility theorem for other networks.

The original mathematics and historical audit are Douglas R. Colkitt's, with
the repository's existing AI-assistance disclosure. **woklerx's PR970**,
`research/bit-compression-provenance`, supplies the credited source-closure,
isolated-replay and type-sensitive comparison pattern adapted here for a
different certificate and arithmetic obligation. **David Breslauer's PR960**
is separate positive-binomial arithmetic work and supplies no code here.
No priority is claimed for the original family obstruction.

New work was prepared by **OpenAI Codex for the requesting contributor**, with
substantial AI assistance in reasoning, code, controls and documentation. No
human identity or independent human peer review is asserted. New files use the
repository's Apache-2.0 license; original source bytes and notices are preserved.
The final overlap refresh found **woklerx's concurrent
[PR996](https://github.com/CrocSwap/integer-mult-bounds/pull/996)** at
`07b7a5710f31829a56698b2455af6788c70ad317`. That note compares historical and
balanced assembly ceilings using rational logarithm enclosures. The present
package independently corroborates its historical component with harmonic sums
and adds complete producer binding and the serialization control. No PR996 code
or balanced-assembly claim is imported; the different assembly rules must retain
their separate hypotheses.
[CLAIM.md](CLAIM.md) records scope, candidates and coordination. Local checks
and their limits are recorded in [VALIDATION.json](VALIDATION.json). Hosted CI,
repository-wide `make verify`, and the unchanged selected supplier's cold replay
are separate and were not run for this additive package.
