# Sharp borrowing-fit threshold for the proposed PR2234 BIT caller

For the exact stock prescribed by [Jose Manuel's PR2234](https://github.com/CrocSwap/integer-mult-bounds/pull/2234),
**311,311 is the least uniform integer cutoff above which the borrowed stock
always fits**. The result holds for every permitted prime `q>2^80`. At width
311,310 an explicitly certified prime gives exactly half-width borrowing,
which violates the source's strict fit condition.

This replaces the word "Eventually" in one stock-fit implication of the
pending proof. It does not certify that entire construction, change the
selected frontier, or identify its stock with the fourteen retained
bootstrap-stage coefficients. No new multiplication exponent is claimed.

## Exact source and theorem

The predecessor is pinned at
`d047ef86fbc5b1614d3d8e2b8d3441413beab73f`,
`research/selected-bit-recursive-closure/PROOF.md`, sections 1, 6 and 8.
Its unchanged [proof](sources/pr2234/PROOF.md) and
[attribution notice](sources/pr2234/NOTICE.md) are retained with Git blob and
SHA256 identities in [SOURCES.json](SOURCES.json). No predecessor code runs.

For each integer width `e>=1` and prime `q>2^80`, define

```
c = 17/10000,  w = ceil(e^c),
M = lcm(28416,28425) = 269241600,
K(w) = M |GL_64(F_q)| q^(4096(w-1)),
D(e) = 0                         if e<64,
D(e) = 1+D(42 floor(e/64))        otherwise,
S(e) = K(w)^D(e),  k(e,q) = ceil(log_q S(e)).
```

**Theorem.** For every such prime and every integer `e>=311311`,
`k(e,q)<e/2`. No smaller integer can replace 311311 in this uniform statement.

The stock is chosen from the original width `e`, before the body width is
chosen, exactly as in the source. Sharpness concerns this prescribed stock
and strict fit test. It does not assert that every smaller width fails, that
this stock is minimal, or that a different borrowing algorithm cannot work.

## 1. Integer upper bound and exact depth staircase

Counting independent columns gives

```
|GL_64(F_q)| = q^4096 P(q),
P(q) = product_(i=1)^64 (1-q^-i),   0<P(q)<1.
```

Since `M<2^29` and `q>2^80`,
`log_q K < 4096w+29/80`. The first term is integral after multiplication
by `D`, so, also when `D=0`,

```
k <= U(e) := 4096 w D(e) + ceil(29 D(e)/80).                 (1)
```

Let `b_d` be the first width of depth at least `d`. Inverting the floor
recurrence gives

```
b_1=64,   b_(d+1)=64 ceil(b_d/42).
```

Indeed `D(e)>=d+1` iff `42 floor(e/64)>=b_d`. These thresholds are strictly
increasing and characterize the entire depth staircase. For
`311311<=e<2^20`, `1<e^c<2`, hence `w=2` exactly. Equation (1) then gives
four constant-bound intervals:

| Widths, inclusive | D(e) | U(e) | First width minus 2U(e) |
| --- | ---: | ---: | ---: |
| 311311–405311 | 19 | 155655 | 1 |
| 405312–617663 | 20 | 163848 | 77616 |
| 617664–941247 | 21 | 172040 | 273584 |
| 941248–1048575 | 22 | 180232 | 580784 |

The positive margins prove strict fit on all four intervals. All endpoints
come from the recurrence, rather than a numerical logarithm approximation.

## 2. Infinite tail, including every later atom-width ceiling jump

Two active levels reduce width by a factor less than one half, since
`2*42^2<64^2`; floors can only reduce the child. Therefore
`D(e)<=2 ceil(log2 e)` for `e>=2`. This weak bound is sufficient here.

For `e>=2^20`, put `j=floor(log2 e)>=20`. Then

```
D(e)<=2(j+1),   w=ceil(e^c)<=2*2^(c(j+1)),
log_q K < 4097w,
k <= B_j+1,   B_j=16388(j+1)2^(c(j+1)).                    (2)
```

We prove `B_j+1<2^(j-1)` for every integer `j>=20`. At the first index,
`21c<1/2` and `sqrt(2)<3/2`, so

```
B_20+1 < 16388*21*(3/2)+1 = 516223 < 524288 = 2^19.
```

The ratio of successive normalized `B` terms obeys

```
(B_(j+1)/2^j)/(B_j/2^(j-1))
  = ((j+2)/(j+1))*2^c/2 < (22/21)*(3/4) = 11/14 < 1.
```

The normalized additional 1 contracts by `1/2<=11/14`, so the same strict
bound persists for `B_j+1`. Combining this with (2) and `e>=2^j` gives
`k<2^(j-1)<=e/2`. This argument treats all later ceiling jumps without
enumerating widths or assuming that `k/e` is monotone at those jumps.

## 3. Exact failure at the preceding width

Take

```
e*=311310,  w=2,  D(e*)=19,
q*=213*2^80+1 = 257501199577916014212415489.
```

Section 4 certifies that `q*` is prime. For this prime the verifier checks
the small integer inequalities

```
2(q*)^6 < M^19 < (q*)^7,   38 < q*-1.                    (3)
```

The elementary product inequality `product(1-x_i)>=1-sum(x_i)` implies
`P(q*)>1-1/(q*-1)`. Bernoulli's inequality then gives
`P(q*)^19>1-19/(q*-1)>1/2`. Together with (3),

```
(q*)^6 < M^19 P(q*)^19 < (q*)^7,
155654 < log_(q*) S(e*) < 155655,
k(e*,q*) = 155655 = e*/2.
```

Thus strict fit fails at `311310`. This is a witness for the actual stock,
not merely a failure of the sufficient upper guard. Every smaller proposed
universal cutoff includes this width, proving minimality of 311311.

## 4. Self-contained prime certificate

The replay checks

```
7^((q*-1)/2) mod q* = q*-1,
(2^80+1)^2 > q*.
```

Here is the elementary reason this proves primality. If a prime `p` divides
`q*`, then 7 is a unit modulo `p` and its order divides `213*2^80` but does
not divide `213*2^79`. Since 213 is odd, `2^80` divides that order and hence
`p-1`. Consequently `p>=2^80+1>sqrt(q*)`. A composite positive integer has
a prime divisor no larger than its square root, a contradiction. The check
uses exact modular exponentiation, with no probable-prime assumption.

## Reproduction and evidence boundaries

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 -I -B research/bit2234-stock-threshold/verify.py
python3.12 scripts/research_package.py --package research/bit2234-stock-threshold
```

Expected verifier marker:
`PASS_BIT2234_STOCK_THRESHOLD cutoff=311311 boundary=311310`.
The registered replay also runs the tests normally and with `-O`.
Source authentication and acceptance checks do not depend on Python assertions.
The stored [RESULT.json](RESULT.json) must equal a fresh exact reconstruction;
missing or changed results fail, without automatic regeneration.

The separate tests build a bottom-up maximum over every child rank 1–42,
cross-check the inverse staircase through 2^21, test distant exact atom-width
ceiling boundaries, and reject source/receipt corruption through the public
CLI in both modes. Boundary controls expose replacing strict fit by weak fit,
flooring either logarithmic or atom-width rounding, omitting high matrix
fibers, and a false prime witness. The universal statement rests on the
written proof above; finite checks do not substitute for its quantifiers.

This result does not implement the full GL64 payload, establish the caller's
time or restoration contracts, or execute the selected cold replay. Nor does
it identify a practical runtime cutoff: constants, the fixed prime, and other
interfaces remain those of the pending construction. The selected-stage
stock, complex supplier, precision/tape and outer-transfer obligations are
not discharged by this stock calculation.

## Overlap and scope change

Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The `selected-stock-envelope` card is explicitly **changed** to the actual
reserve of the proposed replacement caller, rather than a retained selected
bootstrap stage. Its native BIT dimension is 64; the separate complex
dimension 73 is not substituted here. [TASK.json](TASK.json) records this
decision, live overlap coverage and the final freshness checkpoint.

PR2084/2120 already supply conditional BIT stock coefficients; PR2105
studies complex depth; PR2097 supplies a fresh-field theorem. PR2289/2295
formalize the PR2234 time recurrence and numerical moment. PR2310 and the
active Discussion2319 concern control preparation and joined dispatch.
This contribution proves the explicit universal fit threshold and its sharp
boundary, not those earlier statements. Its
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2209#discussioncomment-18941213)
is in the existing BIT-closure discussion.

## Open next questions

1. Does a smaller stock, chosen self-consistently from the post-borrow body
   width, fit earlier while retaining the complete-row divisibility contract?
   This could reduce reserve without changing the moment. Start by studying
   the integer fixed-point inequality using `D(floor((e-k)/w))`; first prove
   that the changed stock supplies every recursive packet. That contract
   change blocks any direct use of this theorem's sharpness claim.
2. Can a joined implementation certify fresh fields, restored row/work and
   the uniform time bound at the same interfaces? This is needed for caller
   admission. Start with PR2234 sections 5–7 and the PR2310/Discussion2319
   preparation/dispatch work. Full physical composition remains the blocker;
   a fit threshold alone cannot certify it.

## Credit

Prepared for Aakash (@aakashthakkar) with substantial OpenAI Codex assistance
in source review, mathematics, implementation, writing and separate agent
checks. No independent human review or proof-assistant verification is claimed.
New work is Apache-2.0, following the repository license.

Jose Manuel (@jmbarrancoml) supplied PR2234's caller, exact reserve and depth
definitions, and the borrowing argument. Its retained notice credits the
selected PR589/PR555 word, alephnan's PR1627 proof, eumemic's GL framework,
source527 and the named routing/parking contributors. Josie Elliston's
PR1956/1965, ToikY's PR1990, Adam Gall's PR2084/2097, Nick Petalas's PR2120
and Sricharan Vagvala's PR2105 motivated the distinct stock, fit and producer
boundaries. Their constructions and generic depth/stock principles are not
claimed as new here.
