# Matrix-corollary layout: positive signoff

The no-sort union layout in `AUDIT.md` applies unchanged to
`work/phase_assembly_ultra/MATRIX-COROLLARY.md`. Its algebraic conditions are
closed axis supports E_i and a complete microbox; neither its proof nor its
implementation requires g<d's bit width, g<sqrt(B), or density W/d.

At the pinned parameters

```
epsilon = .9987451457099504818...
xi      = .7502137479126781301...
beta    = .2497852420873218699...
```

the following strict inequalities suffice:

```
beta + 1/2 - xi < 0,          # union density tends to zero
beta + 2(1-epsilon) < 1,      # membership arithmetic fits p-bit record
epsilon + beta + 1/2 - xi < 1-kappa,
epsilon - beta < 1-kappa.    # grouped full scans
```

The first power is approximately -.00042850582535626. Fixed logarithmic
inflation from carving still tends to zero. The membership power is
.2522949506674209063, strictly below one. The total union movement power is
.9983166398845942215, leaving the claimed 10^-5 strict margin above the
candidate's main saving, apart from its separately reserved 10^-11 floor.

The implementation is specifically the complete rectangle
`U_i=E_i x [L]^(g-1)` extraction, one-field transpose and ordered merge.
It scans U once per axis and moves only Ui in the local transpose. It does
**not** sort U by a g-axis key. Such a sort would introduce an extra growing
factor and is correctly rejected in the new ledger. Sparse keys remain
only on microedge correction streams of volume O(VgA/L), which have ample
p^-5 slack; increasing beta to .25 does not change their negligible status.

Coefficient pages remain polynomial-size per complete microbox: there are
O(L/B polylog p) capped pieces per axis, g is polynomial, and each supplied
local generator has polynomial preparation. L^g and the spectator RHS stock
are superpolynomial, so the existing setup amortization becomes stronger.
Schur support, clipped endpoints and principal-window locality are
properties of the same underlying matrix and are unaffected by replacing
the bounded W-square matrix product implementation.

For clarity, use this global q-ordering:

1. Perform all forward monotone q_j embeddings group by group while the
   tensor remains axis-major. Each is one scan, for O(Vd/g) total work.
2. Perform the single retained global low-bit gather. Keep all dyadic target
   coordinate ranges complete throughout every global H-supplier call.
3. Finish the inverse global gather before performing compression q-image
   selections group by group in axis-major order.

No whole long-axis gather is added per group. The support-local exposure
uses the already audited arbitrary-spacing router. Its short-record suffix
conjugation has now also been made explicit in `SUPPORT-ROUTER.md` following
the independent supplier audit.

No layout blocker remains for this corollary. This signoff assumes, rather
than re-proves, its additional effective matrix-exponent hypothesis and the
separate anchored Gaussian/precision result. It does not itself promote a
new selected multiplication certificate.
