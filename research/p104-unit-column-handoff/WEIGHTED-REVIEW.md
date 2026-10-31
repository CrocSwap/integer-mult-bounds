# Independent review of the allowance-272 alternative

For the same dual pair, let
`S1=I+(1/2)e_594 e_592^T` and `S2=I+(1/2)e_594 e_593^T`.
The two off-diagonal elementary matrices multiply to zero in both orders,
so the shears commute and their inverse is obtained by negating both halves.
Writing `S=S1 S2`, the row `aS^-1` loses both 5/16 entries, leaving only
`a'_594=5/8` and `a'_596=3/8`. The column remains unchanged because its
592 and 593 entries are −1 and +1: `Sb=b`. Thus the previously proved unit
column completion for `(a',b)` followed by `S^-1` completes exactly the
original dual pair, without a spare role or a changed frame.

The inherited ADD tariff charges 20 for 5/8, 8 for ±1 and 10 for ±1/2.
One row-elimination ADD, four source (three cut) column ADDs and two inverse
half-shears give source **7 ADDs / 72 allowance** and cut **6 / 64**.
All four completed boundaries therefore use **26 ADDs / 272 allowance**.
This is a Pareto alternative to the gate-minimal 22 / 280 construction: it
uses four more ADDs and eight fewer allowance units. No weighted optimum or
global scalar-word optimum is claimed, and the six/five ADD lower bounds
for separately completed original dual pairs remain valid.

The separate integer-vector/power-of-two replay checks all 744 formal input
columns (553,536 endpoint coefficients), actual frame legality, independence
of the new public input, and every owned lifetime. The complete word has
25,166 events and allowance 217,700. Its paid histogram is unchanged; the
same rank-nine target becomes rank five plus rank four; the eight owned
lifetimes and peak one remain unchanged.

Normal and optimized executions of `weighted_review.py` pass ten fresh
semantic mutants. The wrapper first accepts this alternative with its own
exact expected counts, then requires every mutant to fail for an actual
endpoint, frame, ownership or algebra error. It explicitly rejects a test
whose only failure is the fixture-count check, avoiding the invalid use of
the original 22-event audit wrapper as a negative control for a 26-event word.
No native/caller admission or new κ is claimed. Review by @CubeJerry with
substantial OpenAI Codex assistance (worker D), crediting the source dual-pair
handoff, inherited tariff and separate worker A factorization package.
