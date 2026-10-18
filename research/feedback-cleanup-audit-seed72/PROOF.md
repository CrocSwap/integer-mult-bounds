# Target feedback and projected cleanup

This audit concerns a proposed relaxation of the scalar interface in
PR543, retained by selected PR589. The actual lemma excludes targets as
inputs to source/helper gates in H1 and repeats this exclusion in H3's
description of B. It assumes a literal reverse of those z-destination
gates for cleanup. The source theorem under those hypotheses is not
challenged here.

The proposed relaxation permits target feedback in both H1 and H3 but
asks only that the raw word's z endpoint be independent of targets.
We retain the *scalar* projected-reverse rule. We do not retain or prove
the full-frame legality conclusion: a target read during cleanup may
be illegal in the original frame model. No toy program below is asserted
to be a legal physical E8 word.

## Exact criterion in arbitrary scalar dimensions

All matrices in this section are over F2. Order the coordinates as
`(z,y)`, where z contains sources x followed by helper dirt. Let L select
the desired source contribution to the targets. Let the preliminary
shear D be `y += N z`, with N supported on helpers for the original H2.
Allow the raw word and its prescribed cleanup to have blocks

```text
R = [ U V ]       C = [ P Q ]       D = [ I 0 ]
    [ J K ]           [ 0 I ]           [ N I ].
```

Cleanup fixes targets because it uses only z-destination gates. Its Q
block need not vanish if target feedback was allowed. The desired full
map is `S = [I 0; L I]`. Direct multiplication gives

```text
C R D = [ PU+QJ+(PV+QK)N    PV+QK ]
        [ J+KN                 K ].
```

Consequently **C R D = S if and only if**

```text
K = I,
J + N = L,
PV + Q = 0,
PU + QJ = I.
```

Necessity follows first from the bottom-right block K=I, then from the
bottom-left and top-right blocks; the extra N term then vanishes in the
top-left block. The same calculation proves sufficiency. This is a
block identity, not a finite-sampling argument. The checker independently
compares the criterion with complete matrix composition throughout the
finite three-wire class and on all selected-word input columns.

Under the original target exclusion, V=Q=0 and the projected forward
z product is U. Reversing the involutive z gates makes P=U^-1, so the
two upper-block conditions hold automatically. The original scalar
lemma's remaining J/K/helper cancellation conditions are recovered.
Without exclusion, raw V=0 alone implies neither Q=0 nor PU=I. It
does not identify the raw z block with the product of the z gates
considered in isolation.

## Sharp three-ADD counterexample

Use wires `(x,h,y)`, one arbitrary helper h, no preliminary D and no
COPY/ERASE. Execute the raw word

```text
h += y
y += x
h += y
```

Its raw endpoint is `(x,h+x,y+x)`. Thus the z endpoint has no dependence
on y, the target-to-target block is identity, and the desired target
source transfer is exact. The raw z block is invertible. The prescribed
projected cleanup reverses the two h-destination gates:

```text
h += y
h += y
```

They cancel, leaving `(x,h+x,y+x)` instead of `(x,h,y+x)`. In particular,
input `(1,0,0)` leaves h=1. The two cleanup ADDs are included: the literal
five-ADD complete program fails; there is no hidden free restoration.
This is an actual counterexample to the proposed weakened premise,
not a failed search or an error in the source's stated theorem.

The first and second upper-block conditions are independently needed.
The receipt also supplies a six-ADD raw witness whose complete map is
`(x,h+y,y+x)`: it satisfies `PU+QJ=I` and both target conditions, but
violates `PV+Q=0`. The three-ADD witness satisfies `PV+Q=0` and both
target conditions, but violates `PU+QJ=I`.

## Complete finite quotient, including arbitrary word lengths

The precise census class is every finite word in the six scalar gates
`wire_d += wire_s` for distinct d,s in `{x,h,y}`, followed by the literal
reverse of its z-destination gates. N=0 and L=(1,0) are fixed. This
class is broader than legal source frame schedules.

For a raw prefix record `(R,Z)`, where R is its full 3-by-3 transfer and
Z is the product obtained by deleting y-destination gates. R lies in
GL(3,2), which has 168 elements. Z fixes y and belongs to the 24-element
subgroup `H={ [A b; 0 1] : A in GL(2,2), b in F2^2 }`.
The prescribed cleanup matrix is exactly Z^-1. For an appended gate g,
R becomes gR; Z becomes gZ for a z destination and stays Z otherwise.
Therefore this pair is a sufficient state for both future evolution and
the complete cleanup result. Two words with the same pair are equivalent
for the audited property, regardless of their lengths.

The checker enumerates GL(3,2) independently by its bijective action on
the eight input vectors, then breadth-first explores this pair transition
system. It reaches **all 168*24=4,032 possible pairs**, expanding all
**24,192 directed transitions**, without a depth cutoff. Diameter is 10.
The layer sizes are
`1,6,24,69,182,438,907,1274,906,219,6`.
The recorded distance-table hash binds every ordered pair and its
distance; replay reconstructs them. Thus the census is complete for the
stated three-wire arbitrary-length class, not a claim about larger words
or arbitrary physical circuits.

Exactly six raw matrices have `V=0`, `K=1`, and `J=(1,0)`: their U block
is any element of GL(2,2). Each can coexist with all 24 projected products,
so **144 states** pass the proposed endpoint premise. For each such R,
exact restoration fixes one and only one Z, namely `Z=R S^-1`, which is
`diag(U,1)`. Hence exactly **6 restore and 138 fail**. This count follows
also algebraically, independently of checking individual matrix outputs.
Among those 144 states the upper-block pass/fail pairs have counts
`(pass,pass):6`, `(pass,fail):30`, `(fail,pass):6`, `(fail,fail):102`.

Breadth-first distance gives the smallest raw failing length as three.
A separate literal enumeration checks all `1+6+36=43` programs of length
zero through two, without quotienting, and finds no counterexample.
For every quotient representative, direct bit updates on all eight
assignments check the raw word, cleanup and full program against the
matrix calculation. These 32,256 complete input assignments provide a
second implementation of the finite semantics.

Target exclusion is sufficient, not necessary for scalar restoration:
two adjacent identical feedback gates cancel, a following `y += x` gives
the desired target shear, and their projected cleanup also cancels.
That positive control prevents interpreting this note as
a prohibition of every feedback program.

## Selected source binding and limitations

The unchanged PR589 word selected at the frozen experiment base has
111 sources, 439 helpers and 111
targets. Independent bitset replay checks all 661 input columns, with
z dimension 550. The actual D, raw A/scatter/B and C blocks satisfy all
four equations; target exclusion and the grouped literal cleanup agree
with the source contract. All 24,305 ADDs are included. Stream composition
is compared with independent block multiplication. Scalar scatter reads
the retained register directly; this audit does not re-establish its
physical COPY/ERASE realization.

The original source's frame, lattice, label, COPY-rank, precision, native
multistage, physical hosting, and outer assembly checks are outside this
baseline replay. No new physical construction, supplier allowance or
kappa follows. This clarifies a necessary interface boundary for future
target-feedback proposals while preserving the selected construction.
