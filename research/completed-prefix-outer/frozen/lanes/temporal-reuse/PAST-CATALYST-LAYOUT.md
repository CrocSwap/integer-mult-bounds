# Place completed coordinates at the current native offset

This note gives an address wrapper for a possible past-coordinate
supplier. It resolves the common-offset requirement. It does not
construct the supplier, establish its cover, or price its full
recursive profile.

Suppose a finite native word uses `a f` active coordinates and `p f`
past coordinates. Each coordinate has a complete `K`-bit chunk.
Only one bit per chunk is selected. The desired current offset is
`rho`, with `0<=rho<K`. The word must fix every other address bit,
including a designated spectator field. Scalar changes of role
values are allowed. All data values, including borrowed values,
are arbitrary.

The relevant source statements are the elementary stream operations
in Section 02, the arbitrary-width interchange in Section 04, and
the selected-bit chart interface in Section 05. The checker pins
their exact Git bytes. In particular, the interchange on two
`u`-bit address fields costs `O(V u^tau)` with arbitrary complete
prefix, gap, and suffix ranges. It includes its own padding,
descriptors, counters, and work-tape cleanup.

## The rotation word

Let `X` and `Z` be disjoint complete address fields of the same
length `L`. For `0<c<L`, write

```text
X=A B,  |A|=c,   |B|=L-c,
Z=C D,  |C|=L-c, |D|=c.
```

Apply these three equal-width interchanges in order:

1. Exchange `A` and `D`.
2. Exchange `B` and `C`.
3. Exchange the full `X` and `Z` fields.

The result is `X=B A`, `Z=D C`. Thus `X` rotates by `c` positions
and `Z` rotates in the opposite direction. The fields need not be
adjacent. Their intermediate shapes are complete address rectangles,
so every interchange is an instance of the cited lemma. The zero
rotation is the identity and needs no call.

Take `X` to be the complete past-chunk block, so `L=p f K`. Choose
the direction and `c` so that an old position `jK` moves to
`jK+rho`. For example, with positions numbered from zero in the
order used by the checker, choose `c=(L-rho) mod L`. No selected
position wraps around, since `rho<K`.

Apply this three-interchange word before the native word and its
literal inverse afterward. The native word uses the now aligned
past selected bits and fixes `Z`. It also fixes all unselected bits
of `X`. Therefore the wrapper restores every bit of `Z` and every
guard bit. Its only effect is to make the native word act on the
original selected past bits at positions `jK`.

This is an operator identity on arbitrary arrays. The argument does
not assume that the spectator address is zero, that its values are
independent, or that any data work field is clean. A finite role
program must apply the same address wrapper to every physical field
whose type uses this coordinate system. Its total physical volume
is the one in its existing stock invoice. The wrapper creates no
productive field or extra address bit.

The six interchanges have total time

```text
O(V (L^tau+1)) = O(V ((eK)^tau+1)),   e=(a+p)f.
```

There are no new complex Fourier children. This is the same order
as the explicit coordinate-map overhead in Section 05. It is not
permission to omit the additional fixed map count from a selected
finite compiler or precision invoice.

## Make the two blocks adjacent

The finite native word may require its active and past chunks in
one consecutive group. Reserve an equally sized address block next
to the current active group. Exchange that block with `X` before
alignment, and exchange it back after the inverse alignment. The
two displaced blocks have arbitrary values; both return to their
initial positions outside the native action.

If the past block is after the active block instead of before it,
permute the fixed number `a+p` of slots of width `fK` into the
declared order and restore that permutation afterward. Equal-width
interchanges implement each slot exchange. The number of slots is
fixed by the finite construction. These operations add only a fixed
number of calls of the same asymptotic type. A compiler must include
their literal count.

The rotation spectator `Z` is disjoint from this consecutive native
group. It need not be adjacent to `X`. The native word must act as
the identity on `Z`; the wrapper cannot be used if a child also
uses that field as a selected coordinate.

## Obtain the reserve without new address bits

Here is one concrete placement for the proposed split `a=64,p=9`.
The same argument works whenever `2p<a`. Assume that at least three
complete chunk groups remain in the outer layout. Each group has
`a f K` address bits. Two blocks of length `p f K` fit inside one
inactive group because `2p<a`.

Complete one branch bit on each participating axis first. The
forward procedure needs at most two initial parallel rounds. The
reversed-label opposite procedure in
[COMPLETED-PREFIX-CODES.md](COMPLETED-PREFIX-CODES.md) needs one common
round. Evaluate these rounds by individual butterflies. This costs
`O(Vd)` and does not add a transform round. There are enough distinct
completed bits to choose the `p f` past coordinates.

Reserve `X` and `Z` in the last chunk group in the processing order.
Use at most `p f` single-bit exchanges to put the chosen completed
coordinates at positions `jK` in `X`. The displaced bits go to their
old positions. All bit names remain in the descriptor. In particular,
an unprocessed bit that has moved remains available to a twiddle's
address calculation. It is not treated as a completed bit.

Until that last group is needed, the reserve is inactive. For each
call, bring `X` next to the active group, align its offset, run the
native word, and undo those temporary address operations. A neighbor
group supplies the temporary adjacent block. The reserve and that
neighbor must be distinct from the active group; there is no demand
for a zero address range.

Before the original reserve group becomes active, undo its initial
single-bit placement. This restores all of its unprocessed bit
positions. Recreate the reserve in the first group, which is now
fully completed. That second placement changes only completed
coordinates. Retain the same logical past-coordinate names, then
restore the placement at the end. This uses `O(p f)=O(d)` initial,
switch, and final digit exchanges in total, not per outer round.
The construction is symmetric for the opposite processing order.

The source has `q=floor((ell-1)/K)` complete chunk groups. Its selected
strict geometric condition is `1-epsilon(1+c)>0`, where
`ell=Theta(p/d)` and `K=d^c` up to rounding. Hence `q` tends to
infinity, and the three-group requirement holds for all sufficiently
large inputs. This statement gives no numerical threshold. Handle
the bounded remaining size range by a separate direct base procedure.

The total added one-time placement work is `O(Vd)`. The selected
strict inequality `1-epsilon-kappa>0` permits this order. The per-call
rotation and placement work has the node bound above. A selected
compact-engine construction still needs an exact updated descriptor,
map, guard, and hosting invoice; this note does not certify that
invoice.

## Keep the row field separate

Past payload coordinates cannot also serve as row-index digits.
If the row code must itself be on completed coordinates, the separate
whole-axis construction in `COMPLETED-PREFIX-CODES.md` gives enough
row bits for every recursive depth at cost `O(V ell)`. Exclude that
axis from the chosen past payload coordinates and active axes.
The remaining axes provide the `p f` completed bits above. This
changes the available active dimension by a fixed number of axes;
a full supplier construction must state its integer grouping and
base-case policy. No coordinate is duplicated.

## What this enables, and what remains open

If a native family keeps a fixed past subspace and needs only the
common-offset access described here, the physical offset no longer
requires individual moves of `Theta(d)` bits in every round. The
wrapper gives the needed exact access through existing bit
interchanges.

It does not show that the actual full orthogonal cover keeps the
chosen past subspace. It does not change a Fourier child of rank
`r` into a child on the active projection for free. It does not prove
that a changed child composes in its parent. Those are separate
mathematical and native-interface conditions. In particular, no
new exponent or complete multiplication supplier is claimed.

## Exact checks

Run:

```text
python3 -I -O -B check_past_catalyst_layout.py
```

Expected first line:

```text
PASS_PAST_CATALYST_LAYOUT
```

The checker uses no producer imports. It checks all bit positions
for 168 combinations of chunk count, width, and offset. It checks
the selected-mask pullback and the inverse permutation, including
the spectator field. It also checks 24 exact early/late reserve
placements at the proposed `64:9` split. These finite checks verify
the literal permutation formulas. The all-size cost and restoration
claims follow from the proof and the pinned interchange lemma.

This note was prepared with OpenAI Codex assistance. It remains a
conditional native-layout result and is not a selected supplier.
