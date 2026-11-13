# Independent price and eight-component review

The exact-source reconstruction and integer-power price checks pass. This is
an arithmetic review of the stated optimistic envelope, not a physical word
or a multiplication exponent claim. Source/global decomposition hypotheses
remain the separate root/C review gates.

`small.py` reads C31's freshly replayed actual source rows and history spaces,
checks the source hash and literal MOVE records, and independently recomputes
the helper-only history extension by main-projection rank-nullity. It uses
maximum pivots and quotient reduction across every pivot. For each of the 43
zero subsets it recomputes the original-helper target-rank prefix ranks,
cache eligibility, and each individual new-cache prefix bound. It checks all
89 grant cases and 91 obligation invoices against the root receipt. No root
linear algebra or root price routine is imported.

For each case, one necessary obligation suffices to prove the claimed cap on
the minimum of obligation upper bounds. `SMALL.json` records that obligation
and an exact proof valid for every 0 <= kappa <= 1/100. The proof either checks
all nine increasing-concave generators min(r,k), or uses the rational bound
9^(1/100) < 1023/1000, certified by 9*1000^100 < 1023^100. For a signed difference,
1000*sum(positive rank multiplicities) >= 1023*sum(negative rank multiplicities)
then proves nonnegativity throughout the interval.

Five components have ceiling zero. The other three have ceilings
f(5)+f(1)-f(6), f(1)+f(3)-f(4), and f(6)-f(4), respectively, on cache sets
{39875,39884}, {42500}, and {41646}. Their sum is
F = f(5)+f(3)+2*f(1)-2*f(4).

At kappa=19/5000, `powers.py` certifies each bracket using only integer
inequalities a^5000 <= r^4981*10^120000 < (a+1)^5000, with rational endpoints
a/10^24 and (a+1)/10^24. Decimal evaluation supplies an initial guess only.
All price signs follow from the checked integer inequalities. Exact integral
prices may have equal endpoints. `margin.py` authenticates the exact native
WORD, exact Git caller bytes, canonical payload, full invoice, and all 17
native calls. It derives the baseline moment M from that invoice and proves

    -25.258109991835383588522658
      <= M+17*F <=
    -25.258109991835383588473069 < -25.2581.

The margin below -25.2581 is greater than 0.000009991835383588473069. The
upper envelope is a generous funding bound; its crossing is not asserted
achievable. All original-coordinate and whole-MOVE restrictions are retained.

The actual validators reject a wrong target-debit sign, a missing case,
18 calls substituted for 17 in the stated margin test, and an invalid lower
price bracket. An all-pivot trap checks that a nonpivot coordinate does not
prematurely stop quotient reduction. Both verifiers pass under normal Python
and `python -O`; receipts agree after deleting elapsed time. Source pins,
file hashes and logical receipt hashes appear in `VALIDATION.json` and the
two result files. No existing frozen wave41 files were changed.
