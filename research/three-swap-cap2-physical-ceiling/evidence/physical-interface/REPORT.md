# Three-SWAP cap-two mechanism: physical-interface feasibility

**Read/derive outcome: the formal changed mechanism is soundly separated from
its missing physical supplier. No strictly subadditive cap-two physical call
was identified in the declared source lineage. No eligible paid occurrence,
changed recursive histogram, emitter or new kappa is established.**

This review concerns Nick Petalas's #5083, exact head
`d2b3f35275cab6fbf18bee40e3fb411496732e54`, and only the physical first question
in `research/rank2-swap-batching/README.md`. The author owns the formal
five-call construction; its checker was not rerun or duplicated. The monitor's
08:28 UTC ownership check found the formal claim complete, physical/native
compilation explicitly open, and no matching physical claim in its refreshed
coverage. This is a local root-authorized feasibility review, not a public
construction reservation. All inspected bytes are listed in `SOURCES.json`.

## 1. Exact missing ABI

The formal payload space is a direct sum of independent owner fields. For a
physical representation rho_f(g) on one complete address range Omega_f, the
attaining word needs only coordinate-projector calls of the form

    Cap2(g,{i,j}): (u0,u1,u2,dirty...)
      -> (rho_f(g)u_i, rho_f(g)u_j, all other original fields unchanged),

with g=a or b. Every u_r is an arbitrary independent payload function on the
complete same-shaped range; arbitrary row and other spectators are retained.
There are two output jobs on the two original inputs, not one job on their
sum, one zero source, or a discarded owner. The third active owner and every
dirty spectator must be individually restored. A candidate must specify the
actual representation, axis order, orientation, weights, width lifting and
complete physical entry/exit maps. The word does not need a physical
implementation for every nonidempotent rank-two N allowed in the lower-bound
model: the attaining calls use only diagonal idempotents.

Let c1 be the complete physical charge for the matching one-owner call and
c2 that for this two-owner transaction, including preparation, routing,
storage and return to the same ABI. The formal comparison is

    new = c1+4c2,       formal disjoint = 3c1+3c2,
    formal saving = 2c1-c2.

Any outside-call overhead difference must be charged separately, without
counting in-call work twice. This comparison is useful only if the actual
caller has that comparator, or a more expensive proven one. It is not a
statement that scalar rank two is a recursive rank-two child.
Both labels and all selected pair positions need the same asserted tariff;
otherwise the new bill is c1_a+2c2_a+2c2_b rather than the uniform expression.

The diagonal attaining schedule could act on an actual representation over
other payload coefficient fields too: it merely applies group elements to
selected owners and uses no scalar XOR bridges. That observation does not
transfer the formal model's arbitrary-coupling lower bound or its tariff to
the complex construction.

## 2. Existing BIT supplier has a different batching dimension

The selected record retained at the reviewed head names the conditional
#4470 supplier. Its `notes/batched-bit-rows.tex`, lines 9–25, explicitly gives
each rank-r child address width r*f and exactly one role's logical volume
V/W. Repetitions are separate calls. The integer-width and spectator rules
retain the full unused address ranges. This is batching of **address
directions inside one arbitrary field**, not batching of two independent
owner fields.

Placing two owners into two ROW values produces one same-address-width job
on volume 2V/W. Under the retained volume normalization this is charge 2c1,
before any additional packing/routing. It supplies a legal linear-price
implementation, not c2<2c1. With c2=2c1 the formal saving is zero. Treating
that pair instead as a width-2f child at volume V/W has no supplied layout or
hosting proof. In particular, a direct sum of two arbitrary functions on
Omega_f is not one arbitrary function on the product address range used by
two active address directions. Padding, cross terms and all restored values
would have to be accounted for. The ability to preserve arbitrary ROW fields
does not remove their logical volume.

The same distinction is visible in the source-bound BIT native binding at
`20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`,
`research/kappa-rebuild/bit/bit_native_binding.py`: physical projector rank is
rank in a rational head-coordinate space, and whole-rank requests act on one
current arbitrary-input role. Independent helper ownership is recorded
separately. That source supplies no two-owner cap-two price rule.

No fixed-alphabet or fixed-tape SIMD discount is assumed. A packed payload
alphabet, growing type, shared decoder or bulk backend would be a new supplied
interface requiring its own recursive closure and complete cost argument.

## 3. A concrete address representation, with orientation-sensitive comparator

#2415, retained in #5083's declared sources, identifies GL2(F2) with S3:
a=(12), b=(23), s=(13). One can therefore realize those labels as permutations
of three complete address chunks, with any other fields as spectators. This
avoids silently applying the natural binary-CNOT matrix to the odd-radix atom
ring used by the actual BIT supplier. The latter is not the same address
operation: binary XOR and addition on Z/q^w have different orders.

If all three S3 transpositions are represented as **ordinary** chunk swaps J,
the existing arbitrary-spectator BIT service also implements target s directly.
They have the same complete shape and ordinary-swap tariff. Three target
owners then have a direct recipe of price 3c_J, whereas the proposed five-call
word costs at least 5c_J when c2>=c1=c_J. The formal six-call comparator is not
the physical comparator for that representation.

There is another relevant, cheaper-generator orientation. The retained raw
atom contract is

    F_f(H,D)=(C_f D,C_f H),

where C_f reverses atom positions but not digits within an atom. Let a=F12
and b=F23 on three chunks, with C=C_f and C^2=I. Direct substitution gives

    (x,y,z) --a--> (Cy,Cx,z)
            --b--> (Cy,Cz,x)
            --a--> (z,y,x).

Thus aba is ordinary J13, not raw F13. These are exact address maps at every
width, with the middle chunk restored. No five-call formal-word computation
is needed for this orientation check.

The source supplies a concrete ordinary-swap upper recipe in
`notes/three-stage-cover-bit.tex`, lines 172–187:

    J_A = R_tail F_A R_tail,
    cost(J_f) <= cost(F_f)+2 cost(F_floor(f/2)).

Each call retains the entire current logical volume, with unused digits as
spectators. This is an upper recipe, not an exact minimum. In the unweighted
case the five-call candidate for three ordinary targets must be compared
against the available bound 3F_f+6F_floor(f/2), not just its formal disjoint
word. A necessary condition to beat that explicit direct recipe is

    F_f+4c2+Delta < 3F_f+6F_floor(f/2),

where Delta is any additional outside-call cost difference. No numerical
power price is asserted for c2. If a separate induction price F_t proportional
to t^tau were applicable at the same logical volume, this threshold would
be about c2<1.25F_f near tau=1, substantially stronger than formal strict
subadditivity alone. This is only an economic condition, not a new supplier.

For actual raw-F targets, the displayed raw-generator word still produces J.
Conjugating each of the three targets by its tail reversal adds six half-width
calls. With c2>=c1=F_f, that particular wrapped recipe cannot beat three
direct F_f calls. Absorbing the reversals into existing layouts could change
the comparison, but requires a literal matched caller proof and bill.
Weighted F_A jobs also require the same actual weights and reversed pairing;
the unweighted S3 identity does not identify different ancestor-dependent
weight arrays across changing owner pairs.

## 4. Complex and funded-caller relevance

In the complex native ABI, recursive rank is the Fourier rank of an actual
Clifford transition. The selected `notes/general-clifford-frames.tex` defines
the physical transition ST^-1 and its preimage-frame intersection distance.
A nested rank-r transition becomes one C^(tensor r*f) child on one field,
between actual rank-zero adapters. Its group and exact phases differ from
the scalar-owner rank used in #5083.

Bare coordinate-CNOT or coordinate-SWAP address permutations are monomial
Clifford maps of Fourier rank zero. They are not the paid Gaussian rank-one
and rank-two jobs in the #4610 invoice. Actual native K_G lifts also include
quadratic phases; their binary permutation labels alone are not their exact
operators. Monomial movement and any BIT service they require remain charged;
rank zero does not mean a free fixed-tape implementation. Interpreting the
natural 2x2 GL2 matrices as scalar-owner ADDs instead would change the paid
alphabet again and would not create Gaussian rank.

No literal group of three eligible completed jobs with a bound subadditive
cap-two transaction was found in the declared #4610 complex source or the
selected BIT contracts. The closest BIT shapes are ordinary-swap adapters
and reversed/weighted whole-job targets just distinguished above. Turning
them into an occurrence requires actual chronology, identical weights,
adapters, changing pair layouts, all outputs and strict child contraction;
the present source reads do not provide that binding.
No chronological occurrence census was run; this is absence of a bound
occurrence in the inspected contracts, not a universal absence theorem.

The selected claim's admitted BIT saving is 17/5000=0.0034, whereas its complex
template and limiting main-transform saving are near 0.00302015. The frozen
#4610 round-six comparison remains near 0.0030217758 and explicitly retains
the same physical/whole-job/compiler hypotheses. A BIT-only local saving
therefore is not automatically an improvement of the binding complex moment
or the integer-multiplication kappa. No new P/T histogram is reported here.

## 5. Smallest useful next fixture, held for root authorization

Before any emitter or search, a prospective supplier should name one exact
Cap2(a,{0,1}) transaction at the same completed ABI, followed by the b version.
Use three active owner fields plus one arbitrary dirty spectator owner, with
the same three address chunks and a nontrivial untouched ROW field. Require
two independent transformed outputs, zero cross-owner leakage, and identity
on both other owners and every spectator. Record all entry/exit layouts,
copies, resets, buffers and charged recursive calls.

Width f=1 alone cannot distinguish internal atom reversal from an ordinary
swap. The smallest orientation-discriminating fixture uses f=2, unequal atoms
inside each chunk, and independent payload impulses in both selected owners
and the unselected dirty owners. An exact symbolic address-permutation or
operator identity at a permitted atom radix must accompany any finite fixture;
a small-radix test is only a type/orientation control, not admission of the
large-prime cover or all widths. Wrong pairing, reversed C_f convention,
discarded dirty input and accidental owner-sum delivery should each fail.

The decisive cost test is whether the supplier's complete transaction has a
justified price below the **actual** direct comparator, with the same logical
volumes, widths, weights and all outputs. Known two-stream packing does not.
If no source-bound subadditive supplier is provided, stop at this missing ABI
rather than relabel scalar rank as H2 or emit a hypothetical positive invoice.

No proposed physical fixture was executed. There was no author formal replay,
source change, compiler/Lean campaign, native emitter, public post or kappa
claim. This is a source-pinned feasibility handoff.

Credit Nick Petalas for #5083; David Arias, Ross Richardson, Adam Gall and the
retained group-cut/model lineage for its formal premises; the selected BIT,
native, row-cover, Clifford and compiler authors for their separate physical
contracts, including Cao Yifan, Cinna Davis, Dugongue, Jacob Sussman, eumemic
and predecessors. Prepared with substantial OpenAI Codex assistance;
Apache-2.0.
