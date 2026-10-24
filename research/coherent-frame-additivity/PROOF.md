# Scalar compatibility of coherent frame potentials

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.
These are written proofs with exact finite corroboration, not proof-assistant
theorems. No new κ or supplier admission is claimed.

## 1. The actual proposed boundary

Yiyang's PR4966 at `039b6ea51ab7a7efb38fc6851f345839683251b0` constructs
same-realization inverse recipes for both native orientations. Its final
paragraph proposes coherent frame potentials as a sufficient compatibility
target for a future caller: a paid transition a→b should realize
`A_b A_a^-1`, and a warp should realize `A_new W A_old^-1`. The proof also
explicitly warns that reversible rounded implementations can be nonlinear
and need not satisfy the controller's linear operator identities. This
contribution makes one part of that warning precise at the actual source.
The unchanged predecessor proof is vendored with its exact provenance.

Consider a **gatewise** proof using one common bijection A_f per frame f,
shared by every register currently in that frame. It must also account for
unchanged scalar instructions. On two independent fields of that frame an
ADD has the map

`G_c(x,y) = (x+c y,y)`.

Commuting the product coordinate change `A_f × A_f` through that same ADD
is equivalent to

`A_f(x+c y) = A_f(x)+c A_f(y)` for every x,y.                 (1)

Transition and warp equations alone do not state (1). This observation is
about the described proof recipe. Global endpoint agreement might instead
follow from a different identity, changed scalar instructions, or a bound
on the resulting errors; none is excluded here.

## 2. Exact local criterion

Let D be a module over the dyadic rationals Z[1/2], with no nonzero element
killed by a power of two. Let c be a nonzero dyadic **unit**, so c=±2^k
for an integer k. An arbitrary map A:D→D satisfies (1) if and only if it
is additive. Bijectivity is unnecessary for this equivalence.

For necessity put y=0 in (1). This gives c A(0)=0, so A(0)=0. Now put
x=0 to obtain `A(c y)=c A(y)`. For any z, choose y=c^-1 z. Equation (1)
then becomes `A(x+z)=A(x)+A(z)`. This proves additivity for every x,z.

Conversely, an additive map commutes with integer multiplication. In a
dyadic module, `2 A(z/2)=A(z)` and the half is unique, hence
`A(z/2)=A(z)/2`. Induction gives dyadic homogeneity and therefore (1).
Thus any one such unchanged ADD forces the full dyadic-linear condition.
The theorem also holds on real or complex vector spaces viewed as dyadic
modules. Additivity by itself does **not** assert continuity, real
linearity, or complex linearity. With continuity, the usual dyadic-density
argument gives real linearity; that is a separate additional hypothesis.

Coefficients such as 3/4 are allowed in the source, but the certificate
deliberately uses only unit dyadic coefficients. No division by three, no
finite-grid closure, and no rounding law is assumed in the argument.

## 3. Binding to every active source frame

The sole executed scientific input is Cao Yifan's round-three actual word,
`research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz`, at canonical base
`b91956876e5b4122fd89179f1b57557ff8378f15`. Its compressed SHA256 is
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`.
This is the same actual word used by PR4966. The parser is independently
written and imports no predecessor verifier, native oracle, or inverse recipe.

For **each** retained forward and backward orientation the exact replay finds:

| Object | Count |
|---|---:|
| Source events | 21,449 |
| Persistent L fields | 632 |
| Active frames | 1,002 |
| Frames with a distinct persistent L-to-L unit-dyadic ADD | 1,002 |
| Owned-center macros | 8 |
| Paid occurrences including centers | 3,298 |

Here active frames means frames occurring in the source's scalar, climb,
center, or warp records. Phase and adapter records are retained markers;
their physical action is not implemented by this audit. RESULT.json gives
the first qualifying ADD's exact event index, coefficient, register pair
and full record for **every frame in each orientation**. Witnesses occur
outside owned-center macros. Frame ids and dimensions are not conflated:
all used ids are checked, including the empty frame and the full frame.

The parser replays scalar/paid/warp frame chronology and both persistent
endpoint lists. It verifies the actual paid profile
`{1:2201,2:412,3:510,4:127,5:40,8:8}` and all eight center macros, including
the separation of unchanged capture sources from modified destinations.
It does not evaluate their physical Gaussian matrices.

Consequently a gatewise coherent-potential proof of this **unchanged**
word, with a shared all-input map per frame, must use additive potentials
on all 1,002 active frames in each orientation. There is no uncovered
transit-only frame where this recipe can hide a nonlinear potential.

The all-input requirement is a contract, not something inferred from a
finite fixture. It is also compatible with arbitrary persistent dirt:
conditional on bijective persistent paid children and warps, each ordinary
persistent ADD/SCALE prefix is bijective. Each completed owned macro is a
shear from its unchanged capture sources into disjoint destinations, even
for a deterministic nonlinear center. It too is a persistent bijection.
Every witness is outside those macros. Thus under those explicit premises
the two persistent fields at a witness can vary independently. This does
not promote a test of one restricted input trajectory into (1).

## 4. Exact distinctions from inverse and warp compatibility

### Reversible rounded maps

On Q² define `R(x,y)=(x+floor(y/2),y)`. Its exact inverse is
`R^-1(u,v)=(u-floor(v/2),v)`. It is a deterministic reversible rounded
shear and fixes zero. Yet at x=y=(0,1) and c=1,

`R(x+y)=(1,2)` while `R(x)+R(y)=(0,2)`.

Every local inverse round trip can pass while the unchanged ADD fails
equivariance. This example concerns a map that is itself proposed as a
potential; the theorem does not say that each internal rounded shear of
an otherwise additive complete realization is individually forbidden.

### Even compatibility with all unitaries is insufficient

On R^d or C^d define `P(v)=||v||² v`. It is a bijection: it maps each ray's
nonnegative radial parameter r to r³. The inverse is zero at zero and
`P^-1(w)=||w||^(-2/3) w` otherwise. For **every** unitary U,

`P(Uv)=U P(v)`.

Nevertheless at a unit vector e,
`P(e+e)=8e` and `P(e)+P(e)=2e`. Thus fixed unitary intertwining, zero
preservation, and exact two-sided inversion do not logically imply (1).
For an arbitrarily small positive t, the bijection
`P_t(v)=(1+t||v||²)v` gives the same distinction while being within t of
identity on the unit ball. Small error on a ball is not exact equivariance.

For example, given unitary ideal frame maps C_f and unitary ideal warp
maps `C_b W C_a^-1`, choose `A_f=P C_f`. All pure transition and warp
conjugations then equal their ideal unitary maps, because P commutes with
every unitary. Their equations do not detect this nonlinear common gauge.
The unchanged ADD does detect it. This is a counterexample to sufficiency
of those equations as a **gatewise gauge proof**, not a counterexample to
the endpoint of the ideal native word. That ideal word is unchanged in
this example and may already have the desired endpoint.

The verifier checks the rounded example, its two-sided inverses on 49 exact
rational points, the radial ADD discrepancy, and 147 exact rational
orthogonal-equivariance instances. The all-unitary statement follows from
norm preservation in the written proof, not from those 147 instances.
It also checks 12,005 rational ADD instances for an invertible linear map.

## 5. Separate closed-walk obligations of the paid graph

There is a second, independent distinction between inverse pairs and frame
potentials. Normalize paid transitions to maps H_e on a common field and
temporarily disregard warp edges. On any connected graph, specified
invertible H_e admit `H_e=A_b A_a^-1` if and only if every fundamental
closed-walk product is identity. Choose a root and a spanning tree. The
tree fixes each A_v from an arbitrary A_root. Every non-tree edge's equation
is exactly its fundamental closed-walk equation. This proves both directions
for arbitrary bijections, without commutativity or linearity. Reverse
traversal uses the actual inverse. Correct inverse pairs only check the
immediate edge/reverse walk and do not test other cycles.

The source graph in each orientation has 1,002 vertices, one component,
3,298 paid occurrences, and hence 2,297 non-tree occurrence tests. If
parallel occurrences are identified by unordered endpoint pair, its 2,855
simple edges instead have cycle rank 1,854. RESULT.json retains the full
deterministic forest/chord event partition; a separate BFS component count
cross-checks the union/find calculation. These are counts of **potential
tests**, not 2,297 proved failures or algebraically independent constraints
on a particular shared implementation. Warp constraints and scalar
compatibility remain additional conditions.

The graph lemma is elementary and not claimed as new mathematics. Nick
Petalas's `coherent-transvection-neighborhood` uses related spanning-tree
holonomy constraints for binary symplectic axes. Its object is a restricted
geometric chart move, whereas this census binds actual paid occurrences
and the nonlinear numerical-potential boundary of PR4966.

## 6. Constructive choices left open

An additive family satisfying all paid and warp equations would clear this
local scalar obstruction. It still needs Gaussian/frame compatibility,
fresh independent D factors, an actual paired caller, and a complete
precision/storage/routing/recursive bill. This audit constructs no such
family and does not prove one impossible.

Alternatively change each scalar gate to its literal conjugate under the
chosen nonlinear potentials, or prove and pay a quantitative error bound
for its failure to commute. Both change the present contract and require
a fresh caller and invoice. A global correlated-error construction may
also use an argument entirely outside this gatewise recipe. It is not
excluded by this theorem, the cycle census, or PR4966's independent-error
tariff. No selected frontier or multiplication theorem is changed.
