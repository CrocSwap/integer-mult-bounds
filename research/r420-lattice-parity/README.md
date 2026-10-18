# selected r420 frames in the intrinsic lattice quotient

**independent finite verification; no new kappa.** this package certifies the
120 selected #543 root labels in the lattice quotient `L/2L`, where `L` is
their even unimodular lattice with metric `dot/2`. the labels correspond
bijectively to the 120 classes with quadratic value one.

all 672 selected frame spans keep their dimensions in this quotient, but
**300 frames gain root incidences: 480 extra memberships in total**. each
extra has an explicit integral lift proving membership modulo `2L`, and
independent witnesses proving nonmembership in the rational frame. this
refutes extending the rational closure statement to intrinsic binary spans.
it is not a defect in the supplier, which does not make that extension.

## reproduce

python 3.10+; standard library only; offline, from the repository root:

```sh
python3 -I -B research/r420-lattice-parity/verify.py
```

expected:

```text
pass_r420_lattice_parity: 120 anisotropic classes; 672 frames; 300 changed closures; 480 extra memberships; 11 rejected controls
```

the command checks the source pins, reconstructs the lattice coordinates,
checks the quadratic identities, recomputes every frame's binary span and
every lift, runs eleven mathematical controls, and compares the entire
`EXPECTED.json`. it makes no writes. `--write NEW_PATH` writes a fully checked
certificate and refuses overwrite. `--source-root PATH` supports relocation.
all checks remain enabled under python `-O`.

```sh
python3 -I -O -B research/r420-lattice-parity/test_verify.py
```

expected: six passing test groups. [VALIDATION.md](VALIDATION.md) records the
independent dual-coordinate, determinant and direct-coordinate checks.

## complete finite census

all indices below are zero-based. "parity roots" counts supplied root classes
in the binary span of the declared frame's classes.

| rational dimension | binary dimension | rational roots | parity roots | frames |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 1 |
| 1 | 1 | 1 | 1 | 120 |
| 2 | 2 | 2 | 2 | 180 |
| 4 | 4 | 12 | 12 | 70 |
| 6 | 6 | 30 | 32 | 180 |
| 7 | 7 | 63 | 64 | 120 |
| 8 | 8 | 120 | 120 | 1 |

the extra roots are exactly the rational orthogonal-complement roots for
every changed frame. this description is checked only for those 300 frames;
it is not asserted for the other dimensions.

coverage is exhaustive for the pinned input: 256 quotient classes, all 65,536
polarization pairs, all 14,400 root pairings, all 672 frames and all 80,640
frame/root memberships. there is no adaptive search or early-success cutoff.

the source's displayed integer coordinates reduced modulo two give only
**15 distinct root residues**, with all eight doubled coordinate axes mapping
to zero. they are not coordinates on `L/2L`. the intrinsic encoding instead
gives 120 distinct nonzero classes. matching a rational rank alone also does
not guarantee matching root incidences, as the dimension-six and seven rows
show.

## an explicit witness

the verified lattice basis consists of root labels
`b = [76,77,78,80,81,84,88,96]`, with coordinate determinant `-16` and gram
determinant one. let `r_i` denote supplied root label `i`.

frame 362 has 30 rational roots and dimension six. it acquires classes 5 and
6 in the binary quotient. its first lift is

```text
r_76 + r_78 + r_0 + r_1 - r_5
    = 2 (b_1 + b_2 + b_4 + b_6 - b_7).
```

the four subset labels lie in frame 362, so `[r_5]` belongs to its binary
span. `r_5` is nonzero and orthogonal to every rational frame generator; hence
it cannot lie in their real or rational span. the certificate also records
the nonzero augmented minor `(coordinate mask 191, value 64)`.

`EXPECTED.json` gives the same two kinds of witnesses for all 480 extra
memberships. each frame occupies one line, with its rational basis, both
dimensions, binary membership bit mask, and the extra-root lifts. bit `i`
of a membership mask denotes root label `i`. coordinate masks for minors use
increasing coordinate order.

## why the certificate suffices

### lattice and exact coordinates

let `c` be the binary span of the displayed integer root coordinates. explicit
enumeration checks that `c` is self-dual, doubly even, and has weight enumerator
`1 + 14 t^4 + t^8`. the roots contain every doubled coordinate axis and generate
`c` modulo two. their integer span is therefore exactly
`L = {z in Z^8 : z mod 2 is in c}`: lift a codeword by an integer root
combination, then correct the remaining even vector with the doubled axes.

the metric `dot/2` is integral by self-duality and even by double evenness.
the coordinate index is `2^8/16 = 16`, giving lattice gram determinant
`16^2 / 2^8 = 1`. enumerating the signed doubled axes and the signed four-unit
vectors with residue in `c` gives exactly 240 norm-two vectors, equal to the
120 supplied root lines up to sign. no lattice classification is required.

integer exterior products nominate a basis using root order `(i-76) mod 120`.
its determinant is checked to have magnitude 16, so its sublattice has the
same index as `L` and is a lattice basis. cofactors give each root's exact
integral coordinates; every reconstruction is checked by integer matrix
multiplication. the seed-nominated basis is verified for this frozen label
order, not assumed primitive for every ordering. a different ordering can
fail closed at the basis-index check; this is not a general basis finder.

### the quadratic quotient

for `x` in the even lattice, define

```text
q([x]) = <x,x>/2 mod 2 = dot(x,x)/4 mod 2,
b([x],[y]) = <x,y> mod 2.
```

these are well-defined modulo `2L`: replacing `x` by `x+2z` changes its
half-norm by `2<x,z> + 2<z,z>`, an even integer. the polar form has an
invertible matrix modulo two because the integral gram determinant is one.

the checker evaluates `q` on all 256 lattice-basis representatives directly
from their original coordinate norms and also from the gram polynomial. it
checks all polarization identities `q(a+b)+q(a)+q(b)=b(a,b)` and all root
pairings against the original integer dot products. exactly 136 classes have
value zero and 120 have value one. the 120 root classes are distinct, nonzero,
and exactly that latter set. these familiar e8 facts are not claimed new.

### complete frame membership and the lifts

enumerate the binary span of each frame's intrinsic root classes, carrying a
subset of its labels as a witness for every class. compare the span with all
120 root classes. for an extra label `i`, the stored integral basis coordinates
`z` verify

```text
sum_{s in subset} r_s - r_i = 2 sum_j z_j b_j.
```

this is an exact membership witness in `L/2L`. a nonzero exterior minor proves
rational nonmembership. the separate test implementation additionally checks
the lift in the original coordinates and proves nonmembership by positive
norm and orthogonality, without using that minor. all other labels are tested
too; the certificate is a complete census rather than just example witnesses.

## relation to existing and concurrent work

the accepted #543 checker already verifies the rational root geometry.
eumemic's existing p111 `discovery/choose.py` and construction note already use
classes in `E8/2E8` for decoder affine rank. this package does not claim that
idea. it supplies an independent construction-a/lattice-coordinate certificate
and the complete characteristic-two closure census for the selected r420
frames, with explicit witnesses for the 480 added incidences.

concurrent [#737](https://github.com/CrocSwap/integer-mult-bounds/pull/737), by
sagar thakrar, independently covers exterior frame geometry and odd-prime
witnesses. its inspected head is `b41e73169430641be18c988c659d2855a6a6218a`.
when it appeared, the initial overlapping exterior-only package from this
session was retired before submission. this package instead checks the
intrinsic characteristic-two quotient and its changed incidence sets. #737
is credited, not imported or alleged incorrect; its odd-prime statement does
not cover this quotient. [CLAIM.md](CLAIM.md) records the single scoped pivot.

## pins, attribution and limits

base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
#543 supplier: `2065fe4f72a914d907f1046603f5a36f17018535`.
selected consuming #626: `660de893d27bb7abd1d5b01b1640207528a5c851`.
conditional project kappa remains `51110230636731/31250000000000000`.
`SOURCES.json` records file hashes and the distinct concurrent work.

no production program or selected record changes. this is a finite exact
certificate with a written elementary argument, not a proof-assistant theorem.
it does not replace frame geometry with binary spans, construct a decoder,
price an implementation, or discharge mutable-basis/common-label realization,
all-size compilation, hosting, precision/tape/recovery or analytic obligations.

credit to eumemic (#543, p111 and earlier carrier work), dylan crow (bitE8
format/checker), jacob sussman (e8 unit), dreamingofclouds (totals and pricing),
and the contributors retained in the pinned notices. the consuming complex
construction retains jeremy kothe and chafik boukhalfa's credit. classical
lattice, quadratic-form and exterior methods are not claimed as new theory.

prepared by gojo (@6ojo), with substantial openai codex assistance, under
apache-2.0. "independent" describes the arithmetic implementation, not
independent human review.
