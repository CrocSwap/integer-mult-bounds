# Three rank-five endpoints after a common cut of 45

Use the P112 root/label model of Nick Petalas's retained root-simplex package.
Its 112 live root lines have nine-bit labels. The full E8 configuration has
120 lines. Let `K` be any characteristic-zero field and let

```
C = { (r_t dot h)_t : h in K^8 }.
```

For a common set `S` of live coordinates, let `pi_S` delete `S`. Binary
support rank means the F2 rank of the labels with nonzero coefficients.

**Theorem.** For `|S| <= 45` and three pieces whose supports outside `S`
have binary rank at most five,

```
dim_K(pi_S(C) intersect span_K(pi_S(q_1), pi_S(q_2), pi_S(q_3))) <= 1.
```

The pieces may be dependent and their coefficients arbitrary. This increases
PR3249's sufficient common-support threshold from 44 to 45. It does not prove
sharpness, exclude a named historical TWOSIDE profile, or supply a decoder,
physical supplier or improved kappa.

## Inherited premises and their exact source

PR3249 at `22c7bf316d55e59f381cc9ba833afccc7702fd58`, `PROOF.md`
and `RESULT.json`, supplies these premises in the same model.

- A binary-rank-five subset of P112 has at most 12 labels.
- A root subsystem of rank at most six with more than 30 lines is E6.
  Its normal plane is A2. This uses the standard real Weyl-chamber theorem.
- Every A2 root plane has a nonzero evaluation union of at least 78 live
  P112 coordinates. All A2 planes form one Weyl orbit.
- Full E8 projective evaluation fibers in an A2 plane have nonzero sizes
  `27,27,27,1,1,1`. Each 27-line fiber spans seven binary dimensions.
  Its binary-rank-five subsets have size at most 10.

The retained-source pins authenticate those exact source bytes. The present replay
rechecks the last capacity and adds the closure premise below. It does not
rerun the 3,309,747 P112 five-flats, the A2 orbit/union census, or the parabolic
inventory. Those mathematical premises remain inherited pending dependencies,
not newly admitted results. No proof-kernel or independent human review is
claimed.

## The new finite premise

**Ten-singleton closure.** If ten labels in one full E8 projective A2 fiber
have binary rank at most five, they span a five-space containing exactly
those ten full E8 root labels.

For one fixed A2 plane, `verify.py` enumerates all 2,667 codimension-two
subspaces of each 27-line fiber's seven-dimensional binary span. Exactly 216
per fiber contain ten fiber labels. In every case those ten span five
dimensions and their span contains exactly ten of ALL 120 E8 root labels.
The receipt records the complete fiber-intersection histograms and hashes of
all 648 tight five-spaces. It also gives a literal ten-label witness per fiber.

Completeness follows because any rank-at-most-five subset of a seven-space
extends to a five-space. A ten-label subset cannot gain further fiber labels
on extension because the fiber capacity is 10. The census checks that every
such ten-label intersection already has rank five.

`crosscheck.py` reconstructs roots and labels independently. It enumerates
all 80,730 five-label subsets per fiber, reduces their bases by a different
algorithm and checks the full-E8 closures. Every rank-five ten-label subset
has a five-label basis, so this independently covers every tight case. The
complete tight-five-space hashes agree with the primary enumeration.

A Weyl reflection acts invertibly on simple-root coordinates modulo two,
leaving the leading label bit fixed. It preserves binary spans and permutes
all 120 E8 root labels. Inherited A2 Weyl transitivity therefore transports
the new closure premise to every A2 plane. Removing frame lines only removes
available support labels. The full-E8 closure statement is essential here.

## Any putative two-dimensional code is still A2 at 45

Suppose the displayed intersection has dimension at least two. Choose lifts
`h,k` of two independent restricted codewords. Their union `U` of full
supports lies in `S` together with the three residual piece supports. Thus

```
|U| <= 45 + 3*12 = 81.
```

At least 31 live root lines are perpendicular to both directions. Their
rational span has rank at most six, since its rational matrix has two
independent kernel vectors over `K`. Rational matrix rank is unchanged by a
characteristic-zero field extension.

As in PR3249's chamber argument, the full subsystem of perpendicular E8 roots
is conjugate to a parabolic subsystem. More than 30 lines force type E6, with
two-dimensional normal plane A2. Consequently the span of `h,k` is the scalar
extension of that plane. Replacing the basis by a rational root basis leaves
`U` unchanged and gives `|U| >= 78` by the inherited union bound.

## The incidence equality cannot occur

Express the two restricted codewords by a fixed 2-by-3 coefficient matrix in
the three pieces. At a singleton site, exactly one piece is nonzero, so the
evaluation pair is proportional to that piece's coefficient column. Hence
the singleton sites of one piece lie in one projective A2 fiber. A zero
column admits no singleton site.

Let `N = |U minus S|`, let `m_i` count the incidences of piece `i` there, and
let `l_i` count its singleton sites. The inherited capacities give
`m_i <= 12` and `l_i <= 10`.

If `l_i = 10`, the new closure premise shows that those singleton labels
already span five dimensions and contain every full E8 root label in that
span. The piece's entire residual support has rank at most five, so its
support is contained in those ten labels. Thus `m_i <= 10`.

Therefore `m_i+l_i <= 21`: when `l_i <= 9`, use `12+9`; when `l_i = 10`,
use `10+10`. Counting each nonsingleton site at least twice gives

```
66 <= 2*(78-45) <= 2*N <= sum_i(m_i+l_i) <= 3*21 = 63,
```

a contradiction. Incidences outside `U` only reduce the available budget;
dependent pieces, nonmodal shifts and cancellations require no extra premise.

## Boundary and remaining obligations

At 46, the raw support bound leaves only 30 guaranteed perpendicular live
roots, so it no longer forces the E6/A2 normalization. The present result
makes no statement there. A stronger A2 incidence budget alone cannot justify
extending the uniform threshold without checking that normalization branch.

The standard Weyl-chamber theorem, inherited finite premises and any actual
caller's common-support/rank hypotheses remain explicit dependencies. No
historical caller census, complete C5 argument, decoder floor, supplier,
all-size multiplication theorem or selected-frontier change follows here.

Credit Nick Petalas/PR3249 and the root-simplex lineage, DreamingOfClouds/PR3154,
and the retained E8/P112 sources including joaqcoo. Frozen predecessors are
unchanged.
