# Paid complex connector repair when both reader and source change

**Scoped interface proof and exact fixed-map pilot; no new κ.** A dirty
connector can pass from `z=z_initial+B0*x` to `z=z_initial+B1*x_new` after
`x_new=x+C*u`. The necessary post-update repair is

```
z += (B1-B0)*x_new + B0*C*u.
```

The reader-change and source-change terms may share a rank-one image. Our
three-coordinate pilot exploits that sharing with a **sharp five-ADD repair**,
including restoring the borrowed source coordinate. Two closed calls require
41 signed scalar ADDs; the carried pair requires 33. Both compute the same map
on arbitrary dirty complex inputs, preserve `u` and `z`, and return both heads.
In the explicitly defined fixed-cell cost model below, their complete costs
are 2,002 and 1,630 unit steps. These counts are not measured bit complexity or
a replacement supplier moment.

This extends woklerx's fixed-reader, characteristic-two source-mutation pilot
[#1439](https://github.com/CrocSwap/integer-mult-bounds/pull/1439), pinned at
`3852c2d03044895cebdc9b31b0c7131a617774d2`. The new features are a changing
reader, characteristic-zero signed readouts, a jointly priced repair and its
five-ADD minimum. Ross Richardson's [universal-connector interface](../universal-connector-boundary/README.md)
is the earlier dirty-row model. The five-source/two-connector transfer searches
in #1438 and Discussions #1412/#1486 are different experiments.

## Exact contract and proof

Work over a field, including Q and C. Let `x,u,z,y0,y1` be distinct arbitrarily
dirty rows; fixed compatible linear maps need not commute or be invertible.
A complete additive call preserves other rows, restores private scratch and
returns its heads. An open connector is reserved and cannot be observed or
borrowed by an unrelated call. The source mutation is part of the requested
map, and the borrowed source coordinate is unobservable during the repair.

The target is

```
x_new = x + C*u; u_new=u; z_new=z;
y0_new = y0 + A0*B0*x;
y1_new = y1 + A1*B1*x_new.
```

Execute this signed word, with the repair after the source update:

```
y0 -= A0*z; z += B0*x; y0 += A0*z;
x += C*u;
z += (B1-B0)*x + B0*C*u;
y1 += A1*z; z -= B1*x; y1 -= A1*z.
```

The first difference cancels all original connector dirt. Before repair,
`z=z_initial+B0*x_old`. Since `x_old=x_new-C*u`, adding the displayed repair
gives `z_initial+B1*x_new`. The last difference produces the second product
and restores the connector. Every source version and sign matters. Neither
output is written before its own call interval; the first output can be
observed after its first readout completes. No k-call early-prewrite claim is
made here. Literal reversal with every sign negated restores the entire input,
including the intended source mutation.

For a source-preserving post-update adapter `z += R*x_new+S*u`, correctness for
all inputs holds **iff** `R=B1-B0` and `S=B0*C`. Indeed `x_new,u` are independent
because the source update is invertible; compare their coefficients in the
required boundary. A pre-update repair instead uses `B1*C*u`. Applying that
version after the update generally double-counts `(B1-B0)*C*u`.

Let `M=[B1-B0 | B0*C]`. In an abstract alphabet of source-preserving outer-product
updates `z += b*ell(x_new,u)`, the exact minimum number is `rank(M)`: rank
subadditivity gives the lower bound and a rank factorization attains it. That
statement does **not** make reading `ell`, changing basis, forming coefficients,
or preserving scratch free. The pilot below pays those operations literally.

## A sharp five-ADD adapter and the priced pilot

The matrices, every gate and the repair's half-open gate range are committed
in [GATES.json](GATES.json). Their entries are integers; all executed
coefficients are ±1, so there is no unpriced scalar multiplication.

```
B0 = [[1,-1, 1], [1,0,-1], [1,-1,0]]
B1 = [[1, 0, 1], [1,1,-1], [1, 0,0]]
C  = [[0, 0, 1], [0,0, 0], [0, 0,0]]
A0 = [[0, 1, 0], [0,0, 1], [1, 0,0]]
A1 = [[1,-1, 0], [0,1, 0], [0, 0,1]]
```

Both readers have rank three. Writing `b=(1,1,1)^T`, we have
`B1-B0=b*e1^T` and `B0*C=b*e2^T`. The joined adapter has rank one although
pricing the two terms separately gives rank two. The literal repair is

```
x[1] += u[2];
z[0] += x[1]; z[1] += x[1]; z[2] += x[1];
x[1] -= u[2].
```

All rows start dirty. The final subtraction is mandatory source restoration;
no clean temporary, COPY, overwrite or recursive call is hidden. The pilot
uses zero-based coordinate 1 from `seed % 3`, and source coordinate 2 from
`(seed // 3 + 2) % 3`, with assignment seed 28. Seed diversity does not establish
novelty; changing the reader is the substantive scope difference.

**Five is minimal for this adapter in the five-row signed-ADD alphabet.**
Let its inputs be independent dirty scalars `p,q,z0,z1,z2`, and require
`z_i += p+q`, preserving `p,q`. Every `z_i` must be written at least once.
If either source is written, at least two source writes are needed: a single
nonzero elementary shear cannot leave that source unchanged on all inputs.
Thus this case needs at least five ADDs. Otherwise `p,q` remain fixed. The
coefficient matrix of original `z` dirt in the current three targets stays
invertible under target-to-target shears; source-to-target shears leave it
unchanged. A target written only once can neither acquire both `p,q` from one
unchanged source nor read a target without unwanted original target dirt.
So each target needs at least two writes, totaling six. The five-gate word
attains the better lower bound. This proves a restricted scalar-operation
minimum, not optimality of the complete two-call program or a supplier.

An exact meet-in-the-middle check corroborates that statement: all 40 signed
ADDs between distinct rows, all words of length at most two from identity and
from the target, 1,121 unique states in each ball and no intersection. Since
the alphabet is inverse-closed, this excludes every word of length at most
four. The proof above supplies the non-computational argument.

The closed baseline and carried pair have these scalar budgets:

```
closed:  2*7 + 2*6 + 2*3 + 2*4 + 1     = 41
carried:   7 +   6 + 2*3 + 2*4 + 1 + 5 = 33
```

For complete direction-symmetric call costs, the corresponding stopping rule
is `c_repair+(I_carried-I_closed) < c_B0+c_B1`. Here `I` includes all preparation,
frame admissions, reserve width, dispatch and hosting opportunity costs.
Use orientation-specific costs when inverses differ. Runtime matrix products
are not free: this pilot compiles fixed coefficients into the instruction
word. A dynamic implementation must price their computation separately.

The declared pilot model stores the five width-three rows in data cells 0–14.
Each signed ADD visits its source, visits and updates its target, then returns
the data head to cell 0: `2*max(source,target)` movements, two cell reads, one
cell write and one signed scalar addition. A separate instruction head reads
one nine-bit fixed record (four bits per address and one sign), advances
through the program, then rewinds; this pays nine bit reads, eighteen head
steps and one decode/dispatch per gate. Signs and source/coefficient access
are included. The independent engine follows the actual visits and checks
690 versus 574 data-head steps. Static fixed-map compilation is outside the
executed pilot, and both programs use the same cell arithmetic contract.
Complex-cell reads/additions have unit prices here; arbitrary precision,
finite-precision error, compiled bit cost and all-size realization are open.

## Exact evidence and bounded coverage

[EXPECTED.json](EXPECTED.json) is reproduced, not trusted as a proof oracle.
The constructor checks all fifteen independent input columns with integer
coefficients. Equality of these linear maps implies equality for all complex
inputs; this pilot identity is not merely a finite random test. A separate
interpreter uses exact Gaussian integer pairs, thirty real/imaginary basis
inputs plus 64 deterministic dirty fixtures, their `I_L` extensions at
`L=1,2,3`, and literal inverse recovery: 1,128 lane evaluations total.

The census covers **all 4,096 ordered triples** `B0,B1,C in {0,1}^{2x2}` interpreted
over Q. It checks the complete signed word on ten independent dirty input
columns. Joint adapter ranks 0/1/2 occur 49/1,027/3,020 times. Separate rank
pricing overcharges by 0/1/2 in 2,011/1,845/240 cases. A second implementation
checks every rank by exact two-by-two minors. This domain is evidence of shared
repair opportunity, not a probability model for selected helpers.

Nine named faulty-word or adapter controls cover missing repair, unrestored
borrowed source, wrong sign, old-reader closure, characteristic-two readouts,
missing dirty prewrite, baseline cleanup, wrong post-update reader version and
reversed product order. An additional independent gate corruption must fail.
The census also records 3,840 omitted-reader, 3,312 omitted-source and 2,784
reversed-product counterexamples. These are actual unequal maps, not failed
searches or missing-proof allegations about the selected result.

## Reproduce and scope

From the repository root, Python 3.12 and standard library only:

```sh
python3.12 scripts/research_package.py --package research/complex-moving-reader-seed28
```

Expected: `PASS_COMPLEX_MOVING_READER`,
`PASS_INDEPENDENT_COMPLEX_MOVING_READER` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
The replay is subsecond on the development host; no repository-wide
regeneration is required. `verify.py --write` rebuilds only the two local
receipts. Exact base, input hashes, predecessor pins, assignment, three
considered candidates and overlap limits are in [SOURCES.json](SOURCES.json)
and [TASK.json](TASK.json). The [claim](CLAIM.md) is Discussion #1489.

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The selected #1094 construction
and κ remain unchanged. No selected helper has yet been instantiated with this
contract; there is no paid child histogram, hosting admission or contracting
multitype recurrence. The inherited all-size/compiler, mutable-source/common-label,
whole-call hosting, precision/tape, analytic and bit H1–H5 obligations remain.
The selected full cold replay was not needed or run for this isolated pilot.

## Open next questions

Extract one actual consecutive complex-call boundary with changing readers.
Compute both adapter terms and check whether their common image yields a cheap
literal implementation. Then compare complete direction-specific costs and
reserve-width/hosting costs before any owner search. The blocker is an actual
selected-call boundary and paid admission, not the matrix identity. Structured
first steps and blockers are retained in `TASK.json`.

## Credit and license

Prepared by Cinna Davis (`1337isnot1337`) with substantial OpenAI Codex
assistance in derivation, implementation, verification and writing. New work is
Apache-2.0. Credit woklerx for #1439's coherent source-mutation boundary and cost
stopping rule, Ross Richardson for the universal dirty-connector/PR934 lineage,
and Ali Romman for the frozen heterogeneous-owner contract boundary. The
selected #1094 lineage credits Rohan Arun, Jeremy Kothe, Hao Yan and the earlier
complex and PR589/PR555 bit contributors in the maintainer review. We copied
no predecessor implementation. This is agent-produced evidence awaiting
independent human review, not a formal multiplication theorem.
