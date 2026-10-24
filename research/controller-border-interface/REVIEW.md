# Author-side independent mathematical review

This review was performed in a separate OpenAI agent context for Dillon on
2026-10-22. It is independent author-side AI checking, not independent human
review or formal-kernel verification. The package's authenticated source pins
remain the authority for the inherited native contracts and invoices.

## What was checked

The all-p proof in DISCOVERY.md was checked against the source chronology:
the forward and backward shears, both bridges, the reverse bridge chain and
final signed swaps. The displayed upper X block and lower Y block agree with
that chronology. Opposite weights on the X and Y chains make every nonzero
off-diagonal coefficient have positive epsilon degree. The endpoint degree is
p-1, while its diagonal is unchanged. This reasoning uses commuting formal
units and the stated arbitrary-input native endpoint, including its separate
helper block. It does not evaluate formal variables at Fourier characters or
replace the physical complex Q inverse by Q.

`independent_check.py` uses a separate exact implementation with no imports
from the construction or its predecessor emitter. It executes numerical
rational shears on every input column and compares with separately hardcoded
p2 and p3 matrices. Across 24 parameter instances it verifies their complete
matrices, forward Lagrange extraction, and inverse-transpose extraction with
the opposite scalar wrappers. Forty-eight wrong-weight controls fail as
required. These finite rational checks support the symbolic proof; they do
not establish the all-p identity by enumeration.

The checker also multiplies polynomial matrix factors for four triangular
chains of lengths 2, 4, 8 and 16. Their actual top-right coefficients have
those respective epsilon degrees, despite binary execution trees of depths
1, 2, 3 and 4. Reversing the factor order destroys that coefficient. This
checks the generic degree-growth counterexample in EXACTIFICATION.md, not a
claim about the actual native compiler's degree.

Nine exact dyadic scalar circuits test the approximation lemma's precision
accounting. Each has gates epsilon^h, 1+epsilon and epsilon^-h, with a positive
additive error immediately before the final gate. The funded precision
succeeds; omitting the h*k conditioning term fails. The finite complex norm
lemma was also reviewed algebraically: the border error and propagated
additive errors each use at most one quarter of the requested tolerance.
The magnitude bound follows from the same subword norm hypothesis.

The added raw forward-controller bound was reviewed at the level of completed paid
oracles. Under its explicit norm contracts, multiplying per-record bounds
gives `H_0(f)=2^(R f+S)`. Disjoint-role wrapper scalings require only the
largest inverse epsilon power, so `h_f=p-1`. The two-term off-diagonal
formulas give the stated exponential-in-f forward remainder bound. Bounding
the initial `D_0=F_9 Q^-1` by its two factors avoids relying on native phase
cancellation. This establishes
linear-in-f logarithmic constants for the fixed raw controller under those
contracts, not for the backward endpoint remainder, paid-oracle interiors
or an amplified recursive compiler.

The BUDGET.md proof was checked separately: scalar border transformations
preserve the formal stage determinant degrees; fixed output count and rank
mass give the Jensen upper bound; rank separation makes the unlinearized
normalized envelope monotone. The 48-bit outward rational power engine uses
integer nth-root comparisons. The proof correctly retains fresh independent
helpers in every repeated evaluation, credits main outputs once, and rejects
K>=2 whole-unit evaluation policies at every t in [0,1]. This result depends
on the stated inventory, output count and rank-mass model.

For DECODER.md, writing U=(I-S)D+S and requiring M U+N=D makes independent
coefficient comparison force M=(I-S)^-1=I+J and N=-J. Its rank is p-1 over Q
and over F2. This proves the fresh-query lower bound in that explicitly
restricted endpoint decoder model. It is not a lower bound against reuse of
internal transcripts, cross-port schemes, changed native words or general
operator-valued adapters.

## Ownership and implementation limits

The source native endpoint is valid on arbitrary inputs. Consequently,
main-only scalar conjugation leaves the separate arbitrary helper outputs
unchanged. Finite interpolation can legitimately retain a fresh helper set
for each evaluation. Copied main fields are owned scratch and receive no
additional productive credit. Running the final evaluation in place on the
original main owners allows earlier copied outputs to be accumulated without
erasing any original input owner. Copying, charts, scalar operations, movement,
storage and owned erasure still need their physical implementation and cost.

A nonzero epsilon execution is a coupled endpoint. It is not already the
exact diagonal supplier required by the chronological compiler. The complex
approximation lemma is a conditional finite-circuit numerical result. Its
raw all-column macro bounds follow under the stated completed-oracle norm
contracts; native numerical oracle interiors, legally amplified all-column
bounds, recursive precision, scalar implementation and physical costs remain
open. Its constants cannot simply
be reset independently at every recursive call.

Reduction of an integral formal identity modulo two does not create small
native BIT scalars. Ordinary BIT has no Archimedean limit. Finite extensions
or polynomial-coordinate representations require explicit native operations,
coordinate charges and return costs. The complex approximation result does
not discharge any of those obligations.

## Reproduction and review status

The direct check completed with Python 3.14.7 and Python 3.12.15, including
optimized mode:

```sh
python3 -I -O -B research/controller-border-interface/independent_check.py
```

Three separate temporary-file mutations were also rejected under Python
3.12.15 with `-I -O -B`: reversing the p2 X-coupling sign, using forward
weights in the backward extraction, and dropping the conditioning bits from
the precision request. Each failed its corresponding mathematical check.
No package source was edited for those mutation executions.

The mathematical review above found no remaining contradiction in the stated
scoped claims. Clarifications about retaining fresh helper credit, reversing
inverse-transpose wrappers, restricting the repeated-evaluation ratio, and
keeping determinant rank credit source-compatible were communicated during
review. The package reports no new admitted supplier, certified kappa or
complete multiplication theorem.

## Open next questions

Can a legal amplification or shared-query implementation bypass the priced
whole-unit extraction and fresh-query decoder policies? Its first obligation
is a complete arbitrary-input endpoint and ownership schedule, followed by
its paid inventory. Existing erased query transcripts are not automatically
available. Can the complex border instead satisfy one global all-column
approximation and precision contract at the actual recursive caller? The
finite norm lemma identifies sufficient numerical hypotheses, but the native
program and caller must supply them.

Apache-2.0. Credit the native/controller work of zxv and Cinna Davis, the
compiler work of Jacob Alan Sussman, and the predecessor sources retained in
SOURCES.json. New review and independent checks prepared with substantial
OpenAI assistance.
