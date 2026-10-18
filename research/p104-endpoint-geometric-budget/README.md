# P104 separate endpoint geometry and two-history budget

PR2909's endpoint-count curve is attainable by actual subspace unions at each
endpoint separately. Within its two history types, the unique cheapest helper
multiplicities at every positive saving are zero cheap helpers and 208
unit-step helpers. Under PR2675's declared transport and ideal-idle screen,
that profile has moment about **0.9988962438816702** at the selected complex
saving. Its relaxed root satisfies the exact rational bracket

```text
0.002104152801941 < a_two_type < 0.002104152801942.
```

This closes the separate-endpoint subspace-union and pricing questions in
[PR2909](https://github.com/CrocSwap/integer-mult-bounds/pull/2909). It does not
construct a correction network. An individual flag's ability to contain labels
does not establish that a helper acquires those labels from the actual sources.
Source/target flags are chosen independently in this relaxation.

## Contract and predecessor scope

Retain the fixed PR1972/1991 P104 channel and the X-only monotone model from
PR2353, PR2614 and PR2896/2909. The correction adds `I-G/2` to unread Y,
reads immutable X along their frozen paths, and uses new helpers with
source-independent dirty inputs at ZERO, increasing frames, restoration at
FULL, and equal-frame rational operations. Original helper/private reads,
source writes, target feedback and descending transports are excluded.
Reinitialization starts a new lifetime. These restrictions belong to the
audited route, rather than every possible P104 construction.

The two helper types are dimension jumps

```text
cheap:     (1,7,1)
unit-step: (1,1,1,1,1,1,1,1,1).
```

At target hyperplane H, a cheap helper's last proper frame is a line, while a
unit helper's is dimension seven. Dually, at source line L, a cheap helper's
first superframe is dimension eight, while a unit helper's is dimension two.
The departure normal spaces are proper subspaces of the eight-dimensional
annihilator `L^perp`. These are the separate endpoint covering sets considered
here. Specifying those sets supplies no source acquisition or coefficients.

PR2909 proves the necessary count relaxation with endpoint demands d and
one-unit capacities b. Both orientations have these types:

| d | b | d-b | Number of endpoints |
|---:|---:|---:|---:|
| 36 | 24 | 12 | 12 |
| 44 | 28 | 16 | 24 |
| 45 | 30 | 15 | 8 |
| 46 | 29 | 17 | 24 |
| 47 | 30 | 17 | 24 |
| 48 | 30 | 18 | 12 |

Its 192-unit threshold at a 400-helper budget is retained. This package adds
geometric attainment in the separate covering problem and optimizes its price.

## Affine-complement lemma

Let D span an eight-dimensional binary space H. Suppose a linear functional q
takes value one on every point of D. Choose a proper hyperplane `ker(f)`
maximizing `b = |D intersect ker(f)|`. Since `0 < b < |D|`, f is neither zero
nor q on H. Therefore both `ker(f)` and `ker(f+q)` are genuine dimension-seven
subspaces of H. On D, `f+q = f+1`, so their intersections with D are disjoint
and cover D. They have sizes b and d-b. This proves exact two-subspace coverage,
beyond the inequality `d <= 2b`.

Every chosen dimension-seven arrival frame extends to a complete unit-step
flag inside H, followed by FULL. A demanded singleton extends to a cheap
line/H/FULL flag. On departure, a dimension-seven normal space V in `L^perp`
gives a dimension-two frame `V^perp` containing L, extendible to a unit flag.
A singleton normal n gives the cheap superframe `ker(n)` containing L.
These flag extensions prove endpoint incidence only. They do not join the
opposite endpoints or prove information can be gathered along the flags.

The checker verifies the lemma's hypotheses and explicit covers at all 104
arrival and 104 departure endpoints. It reconstructs residual sets from the
original 4,058-event word, ordered root Gram matrix and chronological data
paths. A second finite algorithm enumerates all pairs of restricted proper
hyperplanes without using q or the complement formula. It confirms the
one-plane optimum b and two-plane optimum d at every endpoint.

For zero, one and two unit helpers at an endpoint, the exact remaining number
of singleton cheap carriers is consequently d, d-b and zero. The marginals b
and d-b decrease. Sorting all 208 marginals gives PR2909's complete curve
`C_min(U)`, now with actual endpoint subspace unions attaining it.
No extra helpers improve an endpoint after two units. Every positive marginal
is at least twelve, so

```text
C_min(U) >= 12*(208-U)                  for 0 <= U <= 208.
```

## Cheapest two-history profile

Use PR2675's fixed template `m=73`, `W=832/9`, centre charge 56, total paid
rank mass 6712 and ideal idle rank 51. The whole original channel has profile

```text
1074 H1 + 58 H2 + 86 H3 + 104 H4 + 48 H5 + 24 H6 + 8 H7 + 8 H8.
```

Its rank mass is 2368. Every added lifetime consumes nine more rank units,
leaving `4344-9*(C+U)` idle rank units. Hence `C+U <= 482`. Idle packing is
fractional and favorable. Native ADDs, owners, routing, precision, tape and
all other physical charges are unknown and additional.

For `c_r(a)=(r/73)^(1-a)`, replace the nine units of ideal idle used by each
helper. Its excess prices are

```text
q_c = 2*c_1 + c_7 - 9*c_51/51
q_u = 9*c_1       - 9*c_51/51.
```

Both are positive for `a>0`, since their jumps have ranks below 51. Moreover

```text
q_c = 73^(a-1) * [2*(1-51^(-a)) + 7*(7^(-a)-51^(-a))]
q_u = 73^(a-1) *  9*(1-51^(-a)),
q_u < (9/2)*q_c < 12*q_c.
```

For U below 208, at least `12*(208-U)` cheap helpers are required. Their
excess over the 208-unit price is at least
`(208-U)*(12*q_c-q_u) > 0`. For U above 208, the extra units have positive
price. At U=208 any cheap helper also costs extra. Thus `(C,U)=(0,208)` is
the unique minimizing multiplicity pair for every positive a in this model.
Geometric assignments are not unique. At a=0 all equal-mass profiles tie.

The minimizing profile has `H1=2946` and the other original counts unchanged,
local rank mass 4240 and idle rank mass 2472, giving ideal `H51=824/17`.
Each unit flag has relaxed capacity 64 at all seven internal cuts, so 208
units also pass the earlier aggregate crossing rows. This does not assign
their actual subspaces at those cuts.

The pinned exact rational interval evaluator checks the selected moment and
strict root signs stated above. Every rank is below 73 and every profile count
is nonnegative, so the moment strictly increases with a. The root is the
supremum for this two-type, separate-endpoint, ideal-idle relaxation. It is not
an admitted primitive exponent or kappa, nor an optimum over all 256 histories.
For example, `(1,1,5,1,1)` has the same endpoint-adjacent dimensions and cheaper
transport, but different internal cut capacities. It is outside this optimization.

## Reproduction and evidence

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-endpoint-geometric-budget
```

The marker is `PASS_P104_ENDPOINT_GEOMETRIC_BUDGET endpoints=208 units=208`.
`verify.py --emit` prints the complete recomputed receipt without changing files.
RESULT.json records endpoint curves, a digest of explicit cover witnesses,
the optimizing counts and exact rational moment intervals. The verifier
authenticates both inputs and the interval module before importing that module.
It runs no optimizer or predecessor executable.

Four behavioral groups cover a literal affine example, failure without the odd
section hypothesis, wrong endpoint containment, invalid frames/counts, a strict
competing price, duplicate JSON keys, optimized Git-free replay, source rejection
before import and typed receipt corruption. Pair enumeration independently
checks covers but shares reconstructed demand sets. Interval arithmetic is
inherited from Douglas Colkitt's ceiling module. A separate internal audit
checked all 208 covers through the pinned predecessor's implementation and
reproduced the root interval. Evidence is author-checked, without independent
human or formal-kernel review. Environment and commands are in TASK.json.

## Open next questions

Can the 208 unit lifetimes, or a named alternative involving other histories,
jointly acquire and deliver the demanded coefficients in chronological order?
First specify actual nested source/target flags and dependency paths at the
original cuts, then check coefficients and dirty restoration before native
lowering. Separate endpoint covers and aggregate crossing counts do not supply
that joint realization. A candidate also needs the entire consumer, ownership,
idle, routing and precision bill. The selected cold replay is unrun because
this contribution changes no selected construction or frozen input.

Family decision: finish this interface and cost audit and stop. The optimistic
screen passes. It admits no supplier and justifies no further construction
campaign with unknown costs set to zero.

## Attribution and engineering notes

Nick Petalas. Apache-2.0. Substantial AI assistance and internal review are
disclosed in TASK.json, without a claim of independent human review.
Credit Nick Petalas/PR2909/2896 for the demand curve and residual capacities,
Hiroki Kumazaki/PR2889/2353 for endpoint spans and the monotone contract,
Arham Tahir/PR2675/2682 for the coupled price model, ywz65/PR2614 for source
departure handling, Sagar Thakrar's mixer handoff, and Philippe Van Velzen's
relay construction and window bill. Retain Rohan Arun/PR1972, Chafik
Boukhalfa/PR1991, Adam Gall/PR1940, Josie Elliston/PR1071, Ali Romman/PR1125
and the geometry/native lineage. Inspected heads are in TASK.json.
No predecessor package is copied or changed.

Build the Lever shaped the executable cover and price certificate. Prove It
Works required original-input reconstruction, exhaustive pair checks and
rejecting controls. Unslop guided the prose. Finite bounds are 104 endpoints
per orientation, 512 points/functionals, at most 255 distinct restricted planes,
65,025 plane pairs per endpoint, 209 count states, 4,058 events and 23 feasible
minimal price profiles. New functions are below 60 lines.

Power of Ten rule 3 deviation: Python allocates managed objects during checking.
Fixed domains and 2 MB JSON bounds limit live collections; temporary exports
have scoped cleanup on every exit. A fixed-capacity implementation would be
needed for a resident checker. Rule 1/2 deviation in the unchanged interval
module: recursive logarithms and adaptive series preserve source binding.
Calls here use ranks at most 73, precision 256 and `a<=1/100`; the chain has
at most 73 frames and atanh/Taylor tails terminate within 100/100 terms in this
domain. Registered commands have time bounds. A bounded iterative port needs
a separate source-bound equivalence audit. Rule 8/9 deviation: importlib loads
exactly one authenticated interval module; Python dispatch and unittest remain.
The source-before-import control checks that boundary. Warning-as-error
compilation, lint and optimized replay are recorded in TASK.json. Repository-wide
tooling and inherited mathematical assumptions are unchanged.
