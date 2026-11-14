# The optimal scale of Gaussian symmetry-orbit certificates

**Scoped theorem and audit; no new kappa.** This package classifies every
exact permutation symmetry of a homogeneous shifted Gaussian tensor and
determines, within an absolute constant, the smallest number of cycles any
one such symmetry can have. It then proves that explicitly materializing
the specified boundary generators still requires almost quadratic space
and writes. Quantitative entry gaps extend the result to stated rounding
models. The lower bound concerns this certificate class, not displacement
rank or all algorithms.

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Published constructor predecessor:
[`8f1a09fb4f696bd5f20e1953210936308571416e`](https://github.com/CubeJerry/integer-mult-bounds/commit/8f1a09fb4f696bd5f20e1953210936308571416e).
Its exact proof-object hashes are independently fetched and recorded in
DEPENDENCIES.json. Earlier published bytes remain unchanged.

## Precise result

On `X={0,...,n-1}^d`, with `n>=2`, `d>=1`, `0<q<1`, `v>0`, let

\[
 H_{xy}=q^{\|x-y\|^2}v^{\sum_i(x_i-y_i)},\qquad T=n^d.
\]

Every exact simultaneous vertex-permutation symmetry is a coordinate
permutation when v!=1, or a signed coordinate permutation when v=1.
Here a coordinate reversal is `x_i -> n-1-x_i`. The classification starts
from arbitrary permutations of all T vertices, rather than assuming a
coordinate action. The inverse has the same group.

Let g(d) be the classical maximum order of a permutation on d letters, and
let c* be the smallest cycle count of an exact symmetry. We prove

| Kernel | Proven bounds on c* |
| --- | --- |
| Common nontrivial shift v!=1 | `T/g(d) <= c* < 4T/g(d)` |
| Unshifted v=1 | `T/(2g(d)) <= c* < 4T/g(d)` |

The upper bound rotates disjoint prime-power coordinate blocks realizing
g(d). Their exact cycle count is a product because all actual component
periods are coprime. A uniform prime-power correction is at most
`(3/2) exp(8/9) < 4`; its exceptional4-cycle case is handled explicitly.
Landau's classical `log g(d) ~ sqrt(d log d)` therefore gives the optimal
logarithmic saving in this certificate class. Maximum order need not
minimize the finite count: at n=2,d=5, lengths2+3 have order6 and12 cycles,
while a5-cycle has order5 and8 cycles.

Concatenating full symmetry cycles yields the predecessor's boundary
decomposition with at most2c terms. The specified dense format stores2c
length-T scalar vectors, so its optimum size is `Theta(T^2/g(d))`, or
`T^(2-o(1))` for fixed n. This eventually exceeds direct dense axis
application's `O(dTn)` scalar bill, even before coefficient construction,
precision and physical transport. The proof also prices a uniform selector,
orbit enumeration and both layout permutations; none is a free service.

## Rounding and its exact limits

For a perturbed table with entrywise error at most delta, the following
sufficient conditions constrain every *exact* symmetry of that table:

| Conditions | Symmetry containment |
| --- | --- |
| v=1 and `2delta < q-q^2` | Signed coordinate permutations |
| `abs(log v)<=-log q` and `4delta+2delta^2 < q^2-q^4` | Signed coordinate permutations |
| Previous row plus v!=1 and `2delta < q abs(v-v^-1)` | Coordinate permutations |

The proof recognizes nearest-neighbor grid adjacency from separated entries
or paired entries, then classifies grid-graph automorphisms. Arbitrary small
perturbations may destroy all nonidentity symmetries, so containment alone
does not preserve the upper construction. A common deterministic rounding
rule preserves coordinate permutations. Common factorwise error epsilon
gives the global error bound `delta<=d epsilon(1+epsilon)^(d-1)`.

For fixed positive constants A,B,C,c, the regime
`d<=P^A`, `P^-B<=q<=1-P^-C`, `abs(log v)<=-log q`, `b>=cP`
eventually satisfies the product gap under common nearest factor rounding
at b fractional bits. This retains `Theta(T/g(d))` even for tiny shifts,
without requiring the directed-shift gap. It is a mathematical parameter
corollary, not proof that an actual source supplies matched blocks or
coefficient-production/precision services. Nonsingularity and stable inverse
rounding are separate obligations.

## Novelty and inherited boundaries

The predecessor constructs useful orbit orderings but does not optimize
their cycle counts or rule out better exact symmetries. This package closes
that specific class-wide question and supplies a matching robust
materialization obstruction. It does not settle the minimum ordinary
displacement rank over arbitrary orderings, because boundary vectors can
cancel or admit another basis. Partial successors, implicit generators,
compressed access and different circuits remain outside the lower bound.

All factors have the same n,q,v. Common shifts require no diagonal gauge.
Heterogeneous phases, physical gaps, periodic tails and source layouts
still need actual compatibility proofs. Any introduced gauge retains its
condition/magnitude range and precision bill. The complete all-axis,
three-transform analytic-recovery service has not been assembled here.
All five retained foundational assumptions remain, and the selected full
multiplication bound and kappa do not change.

The mathematical ingredients are credited background: Landau's maximum
order function and its classical asymptotic; necklace/orbit counting; and
cube/grid symmetries. See Deléglise, Nicolas and Zimmermann,
[*Landau's function for one million billions*](https://doi.org/10.5802/jtnb.644),
JTNB20(2008),625--671, equations(2),(6). The finite characterization and
all package-specific implications are proved in PROOF.md. There is no
global-priority claim for these classical results.

## Reproduction and executed evidence

Python3.12, standard library only, read-only output:

```
python -I -W error -B research/gaussian-orbit-certificate-scale/verify.py
python -I -O -W error -B research/gaussian-orbit-certificate-scale/verify.py
```

Both executed commands print byte-identical JSON matching RESULT.json and
terminate with `status: PASS`. The bounded domains are:

- 7337 integer partitions through d=24, compared with an independently
  organized grouped prime-power dynamic program.
- 178 unsigned and592 signed coordinate-action fixtures, comparing literal
  word orbits with Burnside averages, including odd-alphabet fixed centers.
- 768 maximum-order constructions through d=256 and594 prime-power
  correction cases through block length1024.
- Complete vertex-permutation searches for eight small exact kernels and
  five rounded kernels, including3-by-3 grids and common factorwise rounding.
- Ten negative controls: finite maximum-order nonoptimality, the signed
  factor-two necessity, repeated primes, composite-as-prime counting, the
  exceptional4-cycle estimate, q=1 degeneracy, shift reversal, coarse
  rounding, unequal kernels and tiny arbitrary symmetry-destroying errors.

These are finite independent formulas and checks, not an asymptotic search.
PROOF.md supplies the universal mathematics; the Landau asymptotic is a
named classical input. RESULTS do not certify actual source adoption.
SOURCES.json pins canonical provenance. DEPENDENCIES.json separately records
independently fetched mathematical predecessor objects and their exact
hashes; no foreign executable code is imported or vendored.

## Open next questions

The structured versions are in TASK.json.

1. Can orbit generators be applied implicitly with a full bill below direct
   axis application? Price one family without storing every cT coefficient,
   including precision, access, accumulation and both permutations.
2. Does an actual analytic-recovery source supply homogeneous factors and
   the quantitative global rounding gaps? Pin one phase block and include
   physical gaps, tails, coefficient production and transport.
3. Can arbitrary orderings or other representations have much smaller
   displacement rank? A useful invariant must remain valid beyond the
   global-symmetry successor class established here.

## Credit

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. The
orchestrator proposed the Landau/classification objective and adjacency-gap
rounding extension; the worker independently derived and checked the proofs,
exceptional correction, exact finite controls and complete cost limitations.
The originating orbit package and its earlier displacement/rounding
predecessors retain their credit:
[exact lexicographic displacement theorem](https://github.com/CubeJerry/integer-mult-bounds/commit/326844a3e0c570fdafa4f3737095cd37154743a6),
[quantitative rounding margin](https://github.com/CubeJerry/integer-mult-bounds/commit/575491d5fc353eac26010e45e9ced60fc9870017).
Independent review is a separate gate;
passing executable checks alone is not scientific acceptance or a selected
frontier update.
