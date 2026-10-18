# P112 shared correction: scalar endpoint and COPY-cost audit

**PR #2308's named frame pair needs at least 12 added COPY rank units in the
additive scalar model. Its fixed-profile 5% screen permits at most 8.** The
shared rational row-space identity remains valid; it does not by itself supply
the advertised +8 correction interface.

This is a scoped proof and exact finite audit of
[Cinna Davis's PR #2308](https://github.com/CrocSwap/integer-mult-bounds/pull/2308),
head `7653e0cc72527c1e7fc02499122d383713ee9d54`, answering its open complete-charge
question. Evidence is author-checked, with two separately implemented finite
arithmetic routes, both written with AI assistance. No independent human review,
proof assistant, supplier or new kappa is claimed.

## Exact object and results

The unchanged [predecessor certificate](PR2308-CERTIFICATE.json) names these
orthogonal frames in its E8 line order:

```
S1 = [2,3,16,17,46,47,52,53]
S2 = [2,3,20,21,42,43,46,47]
S1 intersection S2 = [2,3,46,47]
```

Thus `U = S1 union S2` contains **12**, not 16, distinct ports. The selected-label
map and E8 lattice direction bind the physical shared vector to **r = 234** in
`F2^9`, with self-pairing one. Upgraded ports are orthonormal planes
`E_a = span(q_a,r)`; other ports remain lines. There are 52 complementary ports
`T = {b : r dot q_b = 1}`.

The primary checker reconstructs 120 doubled E8 root representatives, checks all
112-by-112 selected binary pairings and the deleted-frame signatures, and checks
that S1 is the lexicographically first frame for this direction, as in PR #2308.
It derives the rational factorization from orthogonality without importing the
predecessor's solver.

| Checked quantity | Exact value |
| --- | ---: |
| Distinct upgraded ports | 12 |
| Common rational correction-basis rank | 8 |
| Coefficient matrix rank modulo 2 | 1 |
| Support COPY ranks, one direction | 1, 1, 4, 4, 1, 1, 4, 4 |
| Both directions' COPY rank sum | **40** |
| Forbidden nonzero entries left by these corrections | **32** |
| Missing within-U block rank | 8 |
| Any additive scalar correction's COPY-rank floor | **12** |
| Formal source/dirty-target columns checked | 224 |

The natural eight-term decoder using the *deleted* orthogonal frame costs 64
on the line ports and 68 on these mixed ports. With the displayed correction it
costs **108 before the missing within-U repair**. This is a separate-term
algebraic invoice, not a native program or an optimum over other bases. The
ordinary Euclidean coordinate factorization is a different representation and
is not substituted for that decoder.

[RESULT.json](RESULT.json) contains complete supports, rank witnesses, all bad
entries, exact rational moment intervals and controls.

## Scalar model and rational sharing

Let `G_ab = <root_a,root_b>` for roots of squared norm two. The normalized
original scalar map is `K0 = G/2`. For source port E_b and target endpoint
E_a-perp, a free endpoint correction requires orthogonal port subspaces.
Accordingly a fitting matrix satisfies

```
K_aa = 1;
K_ab = 0 for a != b whenever E_a and E_b are not orthogonal.
```

This is the mixed-port version of the condition in the retained
[paired-plane scalar audit](../paired-plane-scalar-mask-obstruction/README.md).
A scalar term `u v^T` costs the binary pairing rank between the spans of all
E_a with u_a nonzero and all E_b with v_b nonzero. Concatenated port bases give
this rank; repeats do not alter it. The primary compares bit and Boolean
elimination; the second checker explicitly enumerates the binary row span.

These are scalar factors with ordinary transpose over Q or C. Sharing physical
children across terms, bundled operator maps, a different tariff or replacing
the original scalar decoder requires a different interface theorem.

For the reference frame S0=S1, put

```
D[a,k] = <root_a,root_(S0[k])>,                         a in U;
B[k,b] = <root_(S0[k]),root_b>/2 if b in T, else 0.
```

Orthogonality gives `D B = G[U,T]`, with zeros outside T. The rank-eight common
basis identity is correct. We deduplicate shared rows, giving the mechanism
the favorable interpretation in which each physical port is used only once.

The ordinary scalar correction suggested by these blocks is `-D B/2` on
U-by-T, and its transpose on T-by-U, eight terms per direction. Their support
ranks cost 20 per direction, hence 40. Coefficient-parity rank one is not this
tariff: `(D,B) -> (2D,B/2)` preserves the exact map and all nonzero supports,
but changes coefficient-parity rank from one to zero. A separate implementation
theorem is necessary to turn coefficient sharing into physical COPY sharing.

## A missing cross-frame block

All upgraded planes contain the same anisotropic r, so **every pair of upgraded
planes is nonorthogonal**, including pairs in different frames. Hence K[U,U]
must be the identity. The displayed corrections leave K0[U,U] unchanged, with
32 forbidden off-diagonal entries. The required within-U correction
`I_U-G[U,U]/2` has rank eight.

For example, E8 lines 16 and 20 have selected labels 38 and 70. Their line
pairing is zero, but their planes share r with `r dot r=1`. The partial map has
`K[16,20]=1/2`. Source 20 equal to one, other sources zero, and target 16 initially
11 produce **23/2 instead of 11**. No free endpoint cross-addition can remove
this coefficient. All 112 source columns and 112 independent dirty-target
columns are checked. Setting the within-U block to the identity yields a valid
*scalar fitting-matrix* control, without claiming an implementation or price.

## Proof: any additive scalar correction costs at least 12

Allow any number of added scalar terms, arbitrary complex coefficients,
cancellations and arbitrary choices on free entries. Retain K0 and write the
final map as `K0 + Delta`. Every pair in `U x (U union T)` is nonorthogonal:
columns in U contain r, and columns in T pair to one with r. Thus Delta has
the fixed restriction

```
A = [ I_U-G[U,U]/2 | -G[U,T]/2 ].
```

This 12-by-64 matrix has full row rank. Write R_U and R_T for doubled-root row
matrices, so `G[U,T]=R_U R_T^T/4`. The T roots span dimension eight. If zA=0,
the second block forces zR_U=0; the first then forces z=0. This works over C
as well as Q and uses ordinary transpose, without a positivity assumption.

Eight T roots have integer determinant **1024**. A separate 12-by-12 minor of
**2A** has determinant **2048**. The second checker reconstructs both integer
matrices and verifies nonzero determinants modulo 101 (14 and 28). Nonzero
integer minors modulo a prime certify characteristic-zero nonvanishing; no
finite-field equality substitutes for the rational identity.

Restrict each added outer product to this rectangle. A nonzero restriction
has rank at most one and touches a nonorthogonal port pair, so its COPY rank
is at least one. A zero-charge term vanishes on the rectangle. Consequently

```
12 = rank(A) <= number of nonzero restricted terms <= sum of COPY ranks.
```

This excludes a complete +8 additive scalar correction for the named pair,
including a re-choice of the common correction basis. It does not claim that
12 is attainable. The rank argument is general under its stated hypotheses;
the finite source-bound application here is only this named pair.

## Correctly bound favorable screen

Retain PR #2308's local profile, width 73, 896 families, nine stages and center
charge 64. The unchanged authenticated `ceiling.relax` grants extra correction
rank the favorable idle rank 51. Access, restoration, hosting, precision and
even the natural base decoder's four extra COPY units are omitted. This is the
predecessor's fixed-profile model, not every possible plane-port redesign.

At target `35491136290869/20000000000000000`, 1.05 times the incumbent
packing-ceiling endpoint, the correct unpaid amount is `1+12/112 = 31/28`.
Exact outward intervals establish:

| Assumption | Upgraded ports | Added charge | Moment at target |
| --- | ---: | ---: | ---: |
| Predecessor's hypothetical screen | 16 | 8 | 0.999388703606489 < 1 |
| Correct port count alone | 12 | 8 | 0.999878251854348 < 1 |
| First rejected integer charge | 12 | 9 | 1.000015937299059 > 1 |
| Proved additive floor | 12 | 12 | **1.000428993633190 > 1** |
| Displayed cross-block factors | 12 | 40 | 1.004284186085082 > 1 |

The formula increases with added charge, so at most eight integer units fit;
the unavoidable twelve fail. Port overlap alone does **not** refute the 5%
screen. Redesigned local children, physical tariffs or a whole replacement
decoder require their own complete profile and coverage calculation.

## Reproduce and controls

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -O -B research/p112-shared-correction-cost-audit/verify.py
python3 -I -O -B research/p112-shared-correction-cost-audit/check_certificate.py
python3 scripts/research_package.py --package research/p112-shared-correction-cost-audit --check-only
python3 scripts/research_package.py --package research/p112-shared-correction-cost-audit
```

Expected primary output:

```
PASS_P112_SHARED_CORRECTION_COST_AUDIT union=12 parity_rank=1 correction_COPY=40 forbidden_entries=32 additive_COPY_floor=12 five_percent_screen=FAIL controls=10 no_new_kappa
```

Both mathematical checkers are read-only, need no network or Git, and accept
optimized Python. `verify.py --out NEW.json` writes only to an unoccupied path.
The package runner separately checks Git provenance. The primary replay took
about one second in the preparation environment; no speed claim is made.

Ten control groups cover coefficient gauge, omitted factor, changed coefficient,
line-only mask, double-counted ports, a valid repaired scalar matrix, the dirty
counterexample, all formal input columns, a dependent minor and a wrong label
map. Source pins and the entire deterministic receipt are checked. The second
implementation reconstructs the rectangle, uses modular minors and enumerated
binary spans, and checks wrong-mask/dependent-minor boundaries independently
of the primary executable. This is not independent human review.

Not checked: the predecessor's full 20,160-block census, another pair, optimal
additive COPY cost, a different full decoder or operator interface, native phases,
chronology, dirty helper restoration, global owners/idle profiles, precision,
all-size admission, hosted CI or the selected supplier's cold replay. The finite
dirty-target check is not the missing native/helper-boundary verification.

## Open next questions

1. Can a redesigned whole scalar decoder satisfy this mixed plane mask with an
   affordable bill? Start with the forced rectangle and solve the full fitting
   equations before pricing actual supports. The lower bound fixes the original
   map and counts additive corrections; a nonadditive decoder remains open.
   Stop if its complete favorable profile fails the desired moment.
2. Can an explicit block/operator interface realize physical sharing of the
   rational basis? Supply its arbitrary-dirty endpoint and complete tariff,
   then test the `(16,20)` counterexample. The missing interface theorem is
   the blocker; coefficient parity alone cannot supply the price.

Structured questions and task provenance are in [TASK.json](TASK.json).

## Credit and provenance

Cinna Davis (`1337isnot1337`) / PR #2308 owns the rational sharing identity,
frame census, label map and hypothetical screen. Philippe Van Velzen
(`philippeVV`) / [Discussion #2278](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278)
supplied the plane-upgrade question and additive-class screens. This is a new
explicit check of the named pair's pending scalar/cost interface, without a
priority claim over those screens. Adam Gall's retained paired-plane audit
supplies the endpoint distinction. `themilkman216` / PR #968, DreamingOfClouds
and the retained E8 lineage supply the root/decoder model; Douglas Colkitt
supplies the interval engine. Rohan Arun, Jeremy Kothe and Hao Yan retain
selected-source credit. The foreign certificate is unchanged; see [NOTICE.md](NOTICE.md).

Base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4;
coordination in Discussion #2278. [SOURCES.json](SOURCES.json) pins the input
bytes, Git blobs, predecessor head and certificate origin. Only this new
package changes; all predecessor inputs and the selected record are preserved.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. Derivation, implementation, checking and writing were AI-assisted;
no independent human review is claimed.
