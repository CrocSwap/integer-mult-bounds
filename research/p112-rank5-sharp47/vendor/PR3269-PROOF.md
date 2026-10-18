# Analytic binary-support capacities for E8 and P112

Let `s_0,...,s_7` be the doubled simple roots in the pinned
`research/p112-root-simplex-exclusion/geometry.py`. A root line has integral
simple-root coordinates `c_i`. Its declared nine-bit label is

```
ell(r) = (1, c_0 mod 2, ..., c_7 mod 2).
```

The leading coordinate is the low bit in the executable convention. The
full 120-line labels here extend this same formula. On the 112 nonframe
lines they agree exactly, in order, with the existing `root_data()` labels.
This is the rank notion used by that source's `flat_capacity(labels, d)`.
The theorem does not assume that an unrelated physical port encoding uses
the same rank notion.

**Theorem.** Any set of these full E8 labels with binary rank at most five
has at most 12 elements. At binary rank at most six it has at most 20.
Both bounds are attained on the fixed P112 subset. In particular these
are analytic replacements for the global five-/six-flat upper bounds
used by PR3249, PR3255 and PR3260, without replaying their large censuses.

This concerns support cardinality. It establishes no new shortening
threshold, caller exclusion, decoder floor, physical supplier or kappa.

## Bind the precise quadratic model

Write `G_ij = <s_i,s_j>/4`, the integral E8 Cartan Gram matrix, with
diagonal two. On `V=F2^8` define

```
q(x) = sum_i x_i + sum_(i<j) G_ij x_i x_j  mod 2.
B(x,y) = q(x+y) + q(x) + q(y).
```

The doubled norm gives `q(c mod 2) = ||sum c_i s_i||^2 / 8 mod 2`.
All root residues therefore have value one. The replay checks their
distinctness, the equality between all 120 residues and all `q=1`
vectors, and every one of the 112 existing live labels. It checks that
the polar matrix is nonsingular and that

```
sum_(x in V) (-1)^q(x) = 256 - 2*120 = 16.
```

Thus the sign and dimension of the quadratic space are established on the
actual declared labels. Calling the form plus type is shorthand for this
positive character sum, not an extra classification assumption. All
65,536 polarization pairs are checked. The separate checker reconstructs
the roots and integral coordinates independently, evaluates `q` using
integer vector norms, and uses dense binary elimination.

For a nonempty support, let `W` be its nine-bit linear span, of dimension
at most `d`. Intersect `W` with the leading-one hyperplane. Forgetting
that fixed bit identifies the intersection with an affine subspace
`a+L` of `V` of dimension at most `d-1`. This follows by rank-nullity for
the nonzero leading-coordinate functional on `W`. The residue map is
injective on the roots, so the support size is at most the number of
`q=1` points in `a+L`. Extend smaller affine spaces to dimension four or
five respectively; extension cannot reduce that count. It remains to
bound affine four- and five-spaces.

## A character-sum lemma with the sign retained

Let `k=dim L`, and let the alternating polar restriction to `L` have
rank `2r`. Its radical is `R=L intersect L^perp`, of dimension
`t=k-2r`. Since `B` is nonsingular on `V`,

```
t <= 8-k.
```

Put `f(x)=q(a+x)` for `x in L`, and
`S=sum_(x in L) (-1)^f(x)`. The number of value-one points is
`(2^k-S)/2`. With `h=x+y`, polarization gives

```
S^2 = sum_(h in L) (-1)^(q(h)+B(a,h))
                    sum_(x in L) (-1)^B(x,h)
    = 2^k sum_(h in R) (-1)^(q(h)+B(a,h)).
```

On `R`, `h -> q(h)+B(a,h)` is linear. If it is nonzero, the last
sum is zero, so `S=0` and exactly half the affine space has value one.
If it is zero, `S^2=2^(k+t)`, hence

```
|S| = 2^(k-r).
```

This gives the usual unsigned upper bound
`2^(k-1)+2^(k-r-1)`. The exceptional cases below require the sign.

Suppose `k+t=8` and the radical character is zero. Then
`L=R^perp`. Define `q_a(x)=q(x)+B(a,x)`. It vanishes on `R`.
On any coset `x+R` outside `R^perp`, its signed sum is zero because
`B(x,.)` is a nonzero linear functional on `R`. Therefore

```
sum_(x in V) (-1)^q_a(x) = sum_(x in L) (-1)^q_a(x).
```

Translation by `a` gives the left side as
`(-1)^q(a) sum_V (-1)^q(x)`. Multiplying by `(-1)^q(a)` shows

```
S = sum_(x in L) (-1)^q(a+x) = sum_V (-1)^q(x) = +16.
```

The positive sign is essential. A minus-type eight-dimensional quadratic
form admits affine four-/five-spaces with 16/24 value-one points. The
behavioral controls construct both counterexamples rather than treating
polar nondegeneracy alone as sufficient.

## Apply the lemma

For `k=4`, the possible polar ranks are zero, two and four. At rank
zero the radical has dimension four. The balanced case has eight ones;
the unbalanced case has `(16-16)/2=0` by the signed lemma. At rank two
the unsigned bound is `8+4=12`. At rank four it is `8+2=10`.
Thus every affine four-space has at most 12 value-one points.

For `k=5`, the radical bound excludes polar rank zero. At polar rank
two, `t=3` and `k+t=8`. The balanced case has 16 ones and the unbalanced
case has `(32-16)/2=8`. At polar rank four, the unsigned bound is
`16+4=20`. These exhaust the possible even ranks. This proves the
20-point bound.

No flat census or assumption about the puncturing frame was used in these
upper bounds. Removing eight root lines preserves them.

## Attainment on the actual P112

In the current eight-bit residue coordinates, two affine spaces are:

```
a=5, L=span(124,94,208,18)
a=6, L=span(210,249,50,247,170).
```

Their intersections with the actual P112 residues have respectively 12
and 20 elements. The leading-one labels of those intersections have
binary ranks exactly five and six. The full support lists are in
`RESULT.json`; both implementations check them against their reconstructed
root/frame inventories. The witnesses establish sharpness for the fixed
P112 as well as for the full 120-line extension.

## Dependencies and boundary

The general proof uses only finite-dimensional binary linear algebra,
polarization and the cancellation of a nonzero character. It does not
use the real Weyl-chamber theorem, A2 transitivity, root-code minimum
distance, characteristic-zero lifting or any shortening theorem. Those
remain separate dependencies of the predecessor applications. This
package replaces precisely the global support-capacity upper bounds,
not their full proofs or finite receipts.

Nick Petalas's PR3249/3255/3260 and root-simplex sources supply the exact
capacity obligation and label convention. David Arias's retained
`masked-root-star-assembly` uses the same E8 quadratic-model idea for a
different nonorthogonality-clique theorem. The affine restriction and
signed character-sum argument above are the present contribution. Retain
the E8/P112 lineage including joaqcoo. No predecessor is modified.
