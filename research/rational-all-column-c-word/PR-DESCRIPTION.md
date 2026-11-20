## Result and motivation

#7834 tests and recursively executes all-column Gaussian C words using a
dyadic scalar alphabet. The selected construction and #7828 also use fixed
odd rational scalars. This package proves a local extension by
`SCALE(a,b,q)`, multiplication by `(a+i b)/q`, and accounts for its exact
common grid without adding paid C instructions.

For a fixed word with base rank N, productive width W and J instructions,
let D be the LCM of the odd denominator parts and d=floor(log_N h).
One root factor D^(Jd) clears every intermediate odd denominator. A
completed child returns its exact dyadic endpoint relative to its entrance;
only unfinished contexts accumulate odd debt. A coefficient-dependent
binary guard also pays denominator height, magnitude and full Gaussian
numerator staging. Both surplus scales are retired exactly at the root.

The exact dictionary/Vandermonde test extends from Gaussian dyadics to
Gaussian rationals. Scalar coefficients stay outside the tensor power;
column phase i remains i^f. Private endpoints are checked and receive
no productive credit. Signed unary codes retain exponential-in-length
validation and polynomial-in-precision bounded startup.

Under the named complete-row scalar, placement, parking and disjoint-XOR
contracts, the added local passes cost O_word(V), root scaling and
retirement cost O_word(V log(h+2)), and working width remains O_word(p)
in the source geometry. Genuine W^d row stock, padding below a factor
of two, zero-output checks and the source fallback remain explicit.

## Evidence

Run:

```sh
python3 -B scripts/research_package.py --package research/rational-all-column-c-word
```

README.md gives the two exact, bounded predecessor fetches if a fresh
checkout lacks their source-history objects. Standalone arithmetic replay
uses the committed, authenticated package only.

The primary implementation checks exact all-column dictionaries and
compares integer-grid execution with a dense closed tensor formula.
Independent review derives the invariant before reading that code, then
checks the final implementation against its separate Fraction oracle.
Coverage includes three recursive levels, three productive registers,
nonreal coefficients, interleaved spectators, nonzero private paid work,
padding, self-aliases and a denominator 2^1024. Controls detect omitted
depth in the odd budget, a coefficient-blind binary guard, scalar/column
phase confusion, nonzero private endpoints and an unretired root scale.

The reviewer corrected one startup overstatement before publication:
unary denominator fields share a length budget, giving
D<=product q_i<=3^(L/3). A D-state table alone would still have
2^O(L) size; binary divisor arithmetic is a valid implementation choice,
not a necessary rescue of that bound. The corrected proof and review
disposition are committed.

## Scope and open obligations

This is a fixed-word scalar/grid implication, not a literal tape executor
or the complete translation of #7828. Python arrays do not certify movement
or erasure. Every test word is deliberately unfunded. An actual compiled
supplier still needs its full phase/owner/adapter translation, paid count,
physical contracts and outer admission. All five selected assumptions remain;
there is no new kappa or unconditional multiplication theorem.

## Sources and credit

Canonical base: e54523517d0f03e58352e647c403a5af3e525a57.
#7834 is pinned at 4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02;
#7828 at 03b572b3b9ab72c6ba67762e85e1630cda1daad5.
Credit Ali Romman for the dictionary, Vandermonde argument, startup,
row recursion and compiler context; the selected #7000 numerical audit
and all retained predecessors remain credited. Common denominators and
binary arithmetic are classical. Prepared for Jerry Chen / @CubeJerry
with substantial OpenAI assistance and separate model-assisted review.
No human peer review or formal-kernel acceptance is claimed.
