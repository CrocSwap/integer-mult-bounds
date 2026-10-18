# A nonlinear terminal-information barrier at every rank-seven endpoint

For each of the two pinned PR2894 providers, a fresh eligible-input
quantity cannot be extracted at any endpoint of rank at most seven by
the monotone suffix interface defined below. The local suffix operations
may be nonlinear, and arbitrary recoding confined to the eligible entrance
coordinates is allowed. The obstruction follows from a finite complete
endpoint census and a written indistinguishability argument.

This is a result about the frozen provider word and its declared entrance,
observation, and frame contracts. It is not a word-independent rank-eight
lower bound, a new supplier, or a multiplication-bound improvement.

## Main theorem and exact interface

Let `D=Z[1/2]`, and let `W` be any `D`-module. Every formal warp in the
pinned provider is represented by an invertible `D`-linear endomorphism of
`W`. Every live non-target entrance value ranges independently over `W`.
The zero module is allowed, in which case statements about nonconstant
functions are vacuous.

The frozen middle operator `M` and the post-`restore` last frames are those
of the two providers authenticated by PR2918 at
`9360ba7312cf8961e672e9eb26c612719028d39d`. Its source pins are PR2908 at
`51309592971e3b5be935599eed2a95404dc7781e`, carrying the PR2894 providers at
`18d03c447886895ef9abf888398178e0428533ca`.

The entrance coordinates are taken immediately after the provider's 84-event
prelude, which `M` omits. Its only non-target operations are 24 invertible warps
on protected registers outside `H`. Hence these coordinates still range
independently over the full module, and the eligible coordinates are unchanged.
The allowed entrance recoding below is applied at this declared cut.

As in that package, the live non-target coordinate set is

```
L = {0,...,703} \ (removed union {112,...,223}),     |L|=520.
```

Let `P` contain all `helper_final` and `start_extra` registers and every
source of an initial operator correction. The eligible entrance set is

```
H = {r in L : r>=224 and r not in P},               |H|=226.
```

Write the eligible entrance state as `h in W^H`. An entrance recoding is
any map `S:W^H->W^H`, extended by the identity on all other coordinates.
In particular it cannot inspect, modify, or correlate the protected
entrance values. Allowing nonlinear or noninvertible `S` only enlarges the
class covered by the negative result. The rank-eight comparison below uses
an actual invertible scalar `S`.

The suffix starts after the fixed `restore` word and before the prescribed
final climbs. It has a fixed finite data-dependency network satisfying:

1. Each local operation acts at a common frame containing the current
   frames of all its data inputs. Its outputs have that frame or a larger
   frame. The local map may be arbitrarily nonlinear.
2. Frames only increase by subspace inclusion. There are no new warp
   resets or other operations carrying a dependency to a smaller or
   incomparable frame.
3. Inputs consist of the live non-target state at this cut, together with
   any constants or ancillas whose joint tuple is independent of the complete
   entrance tuple and can be fixed identically in compared executions. There
   are no target reads, additional source reads, earlier snapshots, or
   retained data-dependent side values.
4. The network, output identities and the frame assigned to every node are
   fixed independently of input values. Data-dependent local branching is
   allowed only inside a node's local function; every potential branch input
   and every data/control dependency is an explicit incoming edge obeying
   rule 1. Branch choice, output selection/presence, timing and frame choice
   provide no additional observation.

**Theorem.** Under these assumptions, no output at a final frame `E` with
`dim_GF(2) E<=7` can equal a nonconstant function of `h` for all entrance
values. The same conclusion holds for any tuple of outputs whose frames
are all contained in one common such `E`.

For a fresh eligible-input extraction using an allowed entrance recoding
and this suffix interface, endpoint rank eight is therefore necessary.
For every nonzero `W`, PR2908's calibrated rank-eight entrance/output pair
attains that threshold algebraically. For `W=0` no nonconstant quantity exists
at any rank, so there is no sharp recovery threshold. This comparison allows
the `H`-only entrance recoding; it
does not assert that a suffix alone, with identity entrance map, attains
the threshold.

## Finite certificate: every rank-seven readout is saturated by nuisances

Let `F_r` be the exact frame of register `r` after the frozen `restore`
word. The available terminal support at an endpoint `E` is

```
R(E) = {r in L : F_r is a subspace of E}.
```

The frame replay includes all recorded scalar incidents in `A`, `B` and
`restore`, including their target writes' source incidents, as well as prelude
warps and inserted `B` warps. The separate 176 target-only `cut` operations
have unspecified (`None`) frames in the provider. They are interpreted using
the inherited center-cut convention: every source is a recorded center whose
current frame already equals its `center_frames` entry at the end of `A`.
Both verification paths check this equality; neither reconstructs additional
physical frame moves for that separate cut. Warps
replace their incoming frame by the recorded outgoing frame. Taking the
union of all historical frames would give a different and incorrect
support. The middle operator omits target writes but retains all 4,583
non-target gates; omitting those target writes does not omit their source
frame incidents.

Every rank-seven subspace of `GF(2)^9` is the orthogonal complement of a
unique two-dimensional subspace for the standard nondegenerate dot
product. Such a plane has three nonzero elements `{a,b,a+b}`. Counting its
ordered bases gives

```
# {rank-seven endpoints} = (2^9-1)(2^9-2) / ((2^2-1)(2^2-2))
                         = 511*510/6
                         = 43,435.
```

Equivalently, choose the two least integer representatives of the three
nonzero plane elements. They satisfy `0<a<b<a xor b<512`, and every plane
occurs exactly once. A register belongs to the associated support exactly
when every vector in its last-frame basis has even dot product with both
`a` and `b`.

For **each provider separately**, these 43,435 endpoints produce exactly
239 distinct support sets. `certificates.json` records the complete
support-class partition, its multiplicities, a representative annihilator
plane, and a forbidden-input column set for every support. For every class
with support `R`, it supplies `J_R subset L\H` such that

```
|J_R|=|R|,
B_R = M[R,J_R] is a scalar matrix over D,
det B_R is one of 1,-1,1/2,-1/2,1/4,-1/4.
```

Being scalar here means that each complete free-operator polynomial entry
has only its empty-word coefficient; every nonempty-word coefficient
vanishes. The selected minor has size at most 16. The empty support has
the empty minor, whose determinant is one. Each provider has the following
unweighted class counts:

| Determinant | 1 | -1 | 1/2 | -1/2 | 1/4 | -1/4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Support classes | 157 | 34 | 11 | 17 | 8 | 12 |

These are finite source-bound matrix claims. `verify.py` reconstructs the
provider operator and last frames with the authenticated PR2918 engine,
regenerates the entire endpoint partition, and checks the minors and their
dyadic inverses. `verify_independent.py` is the separate verification entry
point; its execution status must be established by its own run. The
written proof below does not substitute for executing either verifier.

Since each determinant is a unit of `D`, the adjugate identity makes
`B_R` invertible over `D`. Hence it acts as an automorphism of `W^R` for
**every** dyadic module `W`. Since each minor is already scalar as a
formal-operator identity, this conclusion survives every specialization of
the warps. It does not rely on distinct free words staying linearly
independent after specialization, on `W` being free, or on finite dimension.

For comparison, PR2918's original endpoint

```
E7 = span_GF(2)(256,128,66,36,22,8,1)
```

has

```
R = (105,307,309,314,369,371,373,378,408,572,573),
J = (14,307,309,314,369,371,373,378,41,572,573),
M[R,J] = diag(-1/2,1,1,1,1,1,1,1,1/2,1,1).
```

The new finite obligation is complete endpoint coverage with the same
unit-minor property, rather than just this eleven-coordinate certificate.

## Indistinguishability, including nonlinear recoding and decoding

Fix any support `R` and its certified `J_R`. Split the entrance state
into `h` on `H`, `z` on `J_R`, and `k` on all remaining coordinates. After
the allowed entrance recoding, the complete observation on `R` has form

```
y = A S(h) + B_R z + C k,
```

where `A` and `C` may contain arbitrary specialized operator entries.
Fix `k` and any two eligible states `h,h'`. Starting with any `z`, put

```
z' = z + B_R^-1 A(S(h)-S(h')).
```

Then

```
A S(h)+B_R z+C k = A S(h')+B_R z'+C k.
```

The two states are both allowed: protected entrances range independently
over their entire module. Thus every eligible state can produce every
observation `y` by a suitable choice of these protected inputs. If any
decoder `g`, with no linearity assumption, recovered `f(h)` from `y` for
all inputs, this collision would give `f(h)=f(h')` for every pair. Hence
`f` would be constant.

This is a deterministic exact-recoverability statement for all allowed
inputs; it makes no probabilistic mutual-information claim.

This proves the information obstruction for each rank-seven endpoint.
Every endpoint of rank below seven extends to a rank-seven endpoint `E'`.
Since `R(E) subset R(E')`, the same conclusion holds on `R(E)`: any
decoder of the smaller observation would also be a decoder of the larger
one. The nuisance column set can depend on the endpoint; no common set of
columns for all endpoints is required.

## Causal proof for the complete suffix

Consider a dependency path from an initial suffix register `r` to an
output at frame `E`. By the common-frame rule, a frame on this path is
contained in the frame of the next operation. All subsequent frame moves
are inclusions. Therefore `F_r` is contained in `E`, so `r` belongs to
`R(E)`.

Induction through the finite network shows that the output is a function
only of the initial `R(E)` values and the permitted input-independent
constants or ancillas. Fix those ancillary values identically in the two
colliding executions constructed above. The complete suffix produces the
same output in both executions. It cannot recover a nonconstant eligible
function. Multiple outputs with frames contained in one common `E` obey
the identical argument. This proves the main theorem.

Arbitrarily many nonlinear gates or intermediate buffers do not change
this conclusion under the declared interface. A larger-frame computation
cannot feed a smaller-frame output without violating monotonicity. Known
local frame-conversion maps can be included in the arbitrary local
functions; the proof uses their dependency and frame directions.

The theorem concerns **fresh eligible-input** quantities. Existing cold
outputs correspond to protected entrances outside `H` and are not ruled
out. Nor is the joint information in freely pooled outputs at different,
incomparable rank-seven frames covered: separately masked shares can reveal
information jointly. A physical collector obeying the declared rules is
covered if its own final frame has rank at most seven. An external free
collector changes the observation contract.

## Rank-eight attainment in the allowed pre/post interface

The existing PR2908 construction has an invertible scalar entrance map
`S` supported on `H` and an output map `T` supported at

```
E52 = span_GF(2)(256,128,64,36,20,8,2,1),    dim E52=8.
```

Its 24 entrance gates and three output gates yield the paired identities
recorded and checked in PR2918. In particular, for the extracted helper,

```
v = S e408,
y = Mv = 2 e42,
alpha = e408^T+(1/2)e42^T+e105^T,
alpha M = e408^T S^-1,
alpha y = 1.
```

The terminal gates are

```
408 += (1/2)*42,
408 += 105,
42  -= 2*408.
```

Register42 is available at `E52`. These actual pre/post maps give the
rank-eight algebraic witness in the same eligible-entrance class. For nonzero
`W`, its recovered coordinate `h_408` is nonconstant. The
lower bound and this witness establish a sharp endpoint-rank threshold
for that interface; they do not re-prove the inherited native supplier,
buffers, target compensation, owner allocation, or complete cost ledger.
The construction and its costs remain credited to PR2908.

## Secondary consequences: retained information and repairs

The quantitative rank statements below assume that the entire observation
map is linear in the same original coordinates used for the desired
quantity `Lh` and the additional linear observations. They do not inherit the main
theorem's allowance for arbitrary nonlinear entrance recoding: after such
recoding, a linear side observation can reveal more original coordinates
than these linear-map rank formulas permit.

**General quotient.** For module observations `y=Ah+Bz`, let
`pi:Y->Y/im B`. An arbitrary function of `h` is recoverable exactly when
it is constant on each coset of `ker(pi A)`. Indeed, two eligible states
admit a common observation exactly when their difference maps under `A`
into `im B`; conversely `pi y=pi A h` supplies the quotient. In finite
dimension over a field, the dimension of the recoverable linear quotient
is `rank([A B])-rank(B)`. The unit-minor case has zero quotient.

**Additional linear observations.** In a finite-dimensional vector-space
specialization, let the original readout be `R0 x` and the desired linear
answer be `D0 x`. The exact minimum number of unrestricted additional
scalar linear observations is

```
rank(D0 restricted to ker R0) = rank([R0;D0])-rank(R0),
```

even if decoding is nonlinear. The extra observations must distinguish all
pairs in `ker R0` that `D0` distinguishes, proving the lower bound. A basis
of the desired row space modulo the original observation row space attains
it. Under complete masking, projection of `ker R0` onto `H` is surjective;
therefore recovering `D0 x=Lh` of rank `d` requires exactly `d` additional
scalar linear observations. For `W=F^n`, recovering `t` independent full
eligible arrays requires `tn` scalar linear coordinates, or `t` linear
side arrays of the same capacity.

This counts unrestricted linear information, not its acquisition,
chronological retention, restoration, or recursive cost. Arbitrary
nonlinear rational side encodings do not satisfy this dimension bound:
one rational can encode a finite tuple of rationals because both sets are
countable. Linearity or a separately specified capacity restriction is
essential for the observation count; arbitrary nonlinear decoding is
already covered.

**Low-rank repair.** Over a field, suppose the original nuisance block
`B` has full row rank `m` and a changed construction replaces it by
`B'=B+Delta`, where `rank Delta<=q`. Allow its eligible block to change
arbitrarily to `A'`. Then

```
rank([A' B'])-rank(B') <= m-rank(B') <= q.
```

At most `q` independent eligible linear directions become observable on
the same output space. Extra independent nuisance columns can only reduce
this capacity. Exposing `d` independent directions therefore requires a
nuisance-block perturbation of rank at least `d`. This is necessary, not
sufficient: `A'=0` exposes no eligible information even when `B'=0`.
No vector-space rank assertion is made for a general dyadic module.

## Prior work, evidence type, and unresolved implications

The quotient and collision arguments are standard linear-algebraic
identifiability principles. No novelty claim is made for those principles.
PR2918 supplied the original endpoint obstruction and independent inverse
certificate. PR2908 supplied the positive rank-eight paired construction.
PR2979 already reports a complete 43,435-endpoint paired-extraction screen
on a newer PR2942/stage1 word and a rank-seven positive example on PR2917
V45. Those source words and contracts differ. In particular, the present
claim is not the first rank-seven endpoint enumeration and does not rule
out the changed-word positive example.

The scoped extension is the unit-nuisance saturation certificate for every
endpoint on the two pinned old providers, and its consequence for arbitrary
nonlinear local processing throughout a monotone causal suffix. The source
conventions and complete predecessor credits remain those in the package
documentation and PR2918.

The endpoint coverage and minors are a **finite exhaustive exact
computation**. The implications for all input values, all allowed recodings,
every dyadic-module representation, and every finite suffix satisfying the
rules are **all-parameter written proofs**. Neither is a formal-kernel proof.
An independent verifier run is separate evidence and must not be inferred
merely from the presence of its source file.

The result leaves open changed middle words, changed protected entrance
access, correlated or restricted input domains, additional snapshots or
source observations, untracked control dependencies, new warp resets,
nonmonotone frames, and different observation contracts. It supplies no
paid repair circuit, new native phase identity, full recursive moment,
global supplier optimum, or improved multiplication bound.
