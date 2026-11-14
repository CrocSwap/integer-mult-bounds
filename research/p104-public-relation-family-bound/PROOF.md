# Classify the entire two-dimensional relation space at the cheapest public cache

Source-bound theorem and separately conditional preparation corollary.
Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.

## Source, inherited certificates and exact scope

Use the unchanged #7481 word with SHA256
`acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9`.
Write g=e885-e705, h=e1459 and L=span(g,h). Consider exactly the scalar-linear
helper promises whose annihilator R is a subspace of L. Main inputs remain
arbitrary and independent. All other inputs range over the full kernel of R.
Instructions, event clocks, physical coframes and whole MOVE targets stay
fixed. Histories contain only strict earlier original observations.

The published all-history theorem at fork commit
`fdbb41450a98594bdf1f5fe4535e77d2466adb4f` proves independence of all 7,780
original observations across 979 coframes. This package reconstructs the
full exact-rational source rows and rechecks that rank certificate using its
byte-identical credited column-rank helper. Every other fact needed below is
reconstructed directly from the bundled word; the later singleton census is
credited as related work, not a runtime or theorem dependency.

## A support isolation lemma replaces an expensive parameter census

Owner885 has exactly four original touches:

| Event | Instruction |
| --- | --- |
|30780|ADD into885 from 943, coefficient1/2, frame 3|
|40710|MOVE885 from 3 to189|
|40711|ADD into885 from 705, coefficient-1/2, frame 189|
|41698|ADD into885 from 943, coefficient-1/2, frame 189|

It is never an ADD/COPY donor. Induction on the source instructions implies
that no other field ever acquires a nonzero e885 coefficient. Thus the only
original history generators containing e885 are its initial row in frame 3
and its arrival at 40710 in frame 189. Frame3 has no MOVE arrivals at all; its
history consists solely of its1,060 original coordinate units. Neither705
nor1459 initially has frame 3 (their frames are105 and 189).

Consequently, a vector g+lambda*h cannot lie in any final coframe span other
than189: every other frame except3 lacks e885 entirely, and frame 3 lacks the
mandatory e705 coefficient. This is uniform over every scalar lambda. It is
not inferred from checking a finite list of parameters.

Exact source replay gives the frame 189 rows

    r_initial1459 = h,
    r40708 = e705+e943,
    r40710 = e885+e943.

Therefore

    g+lambda*h = r40710-r40708+lambda*r_initial1459.

The full frame 189 family is independent, so this representation is unique.
Its latest nonzero support member is always40710, including lambda=0.

## One-circuit criterion and every one-dimensional promise

Let B be an independent chronological observation family and let a nonzero
relation u belong to span(B). Its unique expression in B is the only new
dependency after quotienting by span(u). A MOVE arrival becomes recoverable
from strict earlier observations exactly when it is the latest nonzero
support member of that expression. A row vanishes individually exactly when
the expression has singleton support. If u is outside the final span, no
prefix changes rank at all.

Apply this to u=g+lambda*h. The sole new cached MOVE is40710, of rank 8; no
MOVE is zero. The actual decoder identity under the promise is

    r40710 = r40708-lambda*r_initial1459.

All providers are strictly earlier and in the exact same physical frame 189.
There are no exceptional finite lambda values creating another cache. The
remaining projective direction is span(h). Fresh source replay shows that
the only observations with a nonzero e1459 coefficient are its initial
unit in frame 189 and the arrivals at 45748 (owner 1459) and 52236 (owner 763),
both in frame 127. No other coframe can contain h. Inside frame 127 the exact
circuit is

    h = r45748 - (1/4)*r52233 - r52236.

The original frame 127 observation family is independent, so this expression
is unique. Its latest nonzero support is52236, and its three-term support
excludes a zero MOVE. Inside189 the unique expression is the initial unit,
which is not a MOVE. Thus h=0 enables exactly the nonzero rank-one cache
at 52236 and no zero MOVE. All three circuit rows are directly reconstructed
and bound to their actual physical frame 127; no saved membership verdict or
separate singleton theorem is needed.

## The full two-dimensional promise

For any other coframe P, every vector in P intersect L has zero g coefficient,
because g has the isolated e885 coefficient. Thus P intersect L is contained
in span(h); frame 3 has zero intersection with L. The only effects outside189
are therefore exactly the effects of h=0 just proved, namely event 52236.

Inside189, h is an initial generator and g=r40710-r40708. Quotienting by L
kills that initial h generator and makes40710 equal40708. Independence of the
full original family excludes every other new dependency. No MOVE row lies
in L: among the relevant generators only the initial h does. Hence R=L
enables exactly the two nonzero cached MOVEs40710 and 52236, of ranks8 and 1,
and no zero MOVE. R=0 changes no target. This exhausts every subspace of L.

## Exact original-target funding

The original helper target ranks are R705=R885=8 and R1459=1. Retain only
original coordinate targets, and fully debit every helper not retained. For
surjectivity onto the retained coordinates, a rank-one relation must have at
least one nonzero coefficient on a debited coordinate. For R=L, the two
relation rows must remain independent on the debited columns. This forces
loss of 1459 and at least one of 705 or885. Extra debits cannot improve the
budget. Write f(r)=r^(1-kappa),0<=kappa<=1, with f(0)=0.

| Annihilator R | Newly cached MOVE events | Least target debit | Optimistic native gain |
| --- | --- | --- | --- |
|0|none|0|0|
|span(g)|40710|f(8)|0|
|span(g+lambda*h),lambda nonzero|40710|f(1)|f(8)-f(1)|
|span(h)|52236|f(1)|0|
|L|40710,52236|f(8)+f(1)|0|

These are information-relaxation prices with free correlated initialization,
history backing, ordinary processing and zero reframing. They are not
physical savings or an assembled exponent. In particular the positive line
cannot be dismissed merely by deleting 1459's final target credit: the exact
cache decoder uses1459's initial value.

## Conditional preparation conclusion

Add the explicit access contract that retained original885 and 705 are given
at their original entrances while the correlated demoted1459 value is not a
free input resource and must be constructed or separately charged. Freeze
the original producer histories and use a fixed instruction/dataflow schedule
of coframed scalar operations and paid whole native MOVEs. Dataflow fanout is
allowed. Every information dependency crossing frames must follow a charged
transport edge; an input-dependent control/descriptor channel or ordinary
frame algorithm may not bypass that graph. These are restrictions of this
corollary, not an assumption about every Turing-machine implementation. For lambda nonzero the probe

    x885=1, x705=0, x1459=-1/lambda, all other inputs zero

satisfies the relation. After excluding the demoted initial slot, the only
available nonzero dependence before 40710 is in 885 at empty frame 3. It must
reach dimension-eight frame 189. Every such new path has total integer rank
at least8: a Clifford with Fourier rank r has row support size 2^r, and
composition gives r(UV)<=r(U)+r(V). The source-to-destination rank from
empty frame 3 to189 is8. Increasing subadditivity therefore makes the total
new whole-job price at least f(8). No new payload may be inserted into an
already paid original carrier/job; such a changed producer is outside this
access/transport corollary. The
cheapest-target line then has net gain at most-f(1). Choosing an expensive
pivot705 or885 instead already loses at least f(8), so its information
budget is at mostzero even before preparation. All other rows of the table
also have nonpositive gain before preparation.

This corollary prices only the original-history cache and zero-MOVE credits
in the table. Intermediate setup scratch is not an additional free history
provider for other original jobs; any such further supplier modification
needs a new credit classification and full invoice.

Thus no scalar subspace of this particular L improves the native moment
through the classified original-history replacements under that additional
access/transport contract. The unchanged17-call
comparison gains no native price from this modification. This is not an
unconditional preparation lower bound, and does not rule out supplied
correlated inputs, changed producers, other helper relations, cross-call
encodings, ordinary alternative frame algorithms or newly priced target
interfaces. Public zero-reframing still needs its own admitted contract.

## Verification and limitations

`verify.py` freshly executes all 76,475 instructions over Q, checking live
owners, coframes, nesting, COPY freshness and final lifetimes. It checks all
7,780 original observation rows, their exact e885/e1459 supports, all four
885 touches, no885 donor use, no frame 3 arrivals, both exact circuits and
original target ranks. Its column certificate reaches every literal bank
row count modulo the proved prime 1,000,033; invertible rational denominators
and the trivial row-count upper bound prove full rank over Q, and therefore
over R and C. Used physical-frame IDs are checked to have no span aliases,
so no phase equivalence is inferred from equal spans.

The source-support statements and unique-circuit proof establish the infinite
parameter classification. No finite list of lambda values is used as a
universal certificate. The exact two-row restriction matrix establishes the
minimal-debit rule: for a nonzero-lambda line the 1459 column is nonzero; for
the full plane the 1459 column and either705 or885 are necessary and sufficient.

Executed failure controls reject a changed source byte, an added885 donor,
an unaccounted frame 3 arrival, an omitted1459 observation, a wrong circuit
sign/coframe/latest member, and illegal cheap debit sets. Checks remain
active under optimized Python. Normal, optimized and read-only export
receipts are recorded in VALIDATION.json after execution.

The abandoned general intersection-census attempt produced no completed
receipt and is not evidence. This support proof replaces that computation.
Only scalar-linear annihilators inside this particular two-dimensional L are
classified. Other relations, block-operator promises, changed producers,
supplied correlated inputs and general frame algorithms remain outside its
scope. No global foundational assumption is removed and there is no new
kappa. Original sources and prior all-history, public-price, singleton-zero
and preparation investigations retain their authorship.
