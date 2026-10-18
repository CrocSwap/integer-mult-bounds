# The three retained T16 moment crossings are unique

Each crossing identified by mightyOil's PR1254 has exactly one zero in
`0<a<1`. Exact brackets for that zero are:

| Old to new | Lower a | Upper a |
|---|---:|---:|
| 1050 to 1053 | 397/1024 | 398/1024 |
| 1074 to 1087 | 712/1024 | 713/1024 |
| 1082 to 1087 | 344/1024 | 345/1024 |

For all three pairs, the newer profile has strictly smaller native moment
throughout **0<a<=43/128**. This supplies the common favorable interval and
uniqueness deliberately left open by `t16-moment-order-audit`. It does not
change any supplier root, selected record, surcharge or physical construction.

## Scope and exact proof

Reuse the predecessor's source-bound delta histograms. Its acceptance of the
underlying owner maps is inherited, not rerun. With `p=1-a`, all three have

`F(p)=C-A*b^p-B*c^p+D*d^p`,

where `C,A,B,D>0` and `1<b<c<d`. Equal rank mass gives `F(1)=0`.
For every real p,

`F'(p)/d^p = -A log(b)(b/d)^p - B log(c)(c/d)^p + D log(d)`.

The right side is strictly increasing: differentiating its two nonconstant
terms yields strictly positive terms because `log(b/d),log(c/d)<0`.
Thus F' has at most one real zero. Rolle's theorem implies F has at most
two distinct real zeros. No numerical derivative sampling enters this argument.

The exact integer product test

`d^(D*d) > b^(A*b) c^(B*c)`

certifies `F'(1)>0` for each pair. Hence F is negative immediately to the
left of one. Each also has `F(0)=C-A-B+D>0`. Continuity therefore supplies
one zero in `(0,1)`, in addition to one at p=1; the bound proves uniqueness.
Both are simple: if the interior root had zero derivative, Rolle applied
between it and p=1 would give a second derivative zero. Transforming back
to a gives negative moment difference before the unique interior crossing,
and positive difference afterward. The positive normalization
`73^(a-1)/14336` preserves signs under the predecessor's common contract.

This is a specialized four-term shape proof; no general sign-variation
classification, maximal supplier saving or order for changed overheads is claimed.

## Exact arithmetic and independent controls

The verifier uses a different numeric method from PR1254's integer-root
enclosures. Range-reduce `r=2^k*x`, `1<=x<2`, and use

`log(x)=2 sum(j>=0) z^(2j+1)/(2j+1)`, `z=(x-1)/(x+1)`.

The first N=60 terms are a lower bound; the remaining tail is at most
`2 z^(2N+1)/((2N+1)(1-z^2))`. Outward rounding to dyadic denominator 2^80
keeps a rational enclosure. For `0<=t<=4`, sum exp(t) through degree 52;
the omitted tail is at most the next term divided by `1-t/54`.
Monotonicity and signed interval propagation certify both endpoints of each
bracket. Every operation is rational; floating logs or exponentials are absent.

A separately written integer-square-root comparison at a=1/2 checks the
sign for every pair. Controls reject unequal mass, reversed coefficient
signs, a missing term and a genuine four-term/equal-mass/positive-count
fixture with the wrong derivative sign (`{1:3,2:-2,3:-1,4:1}`). In the last
case the slope test fails since `4^4<2^4*3^3`. These are theorem-premise
controls; they are not claims that the retained verifier accepted bad data.

```
python -I -O -B research/t16-unique-crossings/verify.py
python scripts/research_package.py --package research/t16-unique-crossings
```

Normal replay compares the full RESULT.json without writing. Direct replay
checks live source hashes; registered replay checks base Git blobs and task
provenance too. No predecessor numerical function is imported. The written
Rolle proof is not a new Lean theorem or independent human review.

## Open next questions

Can the four-term certificate safely screen a named owner-search loop?
First measure occurrences and verify equal mass, sign shape, and identical
surcharges on every proposal. Actual search integration and a measured benefit
are blockers. No extra search or new owner-map admission is supplied here.
The structured question is in TASK.json.

## Credit and provenance

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`, revision 3,
nonce `f240fdd9e965d3d2960a6b40057ca4da`. SOURCES.json pins the exact
predecessor receipt, proof and verifier. Credit mightyOil for PR1254's
66-pair census and three crossing witnesses, Jeremy Kothe and Rohan Arun
for the accepted T16 maps, Hao Yan for the controller, and the pricing,
owner-audit and supplier lineage preserved in that package. This result
depends on those profiles; it does not repeat their physical admission.
Prepared by woklerx with substantial OpenAI Codex assistance. Apache-2.0.
