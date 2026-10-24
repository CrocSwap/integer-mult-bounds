# Native monomial lower-bound handoff

The coordinating agent proposed the dual-number representation. This
agent reconstructed it and checked its hypotheses. The proof-audit
agent also reviewed the negative-query count and the helper-role scope.

The result is exact: r productive roles, m ADDRESS difference coordinates
and rational monomial rank-one queries require at least r*m queries.
In fact at least r*m queries must have negative determinant. Positive
coordinate scales vanish in this representation. Free binary DATA basis
changes can be absorbed after the ADDRESS augmentation proves their
total product is identity. Extra arbitrary dirty roles that return
identity do not remove the lower bound for the productive roles.

Thus ten and eleven queries cannot implement the complete four-role,
three-coordinate B3 endpoint. Twelve coordinate queries attain the bound.
The old ten-call solver run remains UNKNOWN as a solver receipt, but
the mathematical B3 question now has this direct proof.

Run `python3 -B check.py` in this directory. The frozen run returned 0
in 0.243 seconds. `VERIFICATION.json` gives the exact command, source
hashes and log hash. `CHECK.log` records the checks. The verifier uses
only the Python standard library and imports no earlier catalogue,
solver or checker.

Completed exact computations:

- All 48 B3 maps and all 2304 products preserve the dual-number map.
- The nine rank-one reflections and all 120 scalar projectors give
  1080 verified one-column outer-product factorizations.
- Thirty-six rational weighted examples include positive scales and
  reciprocal weighted swaps.
- The twelve-call word reaches the complete target. Its literal
  telescoping factors have binary ranks 0 and 12, which attain equality.
- Every one-query omission misses the complete target.
- A nonmonomial unipotent square fails the entrywise sign map. This
  negative control checks why that map must not be extended to GL_m(Q).

The general inner-factorization lemma and the monomial classification
are proved in PROOF.md. The finite computations support their application;
they are not a Lean formalization of the general theorem.

The primitive model is pinned to PR521 at
`a190fdb39f31647fc6f651625353710624627348`. Its source proof was read
through the GitHub connector, with blob
`c3f67fc807aa3bf32ba559d51ea0b7e7a424229d`.

No native construction, supplier gain or integer-multiplication kappa
was produced. No PR was opened. No global novelty claim was established.
The result rules out the complete rational monomial family. A gain in
this native model needs genuine nonmonomial maps or a different contract.
Call sizes, widths, helper state and recurrence invoices still govern
any multiplication exponent. The query bound alone gives no global
kappa ceiling.

The earlier packet in `../native-research` has narrower subgroup filters
and a consecutive three-shear normal form. Those statements remain
valid. Its statement that ten-call B3 is mathematically unresolved is
superseded by this proof. Interleaved nonmonomial positive queries remain
open. AI assistance was used in this proof and verifier work.
