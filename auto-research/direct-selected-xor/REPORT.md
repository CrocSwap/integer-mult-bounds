# Direct selected-bit XOR: a phase route and its recursive cost

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Operation-level diagnostic; no faster tape algorithm or new kappa.

## Outcome

There is an exact swap-free expression for the selected-bit addition using
two Hadamard layers and a pointwise sign. It works for arbitrary payloads,
either source order, and all spectator and temporary address values. It
requires no guard exception or dirty-control load/unload.

**This does not yet improve the running time.** Using the existing layer
algorithm as a black box retains its bit-network dependency. Closing the
recursion by replacing basis changes with this identity adds real recursive
children. A literal local replacement already exceeds the available rank
budget on the endpoint-correction class alone, even granting all other
basis changes for free.

We also give a local fusion that halves one implementation's added child
mass, from 32 to 16 units per endpoint. It remains unaffordable. A support
argument rules out fixing this particular local endpoint implementation
solely by a better word of coordinate kernels and diagonal phases at the
same full stream volume.

The missing ingredient is **sharing transforms across distinct residuals,
or an implementation with genuinely smaller child volumes**. This is a
precise new recurrence obligation, not an exclusion of operation-specific
algorithms in general. No larger construction search was started.

## Start with the actual consumer

The [compact-control movement routine](../../notes/compact-control-movement.tex)
implements x-before-y selected-bit additions through two target rotations
and two temporary updates. Each temporary update exchanges a front compact
field with a back field, performs a rotation and exchanges back. Its four
swaps restore the dirty temporaries and permit later-field streaming.

The desired complete action is simply

    (x,y,other addresses) -> (x,y XOR selected(x),other addresses).

The slots have selected positions rho+jK; all gaps and other address fields
must remain unchanged. Payloads are polynomial coefficient records, not
address bits available in random-access registers.

An existing [coded-carry audit](../../docs/research/coded-carry-audit.md)
already excludes sublinear-in-f implementations by a fixed-bank collection
of full-slot affine movements and masks, and by its fixed-order forward
rotation extension. We do not repeat that experiment. The phase proposal
below escapes that class by mixing payloads across selected coordinates,
but must pay for that mixing.

## Exact phase identity

Fix the source selected bits z=(z_1,...,z_f). Let W_y be the unnormalized
Walsh transform on the target's selected bits, independently for every
setting of all other coordinates. Let D multiply a payload at target
address y by

    (-1)^(sum_j z_j*y_j).

Then the required address-XOR permutation is

    P_XOR = 2^(-f) W_y D W_y.

Indeed its matrix entry from u to v is

    2^(-f) sum_t (-1)^(t.u + t.z + t.v),

which is one exactly when v=u+z over F2, and zero otherwise. This proves
the identity for every payload, not just an address simulation. Since all
other coordinates are fixed within the Walsh fibers, spectators and dirty
fields are restored automatically. The identity also handles a later
source because the sign calculation is pointwise, not a streaming rotation.

This is the standard character-conjugation identity, not a new algebraic
identity claimed by this project. The question here is whether it can be
used economically inside the present fixed-tape reduction.

The sign is computable from an address descriptor in polynomial time per
record. Under the retained long-record regime, this is a linear-volume
pass. **The Walsh transforms are not charged as linear-volume passes.**
They are the expensive operations whose implementation must be supplied.

If H0=W/2 on one coordinate, the identity is equivalently

    P_XOR = 2^f H0_y D H0_y.

The inherited H0=b S C S identity implements each H0 tensor by one C
tensor child and diagonal/scalar wrappers. Thus one selected-XOR on f
axes needs two C-tensor children of width f, on the same logical volume.
Their temporary work areas do not divide that volume by two.

For integer coefficient inputs, the unnormalized calculation grows by at
most f bits in each Walsh pass and divides exactly by 2^f at the end. For
dyadics, multiply through a common denominator to obtain the same identity.
This establishes a local O(f) guard allowance. A recursively redesigned
algorithm still needs its own dependency-depth precision proof; we do not
reuse the old permutation-only guard accounting for these arithmetic calls.

## Why the black-box version does not improve the exponent

The existing layer algorithm implements those Hadamard calls using compact
address operations, which in turn use the bit-interchange network. Calling
that algorithm here gives a valid way to express the selected XOR but does
not remove its dependency or improve its established movement exponent.

To seek a new algorithm, make the mutual recursion explicit. A residual
on mf axes uses basis changes made of selected row additions on f axes.
Each row addition can now recurse to two width-f C calls. The widths do
decrease, so this is not automatically an invalid circular definition.
But its contraction coefficient changes. If there are q charged row
additions at volume V/W, the added normalized linear rank mass is

    2q/(Wm).

Every wrapper, source/target order, padding obligation, and child volume
must fit this new recurrence. An algebraic identity by itself supplies
none of its contraction margin.

## A real fusion, and the remaining cost

Consider a rank-one directional kernel C_v=aI+bX_v in physical tensor
coordinates. Choose pivot p in the support of v, and let J contain its
other coordinates. Define the diagonal phase

    D=(-1)^(x_p sum_{j in J} x_j).

Let H_J be the normalized Walsh transform on J. The binary permutation
which adds x_p to each coordinate of J is H_J D H_J. Conjugating C_p
by it yields C_v. Since C_p commutes with H_J, adjacent Hadamards cancel:

    C_v = H_J D C_p D H_J.

Normalization is dyadic when the two Walsh transforms are combined.
The exact integer-pair checks verify the numerator 2C_v, so no numerical
square roots or tolerances are used.

For support weight w, replacing each of the 2(w-1) elementary row
additions separately would add 4(w-1) unit-width C calls. Fusion reduces
this to two transforms of width (w-1), plus the original width-one C_p
call: added rank mass 2(w-1). For f columns, multiply every width by f.
Even granting free packing of the coordinates in J, these are full-volume
children. This is a local algebraic improvement, not a supplied ordered
tape implementation of that favorable packing.

## Quantitative screen on the pinned complex network

The complex network shared by the selected copied-center certificate and
the PR82 research baseline has

    m=784, W=537696432, N=10732176,
    s=421548223824, Wm-s=5778864=(7/13)N.

Its endpoint correction has N rank-one calls, at volume V/W. In the
literal standard tensor coordinates their direction is the tensor product
of two triple indicators, of weight nine.

Keep all other existing C children and grant every other basis operation
for free. Replacing just these endpoint calls gives:

| Replacement | Added rank mass | Total normalized mass at exponent one |
| --- | ---: | ---: |
| Hypothetical one extra unit child per endpoint | N | 1.00001175012 |
| Coordinate-mobility lower bound below | 8N | 1.00018996035 |
| Fused Hadamard construction | 16N | 1.00039362917 |
| Separately compiled row additions | 32N | 1.00080096682 |

All entries are exact rational comparisons in the certificate. Since the
moment increases as the desired exponent falls below one, failure already
at one rules out a sublinear recurrence for these substitutions.

This is a scoped test of **local standard-coordinate endpoint replacement**.
It does not assert that every common-basis implementation incurs these
charges. Moving to another basis may make an endpoint coordinate, but that
transport must then be charged or shared elsewhere. A global choice that
changes costs across residual boundaries requires a new joint ledger and
lies outside this local rejection.

### Coordinate-mobility lower bound

Allow arbitrary diagonal phases, pointwise payload operations/copies, and
coordinate tensor-kernel calls on one complete endpoint stream. A coordinate
never touched by a kernel cannot change along any input/output support path.
But C_v has a nonzero matrix entry between x and x+v, changing every bit in
the support of v. Across f columns, all wf coordinates must therefore be
touched. The sum of coordinate child widths is at least wf.

Compared with the original rank-one width-f call, that is at least (w-1)f
extra mass, or 8N over the endpoint class. This argument survives arbitrary
diagonal cancellations. It assumes each local child acts on the complete
original endpoint volume; new row splitting with smaller child volumes,
cross-residual sharing, or a child that is itself a noncoordinate primitive
is outside its scope.

## What this establishes and what remains open

We have an exact composite operation eliminating explicit swaps and dirty
controls, plus a real cancellation between its transform wrappers. We do
not have a faster implementation. The new computation is more than an
address permutation internally, and its recursive costs consume the saved
network rank many times over in the literal replacement.

Do not expand into a search for shorter isolated coordinate-kernel words
for these endpoint maps. The local mobility bound already prevents that
from rescuing this ledger. A meaningful continuation would need one of:

* A complete segment spanning several residuals and scalar gates whose
  transforms cancel or can be reused, with entry and exit costs charged.
* A concrete new smaller-volume recursion for the selected-XOR operation.

Neither is supplied here. The former is the sharper next question suggested
by this experiment: can the local Hadamard cancellation extend across a
real circuit boundary? That would change an assumption of the rejection.
We have not established that such an extension is possible or beneficial.
The separate complex-network saving required for the 2^-9 target also
remains unmet; bypassing the bit primitive alone would not certify it.

## Verification

```sh
python3 research/direct-selected-xor/audit.py --output research/direct-selected-xor/certificate.json
python3 -m unittest discover -s research/direct-selected-xor -p 'test_*.py' -v
```

Exact tests cover every basis payload on small complete address sets,
both source orders, spectator coordinates, a separate character-sum Walsh
implementation, normalization, the fused directional identity, support
mobility, and pinned rational cost arithmetic. These do not simulate a new
fixed-tape algorithm. `validation.json` records the runs and preservation
of the previous research and published certificates.
