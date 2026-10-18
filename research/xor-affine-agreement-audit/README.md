# Sharp affine agreement for arbitrary XOR masks

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in the proof, implementation, verification, and writing. October 13, 2026. New material is Apache-2.0 under the repository license. This is a research audit; no new kappa is claimed.

The historical [coded-carry audit](../../docs/research/coded-carry-audit.md), section 4, bounds agreement between separated-bit XOR and an affine address map. This package extends the lemma to arbitrary masks and shows exactly how its sharp bound depends on the mask. The earlier lemma remains valid in its stated domain. This does not reopen the closed construction search or supply a faster movement algorithm.

## The exact statement

Let L >= 1, N = 2^L, and 0 <= M < N. Write s for the number of set bits of M in positions 0 through L-2, t = L-1-s, and m = min(s,t). The top bit is excluded. Then

    max over 0 <= a,b < N of #{0 <= y < N : y XOR M = ay+b (mod N)}
        = 2^(L-m).

The result includes even slopes, as required when a coordinate of a larger affine slot map is examined. An invertible slope, either +1 or -1, attains the maximum. The minimum number of affine graphs whose union covers every target point (y, y XOR M) is exactly 2^m. Graphs may contain extra points; address-dependent masks can select their target fibers.

Under the historical fixed-bank circuit's at-most-2^k affine-path premise, any such implementation with k charged movement gates therefore has k >= m. The sharp graph count is not a proof that m movement gates suffice. When m=0, the argument gives no positive movement lower bound.

## Proof for every L

Set sigma_i=-1 where bit i of M is set and sigma_i=+1 otherwise. For the bits y_i of y,

    (y XOR M) - ay = M + sum_i (sigma_i-a) 2^i y_i (mod 2^L).

We use the following elementary fact. Weights with distinct 2-adic valuations, all below L, have distinct binary subset sums modulo 2^L. In a nonzero difference of two subset sums, the term with the smallest valuation has coefficient +1 or -1. Every other term has a strictly larger valuation, so the difference cannot vanish modulo 2^L.

If a is even, all sigma_i-a are odd. The L weights have valuations 0,...,L-1. Consequently every offset b has exactly one preimage.

If a=1 modulo 4, choose the s selected coordinates below the top bit. Their coefficients -1-a have valuation one, so their weights have distinct valuations i+1 < L. Fixing every other input bit leaves at most one assignment to these s coordinates for a given b. Agreement is at most 2^(L-s).

If a=3 modulo 4, use instead the t unselected coordinates below the top bit. Their coefficients 1-a have valuation one. The same argument gives agreement at most 2^(L-t). These cases exhaust all possible slopes and give the global upper bound. For L=1, s=t=0 and the argument is still valid.

For a=1, only selected coordinates contribute nonzero weights. The selected top coordinate, if present, contributes -2^L and vanishes modulo N. Exactly 2^s offsets occur, each on 2^(L-s) inputs. In particular b=M attains that size.

For a=-1, only unselected coordinates contribute. The top coordinate again vanishes, now as +2^L. Exactly 2^t offsets occur, each on 2^(L-t) inputs, including b=M. Choose the smaller of s and t to attain the upper bound.

Each affine graph covers at most 2^(L-m) target points, so at least 2^m graphs are necessary. The offsets of the chosen +1 or -1 slope give exactly that many disjoint target fibers and cover all N points. More explicitly, these offsets are M-2z over subsets z of the selected lower coordinates, or M+2z over subsets of the unselected lower coordinates, reduced modulo N. This proves the graph-cover statement.

The same support argument gives 2^k >= 2^m. Pointwise linear mixing and cancellation introduce no new address graph; a required nonzero target entry must occur on some path. This consequence inherits the original fixed-domain, equal-volume, affine-path assumptions. Recursive volume splitting, proper-subfield primitives, domain changes, or nonlinear backward dependence remain outside its scope.

## Periodic masks and concrete boundaries

For M=sum_j 2^(rho+jK), with n >= 1, L=nK, and 0 <= rho < K, the affine-path movement lower bound m is:

| Domain | m |
|---|---:|
| K >= 3 and rho <= K-2 | n |
| K >= 3 and rho = K-1 | n-1 |
| K = 2, either offset | n-1 |
| K = 1 | 0 |

Thus the former rho <= K-3 hypothesis can be relaxed by one position when K >= 3. The top-position case loses one constraint. The K=2 exception already recorded in the predecessor follows from the complementary slope branch.

All following counts are exact for L=6:

| Mask M | Maximizing (a,b) modulo 64 | Agreement | False bound rejected |
|---:|---|---:|---:|
| 32 | (1,32) | 64 | 32: counting the top bit |
| 15 | (63,15) | 32 | 4: ignoring the complement |
| 36 | (1,36) | 32 | 16: retaining n at rho=K-1 |
| 21 | (63,21) | 16 | 8: dropping the K=2 exception |

These are counterexamples to the listed overextensions, not counterexamples to the earlier scoped lemma. Assignment seed 60 selected this audit from three candidates and the L=6, K=3, rho=2 boundary regression. Exhaustive coverage does not depend on a random search.

## Reproduction and evidence

From the repository root, with Python 3.9+ and only the standard library:

    python3 -I -B research/xor-affine-agreement-audit/verify.py

Expect `PASS_XOR_AFFINE_AGREEMENT` followed by `PASS_XOR_AFFINE_INDEPENDENT`.

The primary checker covers every mask, every residue slope (including even slopes), and every offset for 1 <= L <= 8: 510 masks, 87,380 mask/slope pairs, and 19,173,960 exact agreement counts. It checks the separate slope bounds, explicit maximizers, and optimal graph covers. Its stopping rule is completion of this entire finite domain. Forty periodic-mask controls verify the displayed formulas and cover witnesses through L=16. Eleven negative controls include the four mathematical overextensions and corrupt histograms/covers.

The independent implementation imports no project code and counts solutions by a least-significant-bit multiplication/carry automaton, rather than enumerating y. It recomputes all 299,592 counts through L=6 and matches the complete primary histogram digests. Its negative control distinguishes modular equality from integer equality: for (L,M,a,b)=(6,15,63,15), there are 32 modular solutions but only one with final carry zero.

`CERTIFICATE.json` and `INDEPENDENT.json` record deterministic coverage and counts. SHA256 covers all histogram cells, including zeros, in the documented order. Finite computation supports the written universal proof; it is not a formal proof of that theorem or the multiplication theorem.

## Provenance and limits

Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. `SOURCE.json` pins five predecessor files. Credit Douglas R. Colkitt's coded-carry valuation/path argument and direct-selected-XOR cost analysis, both with their original OpenAI Codex disclosures. The new material is the arbitrary-mask classification, exact graph-cover size, complete periodic boundary table, and independent carry counter. No claim of priority outside this repository is made.

The selected result at the base is conditional kappa `0.001661960547713947`, from Jonathan Capalbo's #942 construction and its credited dependencies. This package changes neither it nor `upstream/`. It establishes no supplier, physical tape implementation, recursive cost improvement, or analytic transfer. The historical audit's closed-search decision is retained.

No pinned sprint coordination issue existed; `CLAIM.json` records the local claim. Related open #773 audits a different packed-rotation repair map; #1046 concerns GF(2) decoder ranks. Neither is used as a dependency. The scoped validation and final overlap refresh are recorded in `VALIDATION.json`.
