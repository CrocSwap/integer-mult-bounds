# The first E8 decoder rank drop does not improve the star-copy ratio

This is a **scoped structural negative result**, not a new supplier or κ.
At 56 deletions, the full E8 binary reader code can first lose dimension.
There are precisely 255 such deletion sets. They form two root-isometry
orbits, with exact optimal star costs **50** (120 sets) and **57** (135 sets)
on 64 live ports. In the former class, the required live-target code has
dimension **seven**, even though the available restricted code has dimension
eight. Conflating these two codes overstates the necessary decoder dimension.
The exact cost calculation below allows totals outside the required code.

All remaining 56-deletion sets retain nine dimensions and have star cost
at least 44. Thus every 56-deletion set has cost/live-port ratio strictly
above `63/111`. Together with the pinned PR939 theorem, this extends the
fixed-star ratio exclusion through **56 deletions**. It does not classify
arbitrary deeper punctures, or all 56-deletion sets' exact optimum costs.

## 1. Precisely which decoder and charge

Use the 120 real E8 root lines in doubled standard coordinates, norm squared
8. Choose the representative whose first nonzero coordinate is positive and
sort representatives lexicographically. Define over F2

```
B_st = (1 + L_s · L_t / 4) mod 2,
C = rowspace(B).
```

The Gram quotients are integers. For distinct lines the dot quotient is
`0, 1, -1`, while the diagonal is 2. Hence for a live set L,

```
(B_LL x)_t = x_t + sum_{s in L orthogonal to t} x_s.
```

The existing star decoder computes these totals and removes the orthogonal
corrections. This note grants those corrections free. For a deleted set P,
write `res_L` for coordinate restriction and distinguish

```
E = res_L(C),                    available label-star functionals,
D = rowspace(B_LL) <= E,         functionals needed by live targets.
```

A permitted star reader pattern is any `w in E`; its optimistic charge is

```
s(w) = dim_Q span { L_t : w_t = 1 }.
```

All input bits are independent, and charges add for all used stars.
The scalar payload of a star may be any linear combination of source bits;
its reader pattern specifies which targets add that payload. A collection
of patterns realizes this fixed decoder exactly when its F2 span contains
the column space of B_LL, which equals D because B_LL is symmetric.
Arbitrarily many reader patterns are permitted; they need not lie in D. Costs are nonnegative and the zero total costs zero. Consequently
a dependent collection can be replaced by a basis of its span without
increasing cost. Denote the minimum total charge by `C_star(P)`.

For fewer than 56 deletions, E=D has dimension nine, giving the predecessor's
minimum-basis model. At the first rank drop this equality must be checked,
not assumed. Explicitly, for a chosen pattern basis w_i, write each live
source column
`B_LL[:,s] = sum_i a_(i,s) w_i`, and give star i payload
`sum_s a_(i,s) x_s`. These column coordinates reconstruct every decoder
output. No assumption that the payload coefficient equals its reader
pattern is needed.

General fitting matrices with different orthogonal corrections,
non-label reader patterns outside E, pairing-rank rather than star-rank pricing,
nonlinear decoders and free nonorthogonal side information are outside this
model. No physical hosting or restoration schedule is constructed here.

## 2. Exhaustive reduction to 255 cases

The inherited reader code has dimension nine and weight enumerator

```
1 + 255 z^56 + 255 z^64 + z^120.
```

Both implementations reconstruct it from the roots and B, rather than
trusting a stored list. A nonzero codeword vanishes on L precisely when
its support is contained in P. At `|P|=56`, this is possible if and only if
P is **exactly the support of a weight-56 codeword**. There are 255 distinct
such supports, all enumerated. No arbitrary-subset sampling is used.

For distinct nonzero codewords a,b,

```
|supp(a) union supp(b)| = (wt(a)+wt(b)+wt(a+b))/2 >= 84.
```

Thus a 56-set cannot kill two independent words. In each of these 255 cases
the restriction kernel has dimension one and `dim E=8`. Every other
56-set has `dim E=9`.

In the latter case also `dim D=9`. To see this, a symmetric rank-nine matrix
B factors as `U K U^T`, where U has nine independent columns and K is
invertible. Rank nine of `res_L(C)` means `U_L` has full column rank.
Then `U_L K U_L^T` has rank nine: its left factor is injective and its
right factor is surjective. The same argument cannot be applied after
`U_L` loses rank. That is why the principal matrix is computed explicitly
at the boundary.

## 3. Exact two-class census and minimum costs

For each minimum-word support, the primary verifier enumerates E, computes
D directly from the live rows of B, and computes the rational physical
rank of **every** available total. It then checks a spanning basis against
the full rank filtration. The result is:

| Puncture sets | dim E | dim D | Nonzero rank histogram in E | Nonzero rank histogram in D | Optimum cost |
|---:|---:|---:|---|---|---:|
| 120 | 8 | 7 | 28 rank 6, 99 rank 7, 128 rank 8 | 63 rank 7, 64 rank 8 | 50 |
| 135 | 8 | 8 | 56 rank 7, 199 rank 8 | same as E | 57 |

Histograms alone would not prove a minimum. For a code V and integer cost
s, define `r_d = dim span {w in V : s(w)<=d}`. A minimum-weight basis has
`r_d-r_(d-1)` members of cost d, by the binary matroid greedy argument:
any independent cheap set extends to a basis, while no independent set
can take more than r_d elements from its cheap span. Equivalently the
minimum is `sum_(d=0)^7 (dim V-r_d)`. The checked filtrations are:

| Class and code | r_0,...,r_8 | Basis costs | Minimum |
|---|---|---|---:|
| 120-set class, E | 0,0,0,0,0,0,7,7,8 | 6,6,6,6,6,6,6,8 | 50 |
| 120-set class, D | 0,0,0,0,0,0,0,6,7 | 7,7,7,7,7,7,8 | 50 |
| 135-set class, E=D | 0,0,0,0,0,0,0,7,8 | 7,7,7,7,7,7,7,8 | 57 |

When `dim D=7`, any subspace of E containing D is either D or E. Therefore
**all** admissible collections, including ones containing totals outside D,
have cost at least the smaller of the two basis minima. Both minima are
50. Explicit seven-total and eight-total bases attain it. When E=D, the
basis minimum is already the optimum over every permitted collection.

The certificate records every deleted support, both bases and their
physical costs, both rank filtrations, and a digest of each complete rank
table. The primary checks all 255 tables directly. Eight literal E8 root
reflections partition these supports into orbits of sizes 120 and 135.
The differing principal ranks prevent the two orbits from merging under
any root isometry. The independent implementation reconstructs all 240
signed roots, computes exact Fraction ranks on two orbit representatives,
and transports all ranks through explicit root isometries to check every
one of the 255 tables and all basis witnesses. It imports no primary or
predecessor implementation.

The primary rank algorithm is also exact, although it uses modular arithmetic:
for k<=8, every k-by-k minor of these norm-sqrt(8) root rows has absolute
value at most `(sqrt(8))^k <= 4096` by Hadamard. The prime 65537 exceeds this
bound, so a minor vanishes modulo that prime exactly when it vanishes over
Q. The independent Fraction calculation avoids that implementation entirely.

This is a complete finite classification following an explicit reduction,
not a claim to have enumerated all `binom(120,56)` subsets, not a randomized
failed search, and not a proof-assistant formalization.

## 4. The rank-retained cases and the ratio comparison

For the other 56-sets, E=D still has dimension nine. Use PR939's
common-deletion support-union argument and root-flat capacities

```
M_d = (0,1,3,6,12,20,36,63,120), d=0,...,8.
```

Two distinct basis readers with surviving ranks a,b satisfy
`M_a+M_b >= 84-56 = 28`. Sort the nine ranks and call the smallest two
`a<=b`. They are positive and the cost is at least `a+8b`. The minimum
over integer `1<=a<=b<=8` with that capacity constraint is **44**, at
`(a,b)=(4,5)`. This is a relaxation, not a constructed cost-44 decoder.
The primary checks its 36 pairs; the independent checker instead examines
all 11,440 nondecreasing nine-rank profiles.

The primary rebuilds M from all 256 simple-root subsets. Its all-subspace
coverage is the inherited parabolic argument in the retained PR939 proof:
a generic normal to a root-spanned proper subspace moves to a closed Weyl
chamber, and the roots perpendicular to it are exactly a standard parabolic
subsystem. This argument, rather than a list of 256 flats alone, justifies
using M for arbitrary surviving reader spans.

The exact comparisons on 64 live ports are

```
111*44 - 63*64 = 852 > 0,       rank-retained relaxation;
111*50 - 63*64 = 1518 > 0,     first rank-drop orbit;
111*57 - 63*64 = 2295 > 0,     second rank-drop orbit.
```

Every 64-line live set still spans Q^8, because a rational rank-seven
root flat contains at most 63 lines. Therefore the reduced **binary**
decoder dimension does not shrink the physical eight-dimensional window
at this boundary. The ratios 50/64=25/32 and 57/64 both exceed 63/111.
Combining this with PR939's result through 55 gives the stated through-56
exclusion; the inherited nine-puncture example remains an attaining ratio
in that larger domain.

## 5. Optimistic budget, limits and attribution

Only a necessary copied-information charge is being screened. Grant all
helpers, source accesses, frame changes, restoration, additional copying,
recursive children and other overheads zero additional expense. The first
rank drop still gives no improvement to the star-copy ratio at the same
physical window. Adding nonnegative costs cannot turn that component into
a gain. This does **not** exclude a better complete supplier from savings
in other invoice terms at a worse copy ratio, or changes to the model.
No assembly improvement or new κ follows; at our exact base the selected
PR890 assembly is complex-limited and retains the PR589 bit supplier.

Scope ends at 56 deletions. Correlated demands, more general fitting
matrices, changed geometry, non-root ports, nonlinear codes, alternative
copy pricing, variable stage windows, and unimplemented physical circuits
remain outside the claim. All-size/compiler, common-label/mutable-source,
hosting, precision/tape and analytic-transfer obligations remain inherited.

Credit Chi Zhao's **PR631**, head
`fb893b5ee1317c2da3b297e6fe78eca0857d1a76`, for the exact code/flat model,
sharp single-reader thresholds, the initial puncture exclusion and geometric
coverage proof. Credit Ross Richardson's **PR939**, head
`3a8ec54d62fb8824c658dc7ed356f99423cac8cf`, for the joint-reader inequality,
flat capacities and through-55 theorem; and Philipp (@mightyOil)'s **PR875**
for the distinct 36-puncture equality analysis. This package does not claim
those predecessor results as new. Joel Pulikkan / GamingPuzzled's PR620,
DreamingOfClouds' PR595/602, eumemic's PR543 and their predecessors provide
the underlying star-accounting and E8 construction context.

The new result is the **first rank-loss classification**, the distinction
between available and required codes, its exact complete star cost including
outside-target totals, and the through-56 consequence. Exact source pins and
unmodified predecessor documents are in SOURCES.json and reference/.
Prepared by **Ross Richardson (@RossRichardson)** with substantial **OpenAI
Codex assistance** in mathematics, implementation, verification and writing.
Both implementations were produced in this session; code independence is
not independent human review. Apache-2.0. No claim of literature priority.
