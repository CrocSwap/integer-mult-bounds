# Two commuting basis shears for the historical complex center

**Finite complex-supplier construction; no new κ.** At h=26, the explicit
factor below reduces the complete gather/scatter bill from **45,381 to
42,600**, and from **43,909 to 42,600** compared with Curtis Dransfield's
pending [PR809](https://github.com/CrocSwap/integer-mult-bounds/pull/809).
Its source reads, both gathers, both scatters and dirty restoration are charged.
It does not introduce runtime center-basis conversion operations.

The complete historical three-stage scalar bound decreases from
**15,959,102,640,000 to 15,846,305,280,000**, saving **112,797,360,000**.
These are symbolic finite-construction operation counts, not measured runtime.
No selected supplier, paid rank profile or multiplication exponent changes.
The base selected conditional κ was **0.001661634653669567**, PR799 with
PR589 on PR555, as read at base
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`.

At the final upstream refresh, main was `47481c89fd30a43f8f882eb4b391e89c29273fd0`
and the accepted conditional κ had advanced to **0.001661957774647029**
(PR890 / U8-T21). Its selected certificate and maintainer review were read.
Every mathematical implementation input used here remained byte-identical.
The base selection is preserved in `BASE-SELECTED.json`, not read from the
mutable current pointer; neither value is a result of this contribution.

## Reproduce

From the repository root, with Python 3.11+ and its standard library:

```sh
python3 -I -B research/dyadic-center-two-shear/verify.py
```

Expected final line:

```text
PASS_DYADIC_CENTER_TWO_SHEAR h=26 G+H=45381->42600 saved=112797360000 no_new_kappa
```

The command verifies source pins, reconstructs the factor and complete
historical invoice, replays the declared finite search, executes the dirty
interfaces, and compares every receipt field against `EXPECTED.json`.
It writes no files. `--write` deliberately regenerates that package receipt.
With `-O`, it starts a normal isolated child so inherited assertions remain
active. `independent.py` can also run alone from any directory, including
under `-O`; it imports no repository implementation or receipt.

## Explicit construction and proof

Let S,T range over the triples of {0,...,h−1}; write s_i,t_i for membership
indicators, and n=binom(h,3). Define the h-by-n gather V and n-by-h scatter U:

```
V[0,T] = 1                   U[S,0] = 3*s_0 - 1
V[i,T] = t_i   (1 <= i < h)  U[S,i] = s_i - s_0   (1 <= i < h).
```

The exact central map is U V / 2, because

```
(U V)[S,T] = 3*s_0 - 1 + sum_{i>=1} (s_i-s_0)*t_i
           = sum_{i>=0} s_i*t_i - 1,
```

using sum_{i>=1} t_i = 3−t_0. This is the same central map as
Douglas R. Colkitt's original rank-h factor in
[`complex_centers.py`](../../scripts/experiments/complex_centers.py).

In terms of that original factor, this is
A=(I+E_20)(I+E_10)=I+E_10+E_20, V'=A V, U'=U A^{-1}.
The two shears commute and are unimodular. They change the specification of
the gather/scatter tables; **A is not executed on live center registers**.
Every gather coefficient is 0 or 1. Scatter numerators remain in the original
allowed set {−1,0,1,2}; no additional scalar alphabet or odd division is needed.

For arbitrary initial centers c, the forward central operations are:

```
y -= U*c/2;  c += V*x;  y += U*c/2;  c -= V*x.
```

Thus y gains U V x/2 and c is restored exactly, including its arbitrary dirty
input. Reversing order and signs gives the inverse. The unchanged side circuit
adds +1/2 for disjoint triples and −1/2 at intersection size two; combined
with (|S∩T|−1)/2 this is exactly the identity on triples. The existing
12-operation signed invocation therefore still sends y to y±x and restores
x and every arbitrary side/center auxiliary. Three signed invocations with
reuse of the first dirty bank give the same bank exchange.

The inherited phase argument groups **all** data/center incidences at each
common frame, including zero coefficients. This contribution retains those
groups and all h center roles. It does not infer geometry from a sparse scalar
list, delete zero-incidence frame participation or change frame scheduling.
The original [phase/invoice argument](../../notes/dyadic-central-factor.tex)
then gives the same h² downward dimension per invocation, endpoint frames,
rank profile, recursive children and all-size hypotheses.

## Complete accounting and parameter scope

Let d=binom(h−1,2), e=binom(h−2,2). Counting the table entries gives

```
G_new = n + (h−1)*d
H_new = 2*n − d + 4*(h−1)*e
G_old = 3*n + (h−5)*d
H_old = 2*binom(h−3,3) + 6*(h−3) + 1 + 4*(h−1)*e.
```

G charges every nonzero gather source read/addition. H charges a scatter
numerator ±1 as a halving plus an addition and numerator 2 as one addition.
With the unchanged side mixer M, source copies C, weighted injections J:

```
complete signed invocation = 4*M + 2*C + 4*J + 2*G + 2*H
complete three-stage scalar bound = 3*n² * (4*M + 2*C + 4*J + 2*G + 2*H).
```

| h=26 bill | Original | PR809 single shear | Two shears |
|---|---:|---:|---:|
| G+H | 45,381 | 43,909 | 42,600 |
| G | 14,100 | 12,352 | 10,100 |
| H | 31,281 | 31,557 | 32,500 |
| Complete three-stage bound | 15,959,102,640,000 | 15,899,398,320,000 | 15,846,305,280,000 |

M=158,444, C=J=10,400. The candidate saves 5,562 operations per signed
invocation against the original, or 2,618 against PR809. Its three-stage
saving against PR809 is 53,093,040,000; the total saving against the original already includes the predecessor
saving, which must not be added again. Scatter is more expensive; the net
saving is the result of complete accounting.

The difference in G+H is
D(h)=2*binom(h−3,3)−3*binom(h−1,2)+6*h−17.
D(8)=−12 and D(10)=5. For even h>=10,
D(h+2)−D(h)=2*h²−18*h+33>0, so the saving is positive.
The identity is valid at h8; **it is not a cost improvement there**.

The finite ledger W=1,247,192,960,000, m=17,576,
s=21,920,655,731,520,000, side roles=89,622 and center roles=26 is unchanged.
The same conservative E=64*(W+m+1)^3 passes the complete node charge and
recurrence guard with greater scalar slack. This retains the existing
add/subtract/halve depth argument; no sharper intermediate norm or precision
bound is claimed. The historical supplier saving interval is unchanged.
Changing this scalar bill alone cannot improve the retained rank-based κ.

## Search, one algebraic revision and overlap

The OS-random assignment seed was **39**, complex-supplier track. `CLAIM.json`
records three candidates, the local claim, base and time budget. There was
no pinned sprint coordination issue. The seed rotates the ordered census by
39, including tie-breaking; it does not make an otherwise duplicate result new.

The bounded experiment fixed PR809's A=I−E_12 and examined exactly **1,300**
second signed elementary shears at h26. Exactly **602** preserve the priced
alphabet (gather ±1, scatter numerator at most 2 in absolute value). The
unique cheapest admissible continuation is (i,j,sign)=(2,0,+1), at **43,128**.
The receipt preserves the full-domain histogram and a canonical hash of all
1,300 move outcomes. Reproduction recomputes every move, not just the winner.
No random sampling, early termination or further numerical search was used.

That witness has V_1=t_1−t_2 and V_2=t_2. One deterministic algebraic
simplification, V_1←V_1+V_2 with its conjugate U update, gives 42,600 and
simplifies to the commuting two-shear formula above. This is the one
recorded evidence-driven revision. The final factor is **not claimed optimal**
over two-shear factorizations, unrestricted bases or scalar circuits.

PR809 at `66cabb478385fbaa1a8060123cd57545d703d84e` is credited for the
single-shear mechanism and comparator. Its implementation is not imported;
its factor is reconstructed from the published A=I−E_12. PR863 changes the
side disjoint-tensor contraction, and recent PR922/924/931 concern the distinct
eight-register raw factory. None is composed here. `OVERLAP.json` records the
fresh metadata and explicit distinction; PR claims are not selected results.

## Verification and remaining obligations

`EXPECTED.json` contains the exact deterministic receipt and invoice.
`SOURCES.json` pins all consumed repository implementation files and the
base selection snapshot separately; historical source commit is
`d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`.

The primary checker validates all 6,760,000 h26 matrix entries for both the
original and new factors with the retained source verifier. It rebuilds and
checks the unchanged side circuit, both orientations of its physical frames,
shared matching, complete scalar/node charges and recurrence guard. A separate
value-free instrumentation of the actual invocation independently counts
786,938 original and 781,376 candidate primitives in each direction. It
executes the entire signed invocation on independent symbolic input columns
at h8/h10 in both directions, four dense dyadic h26 cases and a reused-bank
three-stage case.

The separate integer checker directly constructs the formula and checks
6,777,536 coefficient positions across h8/h10/h26. Its exact symbolic central
replay covers all 5,226 independent source, target and arbitrary dirty-center
columns at h26, in both directions. It imports no repository code or receipt.
Missing conjugate updates, wrong coefficients, omitted compensation/delivery
and failed auxiliary restoration are rejected. Package controls also test
source and receipt corruption; exact execution evidence is in `VALIDATION.md`.

This is finite evidence with a written general factor/cancellation proof,
not formal verification of the full multiplication theorem. The all-size
compiler, common-label/mutable-source realization, hosting, precision/tape
and analytic-transfer obligations remain inherited. Transport into the later
selected supplier, new global invoice/owner admission and selected outer
assembly are unperformed separate work. No new κ, Lean proof or CI result is
claimed. `upstream/`, selected records, production generators and unrelated
artifacts are unchanged.

## Attribution and license

Prepared by **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance**, including scoped AI implementation and adversarial
review; no independent human review is claimed. Credit **Douglas R. Colkitt**
for the original central factor, disjoint tensor circuit, signed invocation,
phase and recurrence ledger; **Curtis Dransfield** for PR809's basis-shear
mechanism; and the retained source notices and supplier lineage. The selected
context credits Jeremy Kothe, Chafik Boukhalfa, DreamingOfClouds and eumemic.
New contribution: Apache-2.0, consistent with the repository license.
