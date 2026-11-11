# Changing-node composition of the actual CRT state evaluator

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Apache-2.0. The independent checks below are mathematical/source checks by
model-assisted agents, not independent human or proof-kernel acceptance.

## 1. Exact claim and what is inherited

Let `d >= 2` be a power of two, `ell >= 2`, and let the **declared** widths
`h_i` belong to `{ell-1,ell}`. Let the supplied axis stream contain pairwise
coprime moduli `2 <= s_i < 2^h_i` and arbitrary padded coordinates
`0 <= x_i < 2^h_i`, in the exact tagged representation of #5353. Its owner
permits writes to coordinate bits and no other input fields. The source
shape, width tuple, node/row schedule and fixed ROM program are compiled
metadata; they do not depend on coordinate values.

**Theorem (source-relative whole-tree composition).** Under the numerical,
ROM, and physical-row contracts inherited from #5053, #5219, #5353, #5092,
#5496, #5519 and #5625, `tree.WholeTree` executes the complete balanced CRT
state permutation of #4195 and its inverse on the **same** physical axis
stream. It uses 127 fixed owned roles: the actual 118-role row workspace,
eight protected-zero numerical roles, and one result staging role. Every
row retires all its private data, and every traversal returns all private
heads and preserves the source metadata. A forward/reverse pair restores
every source byte and its entry head. The retained storage is the sum of
the rolewise historical capacities; it is bounded independently of how
many successful traversals have occurred.

The supplied source role is additional. This inventory is not a total
fixed tape count for a uniformly encoded machine: topology and external
source generation are still supplied interfaces. The eight added roles
contain only exact-width zeros; they are not header or context storage.
All current numerical context and ROM headers remain in the inherited
118-role workspace.

This theorem covers changing nodes, changing precision, and shorter uses
after larger historical backing. #6100 explicitly fixes its node and
precision; #5625 explicitly excludes whole-tree changing-precision entry.
Their local theorems are used, not re-proved. The new obligations are the
changing-node ownership seam, current-width protected-word entry, complete
source-state induction, and summation of their actual tariffs.

This is an **address-state/control evaluator**. It does not move the full
CRT payload. A polynomial or exponential bound on computing an address
key does not by itself provide a fast permutation of all payload records.
The interface receives compiled topology and the supplied axis stream;
their uniform production/encoding cost remains separately named below.
No complete binary transition program, three-epoch compact repair key,
full `E(p,ell)` bit-step theorem, new kappa, or discharge of an entire
selected foundational assumption is claimed.

## 2. The one changed workspace check

`workspace.py` is exactly #6100's file except for the one replacement in
`SEAMS.json`. The old guard requires the full tuple
`(widths, ell, level, start)` to equal its previous value. The new guard
requires only `(widths, ell)` to remain fixed. Source/protected alias
checks, single live owner per role, role selection, marker writes,
head returns and complete owner counts are unchanged. The verifier
reconstructs this file byte for byte from the pinned predecessor.

There is no precision field cached in this workspace. On every invocation,
#5353 reads the current axis records and constructs the unary guide of
length

    P_G = 1 + sum_(i in G) h_i

for the actual node `G`. The retained numerical template and all padded
streams are rebuilt from that guide. The ROM headers are rebuilt from the
same current guide. Thus allowing a different node changes neither a
numerical value nor a width by fiat.

The exact role map remains #6100's: 63 numerical roles, 52 ROM/header
roles and three query roles. At a retired boundary the numerical ports
are blank at head one and all other row roles are blank at head zero.
The original paid entry restores the required LEFT marker and head.
For a larger new width the source methods append blank cells only through
their declared local movement/write semantics. For a smaller new width
the older unused tail stays blank. Every valid source instruction reads
the same symbol as it would on a fresh blank tape; no scientific branch
uses retained capacity to choose a value. The source cleanup theorem
clears the current visited extent, and untouched old cells remain blank.
Induction gives valid reentry, stable backing identities and full-history
blankness for every legal node sequence, not just equal-width rows.

The inherited numerical `Word.step` emulator checks physical bounds.
That observation is not a free numerical oracle: on the valid source
execution the delimiter-driven algorithm remains within its current
constructed extent. Larger retained blank capacity does not change a
successful branch. No malformed-input or failed-initialization rollback
extension is asserted.

## 3. Protected words really have the new precision

The #5219 numerical entry asks for eight disjoint dirty words of exactly
the current `P_G` bits. It would be incorrect merely to carry a previous
node's dirty-word extent into that premise. This package instead owns
eight permanent auxiliary roles and uses the admitted zero case of that
contract.

Before each active row, `ProtectedZeros.prepare(P_G)` writes LEFT, exactly
`P_G` zero cells and RIGHT using single-cell writes and unit moves. It
then returns each head to one. After the row query has retired,
`ProtectedZeros.retire()` uses the existing local `Port.retire` scan to
erase those words and their markers. Their contents are zero on entry,
but their width is exact; no dirty-word theorem is silently generalized.
All eight backings are distinct from the source, staging and 118 row
roles. Their previously longer blank tails are retained and charged.

The construction requires initial owned blank roles, just as the pinned
row providers do. It does not acquire arbitrary dirty ambient storage.
For one word, preparation and retirement make fewer than 32 local
read/write/move operations per `P_G+2` cells; fewer than 16 finite control
steps occur between them. Therefore `2^12(P_G+2)` is a conservative
source-operation allowance for all eight words. Their initial eight
blank cells are charged positively once. No numeric input is decoded:
`P_G` is a constant in the supplied compiled node.

All-idle rows are explicit no-ops: the controller calls neither the
numerical provider nor the ROM provider and performs no tape operation.
Their presence in the compiled schedule does not manufacture target bits.
The supplied compiled control may omit those operations entirely; they
remain in the verifier's trace to show the published synchronized order.
Any literal runtime decoding or dispatch of a topology representation is
part of the separately named `T_topology` interface, not a zero-cost
operation inferred from the tape-work trace.

## 4. Whole-tree source-state induction

The forward command order is exactly:

1. balanced levels `j=1,...,log2(d)`;
2. synchronized rows `r=0,...,2ell-2`;
3. aligned nodes of size `2^j`, in increasing starting position.

At one row, nodes have disjoint coordinate blocks. Each node changes
only its right child and reads only its own left child for its numerical
offsets. Serializing these disjoint node operations therefore realizes
the simultaneous row in #4195. No other node changes its left controls.

Suppose the supplied stream contains the correct current state before
one active command. The unchanged #5496 query reads those actual cells
and produces the next right-node coordinate slice. #5625 copies that
slice to the separate staging tape, closes the query and ends its source
borrow, then writes the staged coordinate bits into the same source.
No source write occurs while the old numerical/ROM borrow is live.
The modulus fields, width fields, delimiters, exterior coordinates and
source extent are unchanged. Staging and all query roles then retire.

The resulting padded coordinates remain in `[0,2^h_i)` even when an
intermediate switch visits `x_i >= s_i`. In particular the controller
does not reapply a target-validity test at a micro-row; that would be the
already documented wrong lowering. Left-child invalidity is handled by
the actual numerical producer's inherited disabling rule.

Section 2 admits the next node's fresh guide and templates; section 3
admits its fresh exact-width protected words. Induction over every
command therefore gives the whole #4195 padded state permutation.
For globally valid input this is the already proved CRT map: if
`P_i=product_(k<i) s_k` and `k=sum_i x_i P_i`, the final coordinates are
`k P_i^-1 mod s_i`. This identity is a predecessor result and a verifier
oracle, not new mathematics claimed by this package.

Every row is an involution at its current left controls. The inverse
controller reverses the **entire command list**, including node order,
rows and levels. Reversing each completed row gives the prior source,
so the physical round trip restores every byte and head. This argument
holds for every padded input, not only the globally valid subset.

## 5. Complete within-interface time sum

The cost unit here is the compatible fixed-alphabet **source operation**
of the inherited row proofs. It includes their declared arithmetic,
finite control and literal ROM instructions. It is not automatically a
unit binary TM transition. Let

    A = sum_i h_i,             M = 2 + 3A + 4d,
    n_G = |G|,                P_G = 1 + sum_(i in G) h_i,
    S_G = 2 + sum_(i in right(G)) h_i + n_G/2.

For an active row with target set `J`, retain the exact inherited bound

    F(G,J) = M + (n_G+1)(P_G+2)
             + sum_(i in J) [(2^h_i+1)(h_i+1)
                             + 2^h_i(2h_i-1) + 2h_i+4],
    E_entry(G) = 2^20(P_G+2)^4 + 2^16(P_G+2)^2
                 + 128(M+P_G+n_G+1),
    E_ROM(G,i) = 2*10^6 P_G^2 (2^h_i+1)^3 (h_i+1)^4,
    E_row(G,J) = E_entry(G) + sum_(i in J) E_ROM(G,i)
                 + 4096F(G,J) + 4096(M+S_G).

This pays full unused-layer disposal, encoded current-coordinate queries,
header creation, all source scans, staging, erasure and rewinds. Add
the #6100 stable entry allowance `4*63+118` and section 3's
`2^12(P_G+2)`. Thus the precise one-traversal bill is

    8 + sum_(active commands)
        [E_row(G,J) + 4*63+118 + 2^12(P_G+2)].                 (1)

The inverse has the same topology and bound; a round trip doubles the
sum, retaining the initial eight-cell charge once. `row_bound` and
`whole_bound` implement exactly (1). The verifier independently compares
every actual row with the unmodified #5625 formula and checks the declared
additions. An arbitrary number of traversals incurs its corresponding
sum; no number of calls disappears through workspace reuse.

### Geometric summation, rather than root-cost times node count

For `A <= p`, `p >= 2`, the balanced near-equal widths give `d(ell-1)<=p`.
At level `j`, `n=2^j` and there are exactly `d/n` nodes. Consequently

    sum_G (P_G+2)^4 < (8/7)(ell+3)^4 d^4 <= 715p^4,
    sum_G (P_G+2)^2 < 2(ell+2)^2 d^2 <= 32p^2,
    sum_G P_G^2 (n_G/2) < (2/3)(ell+1)^2 d^3 <= 6p^3,
    sum_G (n_G+1)(P_G+2) < 3(ell+3)d^2 <= 15p^2.            (2)

For example the first line follows by summing
`d(ell+3)^4 sum_(j=1)^k 2^(3j)`; it is not a max-node bound repeated
`d-1` times. For the second line, `n>=2` gives
`P_G+2<=n(ell+2)`, and `sum_(j=1)^k 2^j=2d-2<2d`.
The last inequalities use `(ell+3)/(ell-1)<=5`,
`(ell+2)/(ell-1)<=4` and `(ell+1)/(ell-1)<=3`, together with
`ell-1>=1`. All four are quantified geometric sums.

There are at most `2ell-1 < 2p` rows per node, `M <= 8p`, and at most
`p` nodes. For `h>=1`, the axis summand in `F` is exactly
`3h 2^h+3h+5`; its `4096` multiple is below the corresponding
`E_ROM` allowance. Also `2^ell+1 <= (5/4)2^ell` for `ell>=2`.
Substituting (2) into (1) gives the deliberately loose explicit majorant

    T_traversal <= 2^34 * 2^(3ell) * (p+2)^8.                (3)

To check the constant without empirical timing: the entry quartics
contribute less than `2^31 p^5`, the entry quadratics less than
`2^23 p^3`, and the remaining non-ROM terms less than `2^20 p^3`.
The complete ROM sum is at most
`48*10^6 2^(3ell) p^4(p+1)^4`; a second copy covers the axis summands
just absorbed from `F`. These are jointly below (3), including the eight
initial cells. For `p>=14`,

    2^34 * 2^(3ell) * (p+2)^8
        <= 2^(4ell) * (p+2)^16,                             (4)

because `2^ell(p+2)^8 >= 4*16^8 = 2^34`.

Equations (3)-(4) show that summing these actual row-provider allowances
does not introduce a new power that already exceeds the published
`E(p,ell)` shape. They do **not** identify the source-operation unit
with the bit-step unit of #4377, nor close topology setup, initial source
serialization, variable-geometry key transport or payload routing. If
those supplied interfaces, including topology production and its encoded
traversal, have costs `T_topology` and `T_source`, the
complete call is `T_topology + T_source + T_traversal`, not just (3).
Those two terms are not silently set to zero. The source-relative
composition and (1) are the new claims; a global evaluator admission
still has named remaining obligations.

## 6. Historical storage across every node

Let `P*=A+1`, `H=ell`, and `S*=2+A+d`. Define the inherited complete ROM
bank bound

    B(P,H)=5P 2^H(H^2+3H+1)+2^H(4H-1)+48P+2H+104.

For each role use its own monotone upper bound at `P*`, `H` and `d`:
58 numerical word/template/guide roles each use at most `P*+2` cells;
five numerical stream roles each use at most `d(2P*+4)+2`; each of
52 ROM roles is bounded by `B(P*,H)`; two query roles use `H+2` each;
the query output and staging each use `S*`. The eight new protected
roles each use at most `P*+2`. Including the supplied source itself,
a complete upper envelope is

    M + 2S* + 8(P*+2) + 58(P*+2)
      + 5[d(2P*+4)+2] + 52B(P*,H) + 2(H+2).                 (5)

Using a complete-bank bound separately on every ROM role is loose but
safe. No claim that one node simultaneously realizes every maximum is
needed. Actual retained capacity is exactly the sum of each distinct
backing's historical capacity. It is never replaced by the largest
standalone node total. Initial source/owned blank extents and every
retired role remain included. The bound is
`O(2^ell p ell^2+p^2)` under `A<=p`, independent of traversal count.
Compiled topology storage and any external source-generation workspace
remain outside the named 127 owned data roles and must be added at that
separate boundary.

## 7. Evidence and remaining obligations

The actual four-axis fixture uses moduli `(5,7,3,2)`, widths `(3,3,2,2)`
and initial state `(3,2,1,1)`. It traverses all 15 forward commands and
their complete reverse, changing numerical precision among 7, 5 and 11
on the same role bank. The forward endpoint `(3,4,0,1)` is also checked
against an independently implemented defining CRT formula. A second
actual fixture checks invalid-left disabling and padded target values.
The receipt records every actual provider call, stable identity,
per-role retained extent, source update, complete row allowance and
observed source traffic. Finite values corroborate the proof; they do
not extrapolate all widths from the sample.

Negative controls detect live reentry, source mutation before close,
changed global shape, a stale retired tail, unretired protected-word
resize, the predecessor's actual next-node rejection, invalid shape,
an omitted subtree, max-of-totals storage, and the rejected `4/3`
quadratic geometric coefficient found during independent review. The
old fixed-node check
is not a bug in its declared domain; it is the precise boundary extended.

The next useful steps are a charged encoded topology/source producer,
and the variable-geometry three-epoch exceptional key with the actual
current-state conversions. The full payload stage, ordinary interchange,
precision/native supplier and outer multiplication assembly remain
external. The current selected kappa remains `.00363005817` under its
five retained assumptions. No selected-source file is changed.
