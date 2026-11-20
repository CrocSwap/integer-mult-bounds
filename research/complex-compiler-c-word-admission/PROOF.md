# The selected complex compiler is admitted by the rational C-word grammar

## 1. Exact question and conditional conclusion

Fix canonical main `e54523517d0f03e58352e647c403a5af3e525a57`.
The source is Ali Romman's [#7828](https://github.com/CrocSwap/integer-mult-bounds/pull/7828)
at `03b572b3b9ab72c6ba67762e85e1630cda1daad5`, specifically the **selected
complex** application of `research/single-grade-rank-compiler`. The receiver
is his [#7834](https://github.com/CrocSwap/integer-mult-bounds/pull/7834) at
`4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02`, specifically
`research/fine-prime-gaussian-product/finite_c_word.py` and its complete-row
execution contract. All cited bytes are retained and authenticated here.

Let the receiver's scalar alphabet be extended by the fixed instruction

`SCALE(a,b,q): z -> (a+i b) z/q`, with integers `a,b` and positive integer `q`.

The rational-scalar lemma supplied in `SCALAR-PREMISE.json` provides its exact
all-column test and numerical realization under the named row, placement,
disjoint-XOR, scalar-scan and parking contracts. This package proves the
missing **finite grammar admission**, not those physical contracts.

**Theorem.** Retain the selected raw complex word's exact arbitrary-input,
all-column endpoint/normal-form and owned-erasure premises, and #7828's
finite construction and funding theorem for that input. Its compiled word
has an effective translation into the receiver's extended alphabet with:

1. the same dimension `N`, productive width `W`, and paid rank-one count `P`;
2. independent complete productive owners and only additional zero-initialized
   private owners, with an explicit charged final CLEAR on each private owner;
3. exactly `C^(tensor Nf)` on each productive field for **every** integer
   `f>=1`, and zero on each private field, with all exterior coordinates intact;
4. only `x,s,cz,cx,unit` for monomial adapters, exterior fixed Gaussian-rational
   scalar coefficients, and positive `paid` C instructions;
5. the receiver's strict test `P^500 < W^500 N^499`.

Every emission and owner label is fixed before external multiplicity `f` or
the eventual multiplication input varies. No astronomical selected word is
materialized here. The exact paid histogram is inherited from the source
construction; the new translation introduces no paid call and drops none.
This theorem does not discharge `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, or `analytic_recovery` in their full selected
contracts, and does not assert a complete-runtime or kappa theorem.

## 2. Source map: what is used, and what is not inferred

The following are the actual source seams, not an arbitrary Clifford-closure
claim. `inputs/` contains unchanged copies at the heads above.

| Source | Exact role in the argument |
|---|---|
| #7828 `APPLICATION.md`, complex producer section | Keeps every scalar contact, MOVE, QUERY, LAMBDA, signed translation and odd conversion in order; scalar ADD coefficients stay exterior; paid/helper factors are independently two-sided |
| Selected #7000 `PROOF-REVIEW.md`, sections 1–2 | Binds 117,612 paid positions and 23,392 productive fields on ambient 153; supplies exact selected signed phases, current frames, arbitrary-input endpoints and distinct-owner chronology under retained premises |
| Selected #7000 admission review and `data/caller.json` | Supplies the actual global LAMBDA formula and the complete compact caller's ADD, SWAP, LAMBDA, SCALE, IDLE_ONE, QUERY and native-call instruction families |
| `general-clifford-frames.tex`, exact representatives | A nested frame quotient has two rank-zero monomial factors around positive coordinate C; inverse orientations retain Pauli/phase corrections |
| `final4610-independent-admission/SPECIALIZATION.md`, sections 2–3 | Gives the constructive binary-affine/quadratic-phase monomial grammar and its exact `a*f` absolute phase; its old #4610 census is not substituted for the selected #7000 census |
| #7828 `product.py:compose` | Suspends distinct outer instances; moves their entire paid owners, services one whole inner word, reverses the additional placements, then resumes |
| #7828 `product.py:specialize` | Gives discarded targets fresh zero owners, retains every paid product position, splits its canonical axes into positive pieces, retires discarded outputs |
| #7828 `schedule.py:expand` | Uses complete permutations, chronological independent batches, positive leaves and sequential root tiles on the same full fields |
| #7834 `Matrix.left` and `Word.all_columns` | Supplies exact Gaussian-dyadic matrix keys with absolute phase; exterior coefficients are separate from matrix tensor powers |
| #7834 `c_dispatch.py:run_word` | Separates scalar `i` from columnwise `unit`, maintains complete independent rows and parks nonchild owners; its physical services remain inherited |

The selected source has 18 native calls, 400 mains per native call, 1,080
independent helpers per call, 51 conservatively reserved native labels,
416 queries, 3,616 whole idles and 14,480 global LAMBDA uses. These are
source-bound facts from the selected admission, not newly recomputed here.
Its LAMBDA already has a finite ordinary-translation/scalar lowering without
a child; each scalar term is translated by the rules in section 4. QUERY
uses its own copy/add/clear bank and one signed positive child.
The global auxiliary Gamma expressions are proof devices, not extra Fourier
operations. None is silently inserted by this translation.

The actual selected normal-form/phase correctness is retained as a premise.
This package proves how **each member of that expressly stated class** lowers
and how the two exact compiler files preserve the class. It does not infer
all-column correctness from a one-column matrix identity or a profile count.

## 3. Exact monomial lowering, including signed phase

Write a source monomial on `n` binary coordinates as

`|x> -> i^(a + sum alpha_i x_i + 2 sum_(i<j) Q_ij x_i x_j) |A x xor b>`,

where `A` is invertible over F2, `b` is binary, `a,alpha_i` are modulo four,
and off-diagonal `Q_ij` are binary. A source Q diagonal is already included
in `alpha`; it is not counted again. The exact representative includes `a`.

Emit `s_i` `alpha_i` times and `cz_(i,j)` for each nonzero off-diagonal entry.
Then Gaussian-eliminate `A` by row additions and swaps. A row addition is
`cx_(source,target)`. A swap is the three row additions
`cx_(a,b), cx_(b,a), cx_(a,b)`. Reverse the complete elimination sequence
to implement `A`, then emit `x_i` for the nonzero bits of `b`, then `unit`
`a` times. Thus the phase is evaluated on the original input coordinate,
before the permutation and translation. This is exactly the source order.

There are at most `n(n-1)` elimination additions, `3n` swap additions,
`3n` S gates, `n(n-1)/2` CZ gates, `n` translations and three units. The
selected conservative bound `4(n+1)^2` therefore applies. `Monomial.gates`
implements this construction and rejects singular matrices and malformed
phase records. The construction needs no paid C.

At the compiler's fixed internal multiplicity `c`, repeat each coordinate
gate on pairs `(i*c+j,k*c+j)`, `0<=j<c`. Emit **c** copies of every constant
unit. Now lift the entire compiled word by the receiver's external `f`:
base coordinate `u` becomes the `f` coordinates `(u,ell)`. The composite
coordinate order is `(i,j,ell)` and the action is the source monomial at
multiplicity `c*f`, with exact exponent

`a*c*f + sum_(j,ell) q(x_(j,ell)) mod 4`.

Consequently constant phase is columnwise `unit`, never the scalar `i`.
For example scalar i is i at both `f=1,2`, whereas one `unit` is i and -1.
Repeating the whole scalar program c or f times would be a different action.
The implementation keeps those levels separate.

The same construction applies to every whole-coordinate matcher introduced
by the compiler, now with `n<=N`. It is a finite list after N is chosen.
An adapter originally on `n*c<=N` coordinates has at most
`4c(n+1)^2 <= 4(N+1)^2` records; it is unnecessary to treat one large
permutation as a unit operation.

For a recorded signed job `K=L C_r R`, emit R first, its **one** positive
rank-r job, and L afterwards. L and R are independent records. An endpoint
normalization, when required, surrounds the entire completed job by
`R^-1` before and `L^-1` after; it does not normalize the helper at an internal
scalar contact. As a concrete signed example,

`C^-1 = (-i) Z C Z = X C`.

After lifting, `(-i)` in this one-column monomial factor becomes `(-i)^f`.
Substituting an inverse-pair wrapper `Z C Z` loses this absolute phase.
The positive C count is one in either correct representation.

## 4. Exterior scalars, aliases and private fields

Every fixed source rational and every selected odd conversion is a scalar
operation on the complete field. Translate it once to SCALE with a common
positive denominator for real and imaginary parts. Its coefficient remains
`lambda`, not `lambda^f` and not `lambda^c`. No source scalar is absorbed into
a matrix key or reclassified as an address monomial.

Ordinary ADD/SUB are the receiver's ADD/SUB. For the general update
`u <- u+lambda*v`, a constructive translation that also permits `u=v` is:

1. give this occurrence a fresh private row t and explicitly CLEAR it;
2. COPY v to t by CLEAR t; ADD(t,v);
3. SCALE t by lambda; ADD(u,t); CLEAR t.

The source v is preserved. The alias case uses its old value because the
copy precedes the update. These are six instructions before the final
whole-word retirement below. Overwrite COPY to a distinct destination is
CLEAR followed by ADD; COPY of a field to itself is the identity. Such
clear/copy sequences are used only where the source permits destruction
of the destination. This is an algebraic lowering under owned erasure,
not a claim of reversible destruction or free physical allocation.

A source SWAP exchanges two complete row values, not their physical owner
identities. Use one fresh private t, COPY u to t, COPY v to u, COPY t to v,
then CLEAR t. With the initial clear this is eight instructions. SWAP of
one owner with itself is the identity. There is no free host-level relabel
substituted for a requested payload exchange.

The actual selected global normalizer is especially relevant:

`Lambda_(s,c*f) = ((1+s*i)/2) I + ((1-s*i)/2) X_(q,...,q)`.

Here s is +1 or -1 and the complete translation repeats q over **all** c*f
columns. Make one whole-row copy, translate that copy, scale the original
and copy by the two displayed exterior coefficients, add, and clear. There
is no paid C. This is not the tensor power of a unary Lambda: that mutation
would multiply the scalar program across columns and create extra terms.
The source review explicitly requires the global form. The verifier checks
both signs, internal multiplicities one/two and external lifts through three.

QUERY similarly keeps its source lowering: one fresh complete copy, the
actual signed R/positive-child/L job on that copy, addition to the destination,
and clear. Its request remains paid even if the copied value is zero.
IDLE_ONE and the complete root/helper jobs retain their canonical positive
axis sets and source adapters. Their eventual rank-one leaves are emitted
by the compiler, not replaced by a free monomial.

Give every raw occurrence, suspended native center, discarded product target,
scalar temporary and compiler temporary its own lifetime-labelled private
row. There are finitely many, since the complete finite compiler has been
expanded. Assign numeric row labels once. All these private rows enter zero;
each source declaration/retirement gets an explicit CLEAR at the same point.
After the last instruction append CLEAR for **every** private label, even
if the source has already returned it to zero. These extra clears are
charged in the translated instruction count J. They create no productive
credit and no paid C call. This deliberately conservative policy avoids an
unproved free-list/alias reuse rule.

The original #7834 `all_columns()` checks productive rows only. That fact
does not prove private zero. The strengthened endpoint contract here checks
both public and private rows, and the appended CLEARs establish the latter
constructively. The verifier includes a word accepted by the original
productive-only test that leaves a private copy nonzero, then checks the
charged-clear repair. The receiver's physical initialization, copying,
parking and erasure of complete rows remain paid inherited services.

These private labels refer to the word's semantic row owners. Arbitrary
productive helpers are never relabelled as initialized private storage.
Internal dirty controls of a receiving movement primitive retain that
primitive's arbitrary-dirty restoration contract; they are not erased by
the word's final CLEAR list. Physical scratch outside the row program is
charged by its provider, separately from the finite row count Z.

## 5. Whole-job placements and chronological composition

For a request with ordered distinct axes S in the N-axis field,
`complete_order(S,N)` is S followed by every other coordinate, once.
`machine.move(owner,order,False)` maps old bit `order[j]` to new bit j.
The inverse uses the inverse complete permutation. Decompose both by the
monomial construction above. This retains all unmatched coordinates.

At external lift f, each base bit is replaced by its full f-coordinate
bundle. The placement permutes complete bundles. A rank-k positive request
becomes positive C on its k*f coordinates and identity on the others.
The caller's prior L/R factors stay outside the complete request; the new
placement is reversed after the request and before the parent resumes.
The source L/R factors themselves are not mistakenly inverted as a pair.

In `compose`, each outer instance has disjoint public inputs and private
banks. At a chronological paid position its yielded owner is an actual
whole field, even if it is a center containing correlated values. The code
requires these owners to be distinct. The inner word acts on those complete
fields; arbitrary-input linearity allows correlation without allowing alias.
Its endpoint returns the required canonical positive transforms. Undo the
additional placements, resume each outer instance, and continue in the exact
paid order. Working ambients are completed with all spectators as in #7828.

In `specialize`, a discarded source target gets a fresh private zero field.
Its completed output is zero by the inherited independent endpoint identity;
its source instructions and paid positions are still emitted. A positive
request with ordered axes S is split into consecutive disjoint positive
subsets of S. Products of C on these subsets equal C on their union. The
complete source adapter stays around the union, never around an unrelated
new source value. No request is removed merely because its current input
happens to be zero.

In `expand`, all child ranks strictly decrease. Each chronological batch
contains distinct complete owners; its requested axes are placed first.
The source word acts on its required working window, the remaining requested
tail axes get one positive leaf each, and the complete placement is reversed.
The child endpoint is the desired positive transform on the original
requested subset and identity elsewhere. The source recurrence and its
divisibility invariant justify each batch. At the root, sequential tiles
partition all N axes and use the same W public fields. Their positive C
products are exactly `C^(tensor Nf)` on every public field.

This is induction over the actual finite instruction tree, not an appeal
to closure under unspecified adapters. Each induction step is one of the
two exact source files' operations. Scalar contacts may temporarily affect
the full field; the complete endpoint fixes every unrequested coordinate.
Any exterior coordinate outside the N*f working axes is untouched by all
coordinate gates and participates only pointwise in row scalar operations,
so the same proof tensors with its full identity. No field slice is counted
as another independent productive input.

## 6. Paid count, finite bill and the receiver's funding test

Let the source expanded word have P rank-one leaves. Each emits exactly one
`paid` instruction. Monomial gates, placements, scalar staging, zeroing and
final retirement emit none. Thus `P_new=P`, including leaves on private or
known-zero fields. Product/splitting determine P before this lowering; no
raw rank-r request is accidentally counted as one final rank-one request.

Let R be its count of monomial/placement records after the source's own
normalization, A its general scalar-accumulation count, S its row-SWAP count,
B its other scalar,
copy, initialization and retirement records, and Z the resulting private
row count including the fresh staging rows. A convenient conservative bill is

`J_new <= P + 4(N+1)^2 R + 6A + 8S + 2B + Z`.

B's factor two covers COPY and overcounts single scalar/clear records.
These counts expand the source's QUERY/LAMBDA macros into the explicit
local rules above; no macro is treated as a unit free instruction.
Z charges the last clear of every private row. Declarations represented by
the six-instruction accumulation macro are counted there, not again in B.
All constants are finite computable integers after the fixed source N is
chosen. The selected physical tariff still charges complete volumes, all
placement gates, descriptor work, scratch retirement and historical backing.
This grammar count does not price an entire field as one bit or supply
the receiver's disjoint-XOR implementation. No precision or runtime exponent
is asserted from J alone.

The exact #7828 selected certificate records

`uniform_saving = 181502908503/50000000000000`

and supplies `P/W < N^(1-uniform_saving)`, with `N=2^H` and
`H=817416431103305304760123392`. Its selected type has multiple positive
counts and the construction has positive depth, so W>=2; N>=2 is immediate.
The scalar translation does not alter either number. The rational gap is

`uniform_saving - 1/500 = 81502908503/50000000000000 > 0`.

Therefore `P/W < N^(499/500)`, and raising to the 500th power gives exactly
the receiver's integer funding inequality. This comparison uses the selected
complex profile only. The pending profile, binary compiler, outer supplier
and complete multiplication saving play no part.

Subject to the rational-scalar lemma, the translated word is a finite code
of the receiver's extended enumeration grammar. It will eventually be among
that enumeration's candidates. This is an existence/admission corollary;
no feasible startup threshold, materialized selected word or fast binary
supplier is supplied here.

## 7. Verification and remaining boundary

The checker also censuses all 3,095 compact selected caller events: 2,108 ADD,
455 SWAP, 226 LAMBDA, 180 SCALE, 100 IDLE_ONE, eight QUERY and 18 native calls.
These are compact event counts before binding the caller's several port types;
they are not substituted for the expanded physical counts in section 2.

The checker imports the exact source `product.py` and `schedule.py` and the
exact receiver matrix/grammar module. It constructs a small native fixture
with rational mixing, independent two-sided phase wrappers, positive paid
ranks, fresh private storage and nontrivial whole-field placements. It runs
the source product, specialization and uniform expansion unchanged. The
result has two public fields on four axes and 18 paid calls, agreeing with
the source leaf recurrence. A matrix-key/exterior-coefficient calculation
checks its all-column endpoint. An independent dense Gaussian-rational
interpreter checks complete fields at lifts one and two against direct
tensor C, including all private endpoint values.

The monomial tests exhaust every invertible binary matrix through dimension
three, with affine and quadratic phase fixtures, all basis addresses and
internal/external multiplicities one and two. Controls distinguish scalar
i from columnwise unit, missing multiplicity in absolute phase, incorrect
two-sided inverses, incomplete spectator restoration, aliasing input owners,
alias-safe exterior scalar staging, omitted paid sites, dirty private exits
and a zero scalar denominator. Finite tests corroborate the universal
translation proof; they are not a reconstruction of the selected raw native
catalogue, a materialization of its enormous compiled word or a literal
tape machine.

The remaining independent obligations are the inherited raw all-column
normal-form/endpoints and owner semantics; #7828's selected funding/construction
proof; the rational-scalar lemma's numerical/physical contracts; and #7834's
complete-row placement, disjoint-XOR, parking and physical runtime theorem.
All five selected assumptions remain. Model-assisted review is distinct
from independent human review and proof-kernel verification.
