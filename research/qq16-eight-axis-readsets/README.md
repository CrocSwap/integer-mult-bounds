# QQ16 read sets for every local-axis hidden family

**Scoped exact result; no new supplier or kappa.** Eliminating all eight
QQ16 common-local-axis hidden-input families requires **88 ordinary port
reads**. The criterion is exact: a fixed read set works for these families
if and only if the unread columns of the actual centre matrix are linearly
independent. Leaving the eight ports `[1,2,3,4,5,6,8,12]` unread attains 88.
This is family-only recovery, not a complete controller.

This takes [PR2384's open question](https://github.com/CrocSwap/integer-mult-bounds/pull/2384)
at `b9ef408b1cb0fcd34ab1f1bdbe645573d5de188f`. PR2354 proved the first-axis
66-port threshold; PR2389 classified its 45 optimal sets, and PR2419
independently checked that classification. Their observation that every one
of those sets misses the second-axis witness is already covered. The new
result is the simultaneous-axis criterion and its sharp thresholds.

| Initial local axes allowed | Common-refinement classes | Total class nullity | Minimum port reads |
|---|---:|---:|---:|
| First one (credited predecessor) | 47 | 22 | 66 |
| First two | 68 | 12 | **76** |
| First three | 82 | 4 | **84** |
| First four | 91 | 0 | **88** |
| First five through all eight | 96 | 0 | **88** |

The proof covers every read set; it is not an enumeration of selected sets.
All attaining sets and exact class ranks are recorded in [RESULT.json](RESULT.json).
The exact oracle decoders recover the selected defect from mixtures of the
permitted axes, not only from one axis at a time.

## Contract and hidden input

Keep the retained QQ16 `F0/B_1_2` pair, A/T/U partition, 19-event ordinary
schedule, and selected/completed-X/forward-history observation boundary.
U contains 96 ordinary ports. Write `r_p` for column p of the actual
8-by-112 rational matrix R and `b_(p,j)` for local chart axis j, `0<=j<8`.
All payload fields below are constant in the tensor coordinates. The actual
registered owner routes obey

```
rho_s(p) b_(p,j) = e_(9+8(s-1)+j),          s=1,...,8.
```

Let G be the retained finite regular owner group and put
`f_b(d)=bit_0(d b)` as a rational number. For k initial axes, choose arbitrary
independent coefficient vectors `c_j in ker(R_U)`, and define

```
h_p(d) = sum_(j<k) c_(p,j) f_(b_(p,j))(d),
H(d) = B0 h(d).
```

The route identities give `B_s h=0` for every positive stage s and every
owner: each axis contributes `(R_U c_j) f_(e_(9+8(s-1)+j))=0`.
Initialize pair 0 with

```
X_U=h, Y_U=0, X_A=-P_(0,A) H, Y_A=+P_(0,A) H, X_T=Y_T=0.
```

Every other field is zero as a **difference** from an arbitrary fixed dirty
baseline. Since `R_A R_A^T=4I`, the selected section is injective. Thus H
nonzero means an original selected A-input defect.

The credited ordered QQ16 formulas give `X_U=Y_U=h`, all selected fields zero,
after F0; after B1 only `Y_(0,U)=h` remains. The ordinary tail leaves zero
selected fields, completed-X descendants after B1 and all five forward
histories. The terminal places h in the excluded former-Y output type.
The entire ordinary X output immediately after F0 is not an additional
free observation. The package reuses PR2384's exact logical maps and adapts
its full replay only to evaluate at a certified owner instead of identity.
This reuse is explicit; it is not an independent native-word implementation.

A fixed read set S grants side-effect-free reads of the **complete owner
arrays** at those ordinary ports, with arbitrary free retention and owner
mixing. Reads may happen before or after F0. The ordinary schedule stays
unchanged; homogeneous selected controls starting after complete F0 do
nothing to a zero selected/read difference. No earlier selected input
record, dense ordinary query, source preprocessing, changed local map or
extra former-Y endpoint observation is granted.

## Actual-owner function separation

Formal names for bit functions do not imply their independence on G.
[CERTIFICATE.json](CERTIFICATE.json) supplies 512 words, each of length at
most four, in actual registered stage-1 owner maps. Their first rows have
every possible first-nine-coordinate pattern x. Each generator is an
orthogonal involution; multiplying its transpose updates that row. No
unregistered orthogonal matrix is assumed to belong to G.

There are 88 distinct local-axis vectors among the ordinary ports. At the
certified owners their evaluation is exactly `f_b(x)=parity(x & b)`.
The integer identity

```
sum_(x in F2^9) (-1)^(x.b) f_c(x) = -256 delta_(b,c),     b,c != 0
```

gives an explicit left inverse. Every one of its 7,744 pairs is checked.
Consequently these 88 functions are independent as functions on the actual
owner group. Within each port its eight distinct axes are independent too,
so a zero port-array read is exactly the condition `c_(p,j)=0` for every j.
These are eight parameters per port in the largest family; no scalar-query
rank heuristic is used to infer the port count.

## Read-set theorem

Fix the unread set J. For each permitted axis j, partition J by the value
of `b_(p,j)`. Let C range over their **common refinement**: ports belong to
the same C exactly when their first k chart axes agree. Put `K=ker(R_J)`.

The read set eliminates every permitted hidden defect if and only if
`H_j(K)=0` for every j. Function separation makes this equivalent to

```
R_J D_(j,b) K = 0
```

for every axis group, where D is the diagonal coordinate projection onto
that group. Thus K is invariant under all these projections. Products of
the commuting projections are the projections D_C onto refinement classes,
so K is invariant under each D_C. Equivalently,

```
K = direct_sum_C ker(R_(J intersect C)),
rank(R_J) = sum_C rank(R_(J intersect C)).                  (1)
```

The converse follows from (1): every class contribution to `R_J c=0`
vanishes separately, hence every axis-group contribution and every H_j
vanishes. This proves the exact read-set criterion for each prefix k.

For all eight axes the source tuples are pairwise distinct, making every
class a singleton with a nonzero R column. Equation (1) is then precisely
`rank(R_J)=|J|`: the unread columns must be independent. Since R has rank
eight, at most eight ports can be left unread. Any eight-column basis attains
that number. The first four axes already suffice because every one of their
refinement classes has independent source columns.

For the smaller prefixes, nullity is monotone under deleting columns. Any
safe J therefore satisfies

```
|J| = rank(R_J) + sum_C nullity(R_(J intersect C))
    <= 8 + sum_C nullity(R_C).                            (2)
```

For k=1,2,3 there is exactly one dependent full class: respectively 30 ports
of rank8, 18 of rank6, and 9 of rank5. All other classes have independent
columns. Include that whole class, then extend its column span to rank eight
with independent outside columns. This attains (2) with 30,20,12 unread
ports, proving the sharp 66,76,84 read thresholds. There is no optimization
assumption or floating-point rank test in this argument.

The proof is constructive. Given dependent unread columns, choose a nonzero
kernel vector and one nonzero port. Repeatedly project onto its successive
axis groups. If every projected vector stayed in the kernel, the final
singleton would give a zero nonzero-column multiple, a contradiction. At
the first failure, the preceding kernel vector and that axis give a hidden
input with nonzero H, detected at a certified actual owner.

For an attaining read set, recover each observed axis coefficient using the
integer left inverse above. Complete each `R_U c_j=0` using a basis of the
unread columns, setting its other unread coefficients to zero. This may
choose different coefficients inside a redundant class, but (1) proves
that H is unchanged. The exact mixed-input checks exercise that distinction:
66/76/84 reads recover H without recovering all coefficients; the 88-read
basis complement recovers all coefficients.

## Adaptive oracle corollary

PR2389's credited transcript-fiber argument applies to the linear space
`(ker R_U)^k`, with one complete ordinary array as each query. Any exact,
always-terminating deterministic side-effect-free reader has a terminal
read set satisfying (1) on **every input**. Otherwise a kernel difference
has the same answers along that adaptive path but a different H. Arbitrary
nonlinear computation and stopping decisions cannot distinguish the pair.
The thresholds in the table are therefore sharp for this oracle too.

As in PR2389, input-independent random seeds and almost-sure exactness and
termination for each rational input give the same conclusion almost surely:
intersect the full-measure events over the countable rational input space.
This is not a bounded-error result or a result about arbitrary interventions
inside native words. The new step is the source-bound simultaneous-axis
criterion; the adaptive and countability arguments are credited reuse.

## Evidence and reproduction

From the repository root, standard-library CPython3.12:

```sh
python3.12 -B scripts/research_package.py --package research/qq16-eight-axis-readsets
```

This executes the primary replay, a separate certificate checker importing
neither the primary nor predecessor code, and five entry-point control groups.
The certificate was found by deterministic breadth-first search over the 112
stage-1 generators, stopping at full prefix coverage at depth4 after 51,271
visited row vectors. `make_certificate.py --out NEW_PATH` reproduces its exact
bytes; verification trusts only the checked certificate, not the search.
Default replay is read-only. `verify.py --emit-result NEW_PATH` intentionally
creates a fresh receipt and refuses an existing destination.

The primary replay authenticates all six live inputs and retained predecessor
files, binds 1,008 actual routes, checks all 7,168 positive-stage axis identities,
and verifies the owner certificate and exact class ranks. It constructs 88
87-read boundary witnesses by adjoining each outside port to one fixed
unread basis. These are examples, not the quantified proof. It also checks
three deeper-axis witnesses, the predecessor's 66-port set, and five exact
mixed-input decoders. There are 92 executions of the full 19-event logical schedule; the specified
66-port set is also the first prefix-boundary case. The independent checker reconstructs the routes, uses direct row
multiplication and rational column-span elimination, and checks every witness
relation and nonzero selected defect. It does not replay the logical maps.

Nine semantic controls/boundaries cover an incorrect owner word, missing
owner pattern, omitted bit function, a genuinely independent unread basis,
an additional detecting port read, wrong A cancellation, omitted bridge,
omitted owner action, and the credited nontrivial first-axis kernel. Five
entry-point groups reject source/receipt corruption, a wrong owner word even
after rebinding its hash, malformed JSON and overwriting existing evidence.

No native child kernels, full selected cold replay or proof assistant are
run. The ordered QQ16 contract is inherited; all-size physical reads,
retention, restoration, hosting, precision and the full supplier bill remain
outside this package. Fewer than the stated reads fail even when their
implementation and retention are free, so this route stops at the information
screen. At 88 reads only these hidden families are removed. A dense B0 query
is a different observation and detects them without an 88-port interface.
No native rank-unit tariff or dimension-per-owner bound follows.

Exact sources, foreign files and substantial AI assistance are recorded in
[SOURCES.json](SOURCES.json), [PREDECESSOR.json](PREDECESSOR.json) and
[NOTICE.md](NOTICE.md). The selected result and frontier remain unchanged.

## Open next questions

- Does an 88-port basis-complement read set restore the full selected input?
  First test input families outside these common-axis mixtures against the
  complete fixed observation map. The present family-only decoder leaves
  that question open.
- Can a different dense record or a changed first pair retain the required
  information with a favorable complete cost? Begin with the current dense-read
  obstructions and specify exact observation timing and native access. Port
  counts here do not supply a physical cost bound for such a different contract.
