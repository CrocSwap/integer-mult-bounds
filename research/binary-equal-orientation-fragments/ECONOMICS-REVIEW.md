# Independent review of the complete-tree economics

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance.
Apache-2.0. This is a separately developed mathematical and arithmetic
check, not independent human peer review or proof-kernel certification.
It reviews the declared recurrence and its certificate; it does not
independently reprove the inherited native physical construction.

## Conclusion and exact scope

The complete-tree exclusion in ECONOMICS.md is valid for the stated
fixed root, native tariff and old/new binary-node invoices. I checked
the arbitrary-size root normalization, finite recurrence, small-tree
replacement, concave large-tree envelope, uniform kappa monotonicity,
and the author's directed-root arithmetic. An independently written
rational-series engine reproduces the decisive signs and explicitly
includes both new-node orientations in its finite optimization.

The number `0.0033072446849` is the certified upper endpoint of the
predecessor's raw crossing interval. The proof excludes every allowed
tree at or above this endpoint within the stated kappa interval; it
does not claim to identify a real-valued crossing beyond that interval's
precision. The new nodes do not improve their all-old counterparts in
the relevant finite range, while all sufficiently large trees are
excluded. No new kappa, native admission or unrestricted caller
obstruction is inferred.

## 1. Symbolic root invoice and normalization

The retained ROOT6726.json has six full stages with masks
`[3,195,195,53,53,5]`. Reading bits by output field gives
`ABCDEF, ABC, DEF, empty, DE, DE, BC, BC`. This is symbolic in all
six positive child sizes; it is not an inference from the one
18-leaf numerical fixture.

Each child main body has rank eight times its number of native leaves.
The first three fields therefore produce exactly the three h terms
in equation (1). The two BC bodies have independently paid whole-body
work: splitting one as plain B plus SC leaves `i(c)`, while retaining
the other leaves `i(b+c)`. Likewise the split DE body contributes
`i(d)` and the unsplit one `i(d+e)`. Nine root queries minus six full
calls leaves three thin queries. The empty output contributes one,
so the net root constant is `1-3=-2` per port.

The native inventories count 104 ports, so dividing their moment
margin by 104 gives the stated ell. An old internal node contributes
`2i(n)-1`; the constructed new node contributes `2i(j)-2`, where j
is the child assigned the retained orientation. Its additional thin
query is the extra negative unit. The optional suffix-only fresh
fields are complete independently paid jobs with equal target/body
moments, so their removal cancels equal quantities rather than granting
free work. The main-port boundary is unchanged by the node comparison.

The independent checker authenticates the native pricing bytes and
ROOT6726.json, reconstructs its eight support sets, and checks the
query constant. The predecessor's formal/native/physical validity is
an inherited premise, explicitly retained by the package.

## 2. Small trees, the concave tail, and uniform monotonicity

For n at most 49 and kappa at most 1/250, the integral expression for
i(n) and `393*4^250 < 5^250` give `i(n)>498/625>1/2`.
For positive child sizes and positive kappa, `i(j)<1`. Therefore
`2(i(j)-i(n))-1<0`: replacing a new node by an old node strictly
improves the margin. This holds for either orientation and every
allowed small subtree; it is not asserted at arbitrarily large n.

For a tree with n leaves there are n-1 internal nodes. The old
contribution is at most `A=2i(2)-1`, since i decreases with n; the
new contribution is negative and therefore also at most A. Positivity
of A throughout the interval follows from the preceding small-tree
inequality. The six children thus contribute at most `(F-6)A`.
Concavity bounds the two half-root h terms by `2h(4F+1)`, and the
four root increments by `4i(1)`. These steps give exactly B(F).

Its derivative at F=50 is
`ell+A+8(1-kappa)401^(-kappa)+8(1-kappa)201^(-kappa)`.
B is concave, so a negative value and negative derivative at 50
exclude the entire real tail F>=50, including all integer leaf counts.

Every positive h term decreases with kappa. The derivative of the
integrand defining i is negative because its argument is at least
eight and `1-kappa>0`. The only signed term needing additional care
is ell. For ranks at most nine, `9*32^250 < 33^250` gives
`r^(1-kappa)>=32r/33`. Using integer lower/upper binary logarithms
with the correct coefficient signs yields exactly
`ell'(kappa)/log(2) <= -24273/572 < 0`.
Thus the bound at the lower endpoint propagates across the stated
kappa interval. There is no unsupported monotonicity inference from
an arbitrary signed histogram.

## 3. Finite-domain coverage

The all-old recurrence considers every split j=1,...,n-1 for each
n=2,...,49. Ordered triples cover every positive assignment to a
half-root. Reversing `(d,e,f)` makes the second half identical in
form to the first. Half-root sizes 3,...,46 and total sizes 6,...,49
are exactly the necessary finite domains.

The independent implementation deliberately optimizes the augmented
recurrence directly: for every split it includes the old node and
both orientations of the new node, checking strict interval separation
of each new contribution below the old contribution. This performs
2,352 orientation comparisons and 15,180 ordered triple evaluations.
All 44 total sizes have negative upper margin, and the best total is
18. It agrees with the reduction to the all-old recurrence without
assuming that reduction numerically.

## 4. Two independent numerical mechanisms

The author's engine brackets kappa by adjacent binary fractions. Its
repeated floor/ceiling integer square roots enclose each fractional
power of the base, and directed products enclose the lower exponent.
When kappa is not exactly represented, multiplying the upper product
by one final smallest root covers the upper adjacent exponent. Taking
directed reciprocals and multiplying by the base gives valid h bounds.
Signed rational multipliers swap interval ends as needed; interval
maxima bound every dynamic-program maximum. No floating-point sign
or Python assertion is needed for the certificate.

`independent_economics.py` uses a different mathematical mechanism.
For a rank r write `r=2^e m` with `1<=m<2`. It encloses logarithms by
64 terms of

    log(m) = 2 sum_(j>=0) z^(2j+1)/(2j+1),  z=(m-1)/(m+1),

where `0<=z<=1/3`. The remainder is bounded by
`2 z^129/[129(1-z^2)]`. The same formula bounds log(2).
After multiplication by kappa and outward dyadic rounding, a
24th-degree exponential Taylor sum and its positive geometric tail
bound enclose `r^kappa`; reciprocation gives `r^(1-kappa)`.
All calculations are exact rational or integer calculations, with
160-bit directed output. The script imports no author numerical engine.

The independent bounds are:

| Quantity | Outward enclosure |
| --- | --- |
| B(50) | `[-0.908794498996720237664239885848763605729163736, -0.908794498996720237664239885848763605729163730]` |
| B'(50) | `[-0.0511981106830088109290768814900547688008622100, -0.0511981106830088109290768814900547688008622098]` |
| Best finite margin at kappa* | `[-1.01790666829957164467307492851430267470665173e-10, -1.01790666829957164467307492851430265415244964e-10]` |

An omitted-extra-query control reverses the local comparison, as it
must. This checks that the extra query is mathematically decisive.
The predecessor source hashes and symbolic root support checks reject
changed inputs. Normal and optimized Python execute the same checks.

## Reproduction and limitations

```sh
python3 -I -W error -B research/binary-equal-orientation-fragments/independent_economics.py
python3 -I -O -W error -B research/binary-equal-orientation-fragments/independent_economics.py
```

Expected JSON status: `PASS_INDEPENDENT_ATANH_TREE_REVIEW`.
The report includes exact reviewed-document and author-engine hashes.
This review establishes the stated complete recurrence's numerical and
analytic conclusion. It neither prices another four-query implementation
nor removes native/compiler assumptions. The physical invoice and the
scientific admission of CrocSwap/integer-mult-bounds#6726 remain their
separately inherited obligations.
