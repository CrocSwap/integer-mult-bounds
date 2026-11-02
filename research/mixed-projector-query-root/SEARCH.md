# Search scope and fixed-root limit

The new bound uses the explicit rational root in ROOT.json. Its acceptance
does not depend on a heuristic search or on a modular zero test.

## Basis catalogue

The search kept rank-two projectors at query sites zero and six. Their
intersection has one dimension. Write u for (-1,1,-1,1,-1,1). Let K be the
four-dimensional space of vectors whose first coordinate and coordinate
sum are zero. For z in K and three independent columns d1,d2,d3 in K, use

```text
F = [e0-u-z, u+z, e0-z, d1, d2, d3].
```

In the four coordinates of K, z ranged over the nonzero vectors in
{-1,0,1}^4. Each d column ranged over primitive integer vectors in
{-2,-1,0,1,2}^4, with first nonzero coordinate positive. The search used
each unordered triple of d columns. Singular F matrices were excluded.

The enumeration checked 241,886,080 invertible bases modulo 65521. It found
695 distinct seven-site support patterns. Floating child-size searches
selected a pattern with full-site ranks 2,3,3,2. The rational reconstruction
then checked its exact projectors, native query planes and all independent
stage coefficients. The selected F has determinant one. Its inverse and
native basis data have dyadic coefficients.

This is a bounded catalogue. It does not cover all rational bases, larger
roots, noncommuting stage families or other query words. Floating searches
over the catalogue do not prove that each pattern's price is optimal.
An additional integer-program screen has finite time limits and unresolved
solver bounds. It is not used as an exclusion certificate.

## Child sizes

The two-pair score separates the four child sizes into two sums. A floating
dynamic program tested all totals through 200 and all binary child splits.
It selected 7,2,2,7. The complete exact caller and invoice use those trees.

The separate rational checker ceiling.py covers all positive integer child
sizes and all binary tree shapes for this fixed root and native source.
It checks every total below 100 and proves a decreasing negative bound for
all larger totals. Its ceiling is .00328469. The claim is .00328467.
PROOF.md states the full argument and its restrictions.

## Other local searches

- Structured roots through 20 fields did not improve the retained price.
- Braid moves on longer query words did not give a favorable complete bill
  in the tested finite domains.
- Two- and four-copy coupled bases did not improve the scalar construction
  in 14,000 proposed moves per coupling size.
- An internal-query extension of the earlier root has two exact shared
  idle subspaces. Its complete proposed price still loses to the binary
  supplier. The screen tested all child tuples through 48 per child.

These are search outcomes, not general impossibility results. The local
scripts, output files and logs remain in work/new-route-20261101. They are
outside the registered mathematical replay. The complete positive word,
source pins, exact bound and fixed-root ceiling are in this package.

The selected frontier is unchanged. The donor's local publication hold
remains in effect. No result from another investigation is claimed here.
