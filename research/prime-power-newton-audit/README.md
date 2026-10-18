# Exact Newton polygon audit of the prime-power nonunit lemma

This **mathematical audit / research note** corroborates the nonunit-root
lemma in Ali Romman's incorporated [PR621](https://github.com/CrocSwap/integer-mult-bounds/pull/621)
and gives the complete p-adic root-valuation multiset for its kernel. No defect
was found in that lemma. The result does not change the selected exponent,
complex conditioning bound, supplier, or inverse implementation.

For a prime power `r = p^a`, normalize the valuation by `v(1-u) = 1`, where
`u` is any primitive r-th root. For each `k = 1,...,a`, the integral kernel
has exactly

    (p-1) p^(k-1) roots of valuation 1 + (k-1)(p-1)/p,

counting multiplicity. These positive valuations imply that every root is
an algebraic nonunit. With the alternative convention `v_p(p)=1`, divide
all displayed valuations by `phi(r)`. These are **p-adic valuations**, not
complex absolute values. They do not distinguish roots inside and outside
the complex unit circle.

The [written proof](PROOF.md) establishes the all-prime-power statement.
The finite checker tests its coefficient, polygon, normalization, and
multiplicity obligations using two different implementations: factor-valuation
counting and exact cyclotomic polynomial multiplication followed by a
uniformizer-basis change. Neither imports PR621's verifier.

```sh
python3 -I -O -B research/prime-power-newton-audit/verify.py
python3 -I -B research/prime-power-newton-audit/test_verify.py
```

Python 3.9+; standard library only. The first command checks the source pins
and complete frozen receipt. Expected:

    PASS_NEWTON_NONUNIT_AUDIT: 28 radices; 697 primitive embeddings; 30224 coefficient obligations; 9 negative controls

The fixed finite domain is every prime power `2 <= r <= 68` and every
primitive exponent `1 <= t < r`. The OS assignment seed 68 selected the
upper endpoint. This is a completed exhaustive finite audit, not a search
for better κ. The explicit controls include a unit constant, an omitted
ramified factor, mixed valuation normalizations, reversed coefficients,
a nonunit leading coefficient, invalid field/root inputs, and lost
collinear contacts. A unit-constant mutation really changes the polygon
to a horizontal edge: it is a counterexample to dropping the original
coefficient hypothesis, not to PR621.

To regenerate a separate receipt:

```sh
python3 -I -O -B research/prime-power-newton-audit/verify.py --write-receipt /tmp/newton-audit.json
cmp research/prime-power-newton-audit/EXPECTED.json /tmp/newton-audit.json
```

[CLAIM.json](CLAIM.json) records track selection, three candidate tasks,
coordination, and the stopping rule. [SOURCE.json](SOURCE.json) pins the
base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, PR621 source head, exact
contextual files, and mathematical references. [VALIDATION.md](VALIDATION.md)
records executed checks and limitations. [NOTICE.md](NOTICE.md) preserves
attribution and substantial AI assistance disclosure.

The existing PR668 CRT audit checks resultants, Bezout identities, and norms;
PR666 studies composite-radix lifting; PR628 and PR692 study rounded inverses
and weighted cyclic closures. This package instead determines every root's
nonarchimedean valuation for prime powers. It does not import or certify those
pending changes, claim literature priority, or replace the accepted PR621
circle-bound proof. No paid preparation, rounding/restoration, tape/compiler,
precision, all-size supplier, or analytic multiplication obligation is discharged.
