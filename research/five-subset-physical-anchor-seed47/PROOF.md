# An output anchor replaces the frozen dirty-helper station

This is a finite Gaussian-dyadic array construction and a complete comparison
in the declared read/restore model. It is not a new multiplication exponent,
an optimal circuit, or adoption into the monotone supplier interface.

## Fixed object and logical identity

Retain PR1230's six weight-five source labels
`[31,55,457,458,481,482]` and six target labels `[47,59,87,151,279,451]`.
Its signed kernel is `K(s,t)=Re(i^popcount(s&t))=alpha_s beta_t`, where
`alpha=[1,1,-1,-1,-1,-1]` and `beta=[1,1,1,1,1,-1]`.
This package includes the historical factor one-half: the desired update is

    y_j += (beta_j/2) sum_i alpha_i x_i.

Every input and output array can contain arbitrary dirt. For an output anchor p,
perform, in order:

1. `y_j -= beta_j beta_p y_p` for the five j different from p.
2. `y_p += (beta_p alpha_i/2) x_i` for all six i.
3. `y_j += beta_j beta_p y_p` for those five j.

The old value of y_p cancels. Since beta_p squared equals one, every output
receives its prescribed update, the sources are unchanged and no array helper
is used. This standard accumulator identity takes sixteen ADDs and six dyadic
half-scalings. No novelty or optimality is asserted for the generic identity.

The comparator is the actual frozen four-pass helper schedule: six gathers,
six half-scaled scatters, six ungathers and six old-helper corrections. It takes
24 ADDs and twelve half-scalings. It restores arbitrary helper dirt. Both words
include the same thirteenth role at the physical boundary, so the unused helper
in the anchor word still pays its terminal Fourier operation.

## Actual operators and query lowering

Arrays have 512 complex entries indexed by F2^9. Let X_v translate addresses by v
and define the exact Clifford quarter transform

    C_v = ((1+i)/2) I + ((1-i)/2) X_v.

Its Walsh-character eigenvalue is `i^(v dot k)` and `C_v^2=X_v` exactly.
Let `F=product C_ei` on the nine coordinate directions. A source's live gauge is
C_s. A target's live gauge is F C_t inverse. The helper gauge is the product of
C_v over a fixed orthonormal basis of the nondegenerate U4 from PR1230.
These are exact representatives, not merely binary frame labels. General frame
geometry and the preimage convention are inherited from icekylinx's
`notes/general-clifford-frames.tex`.

For each logical ADD, borrow its source temporarily, apply `T_dst T_src^-1`,
perform the ADD in the common physical gauge, then apply the exact inverse to
that source. The source is returned before the next logical gate. This is an
explicit caller contract: intermediate source observations are forbidden.
The word permits frame descents; it does not satisfy the selected monotone
supplier contract just because the source is restored at query return.

Each transition is lowered into a binary address permutation, one coordinate
`C^(tensor r)` child, the inverse permutation, and any required Pauli translation.
All 512 character phases of every recipe are checked. The child directions are
independent; they need not be orthonormal for a general address adapter.
In particular, two target labels can have odd mutual dot product. Requiring
their two directions to be orthonormal would improperly exclude this lowering.
The binary B block of such a recipe is the sum of the direction outer products;
its rank r is recomputed independently.

An inverse child is not free and is not an assumed second provider:
`C_r^-1=X_first-r C_r`. The executable forward and normalized inverse words use
only forward children and explicitly pay this extra translation. PROGRAMS.json
lists the forward permutations, translations, scalar gates, source reads, births
and final tails. The verifiers deterministically reverse and normalize that stream
to obtain the inverse; its distinct invoice is saved in both receipts. No array
COPY, ERASE or clean-array initialization occurs.

All thirteen arrays start at the raw identity gauge. Six source births have
rank one and six target births rank eight. Their tails have ranks eight and
one respectively. The comparator helper has a rank-four birth and rank-five
tail; the unused anchor helper receives one rank-nine F. The complete endpoint
in both cases is F on every role after the logical K/2 shear. The inverse is
F inverse on every role after the negative shear. This common boundary is a
chosen finite-array experiment, not an already-instantiated global Side caller.

## Complete costs and uniform moment comparison

Helper queries have residual ranks three and four. Both calls inside each query
are paid: the core is `24 H3 +24 H4`. Source/output boundary work and the helper
birth/tail give the complete comparator profile

    12 H1 +24 H3 +25 H4 +H5 +12 H8, mass285, 74 children.

An anchor has six rank-seven source-to-target queries and ten rank-two
inter-target queries. Its complete profile on the same thirteen roles is

    12 H1 +20 H2 +12 H7 +12 H8 +H9, mass241, 57 children.

The difference of complete moments, with p=1-a, is

    12(3^p+4^p-7^p) +(4^p+5^p-9^p)
    +12*3^p+12*4^p-20*2^p.

For 0<=p<=1, subadditivity makes the first two brackets nonnegative. The last
line is at least `4*2^p>0`. Thus the anchor has a strictly smaller complete
child moment throughout that interval, under this explicit interface.

The separately counted forward rank-zero complex-value copies decrease
133836 to104836 for the seed-selected anchor5. The normalized inverse has
190668 to148612 copies; its extra inverse translations are not omitted.
Forward permutations/translations are148/73 versus114/60; inverse values are
148/147 versus114/117. Exact AXPY value accesses decrease36864 to24576 and
half-scalings per address decrease6144 to3072. RESULT.json records the address-XOR
upper bounds and both direction invoices, rather than treating adapters as free.

One in-place permutation cycle of length l>1 uses l+1 complex-value copies
with one machine-scalar temporary. The address routines also require512 visited
bits, fixed permutation tables and program metadata. These are private machine
work, not a zeroed array carrier. Interface counts exclude the internal service
implementation of CHILD, tape routing, rounded arithmetic and global controller
setup. They are not a runtime benchmark or an all-size storage theorem.

The complete normalized main bill is still noncontracting. For a>=0 and r<=9,
`(r/9)^(1-a)>=r/9`, so the new bill is at least `241/9>13`. In particular it
exceeds the thirteen-role reference mass117 already at a=0. The rank-nine child
is equal-sized, another reason this finite word is not a contracting recursion.
With the unused helper omitted, the corresponding twelve-role mass232 still
exceeds108. Scalar and moment improvements here cannot supply a new kappa.

## Coverage and exact finite evidence

The declared experiment is exactly the comparator plus all six fixed output
anchors. Seed47 selects p=47 modulo6=5; no labels, stations or frame schedules
are searched beyond those seven programs. Every anchor has the same complete
endpoint and child profile. There is no global or neighborhood optimality claim.

The primary checker executes spatial Gaussian integer-pair coefficients divided
by powers of two. At completed recipe cuts, each thirteen-by-thirteen array
block is circulant. During a recipe, its active block row is a common left
permutation of circulant blocks: a partial coordinate child before the final
permutation is conjugate to translation-circulant quarter factors. Therefore
thirteen origin-impulse kernels determine all6656 raw input columns. The sum
of absolute real and imaginary coefficients is uniform over output addresses,
so those kernels also give the exact component-row-l1 peak. Both directions
attain128, including the explicitly expanded coordinate child subfactors.
Internal states of a separately implemented recursive CHILD service are not
covered by that128 statement.

The independent checker uses inverse-transpose character permutations and exact
fourth-root phases, checks every actual recipe on all512 characters, recomputes
B ranks and current-gauge chronology, and checks all13 input columns in every
character in both directions. Its separate logical schedule has the same
physical endpoint. Primary semantic controls include omitted compensation,
wrong half-scaling, missing Pauli adapters and a clean-source-only test that
misses an old-helper error. Actual corrupted-file tests exercise the CLI.
Finite replays support the written identities; they are not formal verification
of integer multiplication or independent human review.

Global label coverage, a compatible selected caller, common-label/mutable-source
realization, monotone hosting, compiler/tape/precision and analytic transfer remain
uninstantiated. The selected E8 sources and frontier are untouched. The rejected
global ParitySide DAG is not reopened.
