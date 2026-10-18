# Bounded independent verification of rounded Newton arithmetic

**Independent verification; no new kappa.** The retained
[Section 09](../../upstream/build/sections/09-exact-arithmetic.tex) reciprocal
and square-root routines meet their stated residual/error bounds for every
real normalized input at each target precision `p = 1,...,8`, under the
prefix-cell argument below. Separate integer-significand and rational ports
agree on every rounded operation in that domain. Exact final corrections
also recover every division and square root in the declared integer domains.
No discrepancy in the retained routines was found.

This checks the downstream exact-arithmetic corollary. As
[the repository audit](../../docs/audit.md) states, Section 09 is not a
dependency of multiplication. The selected conditional result at the base
remains `836330098538459/500000000000000000`; this package neither changes
nor cold-replays its suppliers.

## Evidence and independence

| Completed domain | Coverage |
|---|---:|
| Reciprocal cells, all `c` in `[1,2)`, `p=1,...,8` | 16,320 |
| Root cells, all `c` in `[1,4)`, `p=1,...,8` | 48,960 |
| Outer rounded steps compared | 256,256 |
| Nested reciprocal steps compared | 862,464 |
| Division tuples `(n,a,b)`, `1<=n<=8`, `0<=a<2^n`, `1<=b<2^n` | 86,870 |
| Root tuples `(n,a)`, `1<=n<=8`, `0<=a<2^n` | 510 |
| Additional boundary divisions / roots, through 168 input bits | 4,468 / 270 |

[fixed.py](fixed.py) uses integer significands and shifts; [rational.py](rational.py)
uses `Fraction`, direct floor operations, a separately formed precision schedule
and comparison-based normalization. Neither imports the other. The checker
compares their full traces, including input prefixes, nested calls and all
rounded products. Integer answers are checked against `divmod` and `math.isqrt`.
These are separate implementations by the same AI-assisted author, not an
independent human review.

[CERTIFICATE.json](CERTIFICATE.json) records exact minimum margins, attaining
cell indices, transcript digests, coverage counts and concrete failure witnesses.
Division and root coverage includes zero inputs, leading zeroes, exact quotients
and perfect squares. In the small integer domain, 2,444 division trials and 25
root trials require an increment; the boundary domain has another 666 and 40.
No decrement was encountered in these actual runs. Separate valid approximation
fixtures exercise both directions of each correction.

## Why the finite cells cover real inputs

Fix a tested target `p` and put `T=p+5`. Every read of the original normalized
input is `R_t(c)=2^-t floor(2^t c)` with `t<=T`; the warm-up uses `t=6<=T`.
For a cell `I_k=[k/2^T,(k+1)/2^T)`, every such prefix is constant. Induction over
the deterministic operations therefore makes every stored iterate constant on
`I_k`. The root routine's inner reciprocal reads the stored iterate, so it does
not introduce a finer read of the original `c`.

Let `x` be the computed iterate and `epsilon=2^(-p-1)`. For the reciprocal,
the checker verifies `max(|1-L*x|,|1-U*x|)<=epsilon`, where `L,U` are the two
cell endpoints. Affinity gives the same bound throughout the cell, and `c>=1`
also gives `|x-1/c|<=epsilon`. For the root, it checks `x>=epsilon` and the
exact rational inequalities `(x-epsilon)^2<=L` and `(x+epsilon)^2>=U`.
Monotonicity of the square root gives `|x-sqrt(c)|<=epsilon` throughout the
cell. Checking the excluded upper endpoint is conservative. No floating-point
square root enters these decisions.

The same endpoint checks cover every intermediate outer target. Additional
checks cover the signed reciprocal residual identity, rounding directions,
the nested reciprocal residual, root normalization, quotient error and the
fixed integer guard bounds. This is a finite exhaustive certificate with a
written cell argument, not a kernel-checked proof for arbitrary precision.

## Reproduce and reject altered inputs

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/newton-prefix-audit
```

Expect `PASS_BOUNDED_NEWTON_PREFIX_AUDIT`, seven passing semantic test groups,
then `PASS_REGISTERED_RESEARCH_PACKAGE research/newton-prefix-audit outcome=completed`.
Direct, read-only verification also works with
`python3 -I -B research/newton-prefix-audit/verify.py`. Normal replay compares
the committed certificate and writes no outputs. Explicit regeneration requires
`--write-receipt PATH`.

Sixteen controls reject omitted warm-ups, zero guard bits, a stale six-bit
prefix, wrong inner normalization, omitted correction branches and invalid
inputs. Mathematical mutations include explicit in-domain rational
counterexamples. The seven additional test groups check non-dyadic cell
interiors, the residual sign, scaled outputs, correction hypotheses, source
tampering, implementation separation and recorded coverage. Checks remain
active under optimized Python.

## Sources, scope and credit

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`.
Retained OpenAI source: `adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
[SOURCES.json](SOURCES.json) binds the exact source bytes and Git blobs;
[TASK.json](TASK.json) records seed 84, three candidates, overlap, limits and
the change from the catalogue's formalization card to an executable audit.
No pending PR is a mathematical dependency. The bounded domain was fixed
before the census; the seed also selects input widths 84, 85 and 168.

The new evidence does not establish all-precision induction, physical tape
execution, head-return costs, asymptotic complexity, a supplier interface,
or a complete multiplication theorem. Larger-width fixtures are finite tests,
not uniform coverage at their higher precisions. Hosted CI is separate from
local execution.

Prepared by Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
Credit OpenAI's retained manuscript, its cited classical Brent reductions,
and Douglas Colkitt's repository and audit guidance. Related square-root uses
in PR1293 and `research/u8-supporting-uniform` concern logarithm enclosures and
norm calculations, respectively. They are distinct from this numerical
corollary check. New work is Apache-2.0; the original license and notices remain
at [upstream/LICENSE](../../upstream/LICENSE) and [NOTICE](../../NOTICE).

## Open next questions

Can the source's residual induction be proved mechanically for every positive
precision, with the actual directed rounding and changing input prefixes?
That would replace the finite precision boundary here with a uniform theorem.
A first step is to formalize the signed reciprocal identity and the capped
doubling invariant over exact rationals. A separate source-binding argument
and fixed-tape implementation would still be required. The structured question
and its blockers are also recorded in [TASK.json](TASK.json).
