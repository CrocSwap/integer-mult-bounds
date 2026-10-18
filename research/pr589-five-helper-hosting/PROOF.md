# PR589: whole-call hosting in the exact stream model

This is a written, source-bound proof with executable finite certificates. It
is not a Lean kernel proof, an all-size compiler, or an unconditional integer
multiplication theorem. Its conclusion concerns the ideal address operations
defined below. The cost and implementation of those operations remain separate.

The source is the selected PR589 word at upstream head
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`, retained at base
`ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. Exact local input pins are in
`SOURCES.json`; reconstructed record and template hashes are in `RESULT.json`.

## Statement and domain

Let K be a field of characteristic other than 2. For a cover sweep take a finite
field and the full orthogonal group G of the form I_64/2, with every element
visited once, in any order. A physical stream is indexed by **(family, g)**,
where g is an element of G, and contains an arbitrary Boolean function on
X = K^64 × K^64. Different streams may have arbitrarily correlated contents.
They are different storage locations even when their family numbers agree.

Use the source's 288 stage/replica descriptors, each representing an entire
cover sweep, with the two literal local instruction lists. Interpret ADD as
XOR at the common native address, MOVE and fresh COPY by the frame-relative
partial swaps, and ERASE only with its transported-source equality guard.
One reserved private family starts blank at every cover class; each invocation
uses its stream at class d and leaves it blank for subsequent reuse. This does
not reduce the source's existing nine-family private reserve.

There is an explicit orthogonal realization of every hosted owner descriptor
such that:

1. Every complete local call has the source's data endpoint, independent of
   every dirty helper input; every helper has exactly its prescribed residual
   endpoint; the private stream ends blank; every other physical stream is
   untouched.
2. On **all retained data streams**, the chronological hosted schedule with
   its remainder children equals the unhosted schedule with full idle children.
   Auxiliary bank outputs in the unhosted comparison are allowed to evolve;
   they are not asserted equal to initial bank inputs or to hosted data.

This is an existence and operator-equality statement for the explicit charts
below. It does not certify that an all-size compiler emits these charts within
the retained routing, tape, precision or finite-invoice budget.

## 1. Address algebra and specialization

For a symmetric idempotent P define

    D_P(x,y) = ((I-P)x + Py, Px + (I-P)y).

Direct multiplication gives D_P²=I. If PQ=QP=P, then
D_P D_Q = D_(Q-P). For orthogonal projectors P,Q with PQ=QP=0,
D_P D_Q = D_(P+Q). For an orthogonal sigma, writing bar(sigma) for its
action on both halves, bar(sigma) D_P bar(sigma)^-1 = D_(sigma P sigma^-1).
These are operator identities, not equalities of ranks.

The checker independently constructs all 636 frame projectors from the word's
root lines, using rational Gram-Schmidt. It checks symmetry, idempotence, and
all nesting and relative-transport identities used by both literal programs.
All final matrix entries are dyadic. Thus these identities are identities over
Z[1/2] and specialize to every such K; intermediate Gram-Schmidt denominators
are not additional excluded primes. Rank is also preserved: the characteristic
polynomial of a rational idempotent of rank r is t^(8-r)(t-1)^r. This polynomial
identity specializes, and idempotents over a field are diagonalizable because
0 and 1 are distinct. This proves rank r in the specialized field even when
its characteristic divides r.

## 2. Actual owner charts, including five helpers in family 666

For port q use the retained orthonormal complement U_q and the fixed chart

    A_q = diag([q/2 | U_q], I_56).

The checker verifies A_q^T A_q=I for all 111 ports, its dyadic entries, the
source rho15 data charts, and the stage embeddings. Crucially A_q is fixed
for the physical family, independent of the idle child and stage.

In these coordinates an idle child from level -1 to b has pending axes
1,...,7(b+1). One from level a>=0 to b has axes 8+7a,...,7+7b.
This follows directly from the data levels: source levels are P_q at -1 and
I_8+E_a at a>=0; target levels are 0 at -1 and I_8-P_q+E_a at a>=0.
Here E_a is the first a exterior seven-blocks. The difference is the same
for both members. The source rho_s interchanges q-perpendicular directions
with exterior block s; its displayed block matrix gives these boundary
identities in both call orientations.

For a descriptor (child, offset, 8), let S be the corresponding eight entries
in that ordered pending list. Define pi_S by mapping local axes 0,...,7 to
the ordered entries of S, then mapping the remaining axes to the unused
ambient axes in increasing order. Put sigma_S=A_q pi_S. This is an explicit
orthogonal matrix; it maps the full local residual projector to precisely S.

For the common invocation d the helper owner is

    (F, g),  g = d sigma_S^-1.

For data use g=d rho_s,q and sigma=rho_s,q^-1. Consequently g sigma=d
for every role. The private temporary uses a separate reserved family and
class d. Within a call, different data roles have different families; hosted
families belong to inactive pairs; the private family is outside the live
data stock. Helpers sharing F have different actual pi_S, not merely different
text descriptors. The verifier checks the slot supports and their disjointness
even when one call uses several idle children of that same family.

If two such helpers had the same physical class, canceling d and the common
A_q would give pi_S=pi_T. Applying them to a basis vector distinguishes them
over every K. Thus all 661 dirty roles and the private role have injective
physical owners at each fixed d. This does not assert disjointness across d.

For stage 2, replica 0, pair 0, the helpers 232,...,236 in family 666 use child
4 and supports 1..8, 9..16, 17..24, 25..32, 33..40. The pending support is
1..42, leaving 41,42. The checker conjugates all five full local swaps by
their actual permutations and checks completion on all 128 address basis
columns. The five distinct streams can carry correlated values without aliasing.

## 3. Whole-call simulation and the rank-seven issue

Work at a fixed common invocation d. Pull each owned physical row back by
bar(d), obtaining a common-address row f_i. Give it a bookkeeping gauge
Gamma_i and decoded row c_i=f_i composed with Gamma_i. A gauge is a bijection,
not a data reset. At stage s use the partial swap on the frame projector plus
E_s; for a reflected call use I_8-P_frame plus E_s.

MOVE from Gamma_a to Gamma_b changes the payload to
f_i composed with Gamma_a composed with Gamma_b^-1, so its decoded value is
unchanged. ADD between equal frames changes the decoded destination by the
decoded source. Fresh COPY uses the same transport into the private row, and
therefore copies its decoded value. If temporary and source decoded rows are
equal, bijectivity gives

    f_temp = f_source composed with Gamma_source composed with Gamma_temp^-1.

This is precisely the physical ERASE guard. Zero decoded payload is equivalent
to zero physical payload, so no dirty private value is silently discarded.
Induction over the literal events proves simultaneous execution correctness.
Injective physical owners ensure each event leaves all other streams unchanged.
The equation g sigma=d means a chart-routed ADD is exactly a common native
address ADD, rather than an additional unpriced data-dependent routing rule.

This is the generic simulation argument of PR540's FramedReplay and
OwnerTransport, instantiated here with PR589's word and owner construction.
The checker reconstructs every record directly from the pinned word and checks
equality with both template programs and their hashes. It propagates all 661
input columns simultaneously, including dirty helper columns. MOVE labels,
common ADD frames, clean COPY destinations, centre immutability, every ERASE
guard, and the final private zero are checked in that same chronological run.
The final decoded map is x'=x, h'=h, y'=y+x, for both orientations in their
local role ordering. This identity of Boolean-linear maps also holds after
substituting arbitrary correlated input functions.

PR540's concrete rank-eight COPY lemma cannot be reused unchanged. PR589 copies
sources 472,...,480 from frames 510,...,518 to frame 0. These frames have rank
seven. In the forward call, Gamma_510 Gamma_0^-1 = D_P510 on the local block;
the common E_s factor cancels. In the reflected call the relative map is
D_(I-P510) D_I = D_P510, again rank seven. The same calculation supplies
each matching ERASE transport. All nine frame pairs are checked exactly in
both orientations. The receipt includes distinguishing basis columns against
both a full rank-eight swap and a different rank-seven projector.

For a helper, the difference between its entry and exit gauges is the full
local eight-dimensional swap in either orientation. Returning to the native
physical stream (F,g) turns this into D on g A_q S. Data output formulas use
only that call's input data, because no helper column remains in decoded data
outputs. They agree exactly with the unhosted call using the same data owners,
regardless of the distinct and evolving bank/helper contents in the comparison.

## 4. Cover sweeps and chronological composition

Apply the complete-call result before commuting anything. For a fixed helper
slot, d -> d sigma^-1 is a bijection of the full group G. Thus its cover sweep
applies its residual once to every class of its host family. Different d's
may revisit a stream through other slots. They use its **current** contents.
Since the complete-call result held for arbitrary dirty functions, this is
legal without a fresh-input or independence assumption. Active data families
are disjoint from hosted families throughout that sweep. Residuals on disjoint
axes commute within each fixed (family,g) stream.

The checker independently walks the actual nine-stage schedule. Each local
stage enters its required level; every bridge has equal levels; idle children
have the actual source level; all pairs reach level eight before exchange.
For every host slot its stage lies after the last local/bridge touch of that
pair and strictly before its nominated idle child. Across those positions,
complete calls and bridges on other pairs have no endpoint dependence on this
family. Any intervening idle/host operations on this family use disjoint axes,
checked in the same fixed A_q chart. Consequently its residual can move to
its nominated child after complete calls have been reduced to their endpoints.

For each (family,g,child), the moved residuals occupy disjoint subsets of the
pending projector, and the remainder is exactly the complement. The partial
swap product identity in section 1 therefore reconstructs the original idle
child. Repeat for every child. All data, inactive streams and the private zero
are retained throughout; no prior bank output or hosted output is reinitialized.
This proves the retained-data equality in the stated exact stream model.

The count check yields the unchanged formal profile
{1:381024, 2:400416, 3:22752, 4:26880, 5:29376, 6:17376, 7:26784, 42:288},
rank mass 1808352 and deficit 10272. These are recursive rank counts. They do
not establish a new routing invoice or justify changing the selected result.

## Remaining obligations

The Python certificates and this written induction have not been ported into
PR540's Lean source provider. Its proof of the older PR442 call is not a formal
proof of this newer call. A finite-group operator proof also does not implement
the all-size injective compiler, child algorithms, common grid, restored work,
tape, precision, row, exceptional-class or analytic transfer contracts. Full
native supplier replay and finite invoice admission are separate checks.

Predecessors: DaysSky (PR442 hosting); Zhihao Chen, chafreaky and eumemic
(compressed geometry and retained supplier chain); DreamingOfClouds/eumemic
(PR545/555/589 punctured and tuned words); cheesegrader (PR540 formal framework);
commdata2338 (PR1307 ambient-axis census and PR1421 projector ledger);
1337isnot1337/CinnaDavis (PR1351/1371 physical-family operator checks).
Prepared with substantial OpenAI Codex assistance, Apache-2.0.
