# Independent review of the companion grammar ceiling

Independent construction author, for Jerry Chen / @CubeJerry, with substantial OpenAI Codex
assistance; 2026-11-06. Apache-2.0.

Reviewed the economic author's `PROOF.md` and `verify.py` (integrated here as `ECONOMICS.md` and `economics.py`)
after constructing the four-query module. The source-relative claim fixes
the #6726 leaves and six-site root and permits arbitrary mixtures of
ordinary and the new four-query nodes. Its all-size bounds are uniform for
complex kappa in [0.0033,0.004] and BIT kappa in [0.0037,0.004].

The mathematical checks were:

- The two independent plain R targets cancel precisely their two paid R
  idles. Including both, the new node contribution is `2 i(a)-2` and the
  difference from the old node is `2[i(a)-i(a+b)]-1`.
- Strict concavity gives `i(a)<1`; every new node is negative, hence below
  the positive ordinary-node envelope `A=2 i(2)-1` on the declared ranges.
- Six binary trees with F leaves have exactly F-6 internal nodes, including
  any mixture of node types. The source-bound root formula and Jensen
  bound give the stated B(F); differentiating gives the reported B'(F).
- B(F) is concave in real F. Negative B(50) and B'(50) suffice for the full
  tail. Native signed moment monotonicity is separately certified by the
  derivative enclosure rather than presumed from its signed coefficients.
- The uniform finite replacement bound is valid: `i_k(a)<=i_lower(1)`
  and `i_k(a+b)>=i_cap(49)` for the stated node-size range. Thus nodewise
  replacement proves dominance before the ordinary dynamic program is run.
- The triple maximization uses the left signature `i(b+c)+i(c)` on both
  halves. The right signature `i(d+e)+i(d)` has exactly the same maximized
  value by reversing the ordered triple; all positive triples are included.
- Monotonicity through the cap follows from the separately checked native
  derivative and the decreasing positive H/i terms in the ordinary optimum.

No mathematical issue was found in these steps. This review does not
independently revalidate all source native frames or the power-enclosure
engine. It is not a physical supplier-admission review.

As a separate numerical transcription check, Python Decimal at precision
85, with no import of the retained interval engine, recomputed B(50),
B'(50), and the full literal source target-minus-paid moment at each raw
ceiling. All six values fell inside the economic author's rational intervals. The
leading values were:

| Source | B(50) | B'(50) | Complete literal margin at ceiling |
|---|---:|---:|---:|
| Complex | -0.8591428254814850989764359210065 | -0.05009175986144440060194662634970 | -1.017906668299571644673074928514e-10 |
| BIT | -0.5173312517837142916261833974169 | -0.04226750615088335877829607331438 | -5.796103785719505307252530252105e-11 |

These decimal computations corroborate transcription; they are not the
exact sign certificate. The exact enclosures remain the economic author's certificate.
The three-query lower bound, the positive four-query realization, and the
complete grammar ceiling have distinct proof boundaries and should remain
distinguished in the integrated package.
