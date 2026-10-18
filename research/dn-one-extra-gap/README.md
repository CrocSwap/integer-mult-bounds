# A sharp penalty for one extra D_n decoder term

For the full D_n line set, dense orthogonality pairing and fixed standard-coordinate one-extra family of [PR2518](https://github.com/CrocSwap/integer-mult-bounds/pull/2518), every genuinely `(n+1)`-term decoder costs at least

```text
n(n-1) + delta_n,   delta_n = n-2 if n is odd, n-1 if n is even,
```

for every integer `n>=3`, every real direction a and every real parameter lambda. This is sharp. The only baseline-cost cases are zero extra term or exact replacement of one original coordinate term. Thus the finite D4/D5 minima equal to the number of lines in PR2518 are replacement cases, not useful overcomplete ties. The new result is the **strict gap and equality classification over all real parameters and all dimensions**. It retires further direction searches within this exact full-set family.

This does not replace the broader D5 all-term floor or D4/D6 realization floors of [PR2277](https://github.com/CrocSwap/integer-mult-bounds/pull/2277). It adds a sharper conclusion for this particular one-extra family. No supplier, new kappa, native cost or arbitrary-pairing result is claimed.

## Exact contract

Use one representative `e_j+e_k` and `e_j-e_k` for every `j<k`. The matrix X consists of these `v=n(n-1)` rows. PR2518 uses `2X`; uniform scaling does not change supports or pairing ranks. Let `M=XX^T`, and let the binary matrix B have diagonal 1 and off-diagonal 1 exactly for orthogonal roots. Every term `(p,q)` costs `rank_F2 B[supp(p),supp(q)]`, with an empty support costing zero.

The fixed family is

```text
p_i = X e_i, q_i = X b_i, b_i = e_i - lambda a_i a  (1<=i<=n),
p_* = X a,   q_* = lambda X a.
```

Its sum is M, since `sum_i e_i b_i^T + lambda aa^T = I`. A **genuine `(n+1)`-term member** means all these rank-one terms are nonzero: `lambda!=0`, `a!=0`, and every `b_i!=0`. This includes the sharp example below with a new two-coordinate direction. The result does not assume independent or distinct directions among all n+1 terms.

The main theorem does not cover punctures, a different admissible B, moving the original p_i frame, arbitrary `(n+1)`-term factorizations, factors outside the root code, or other root systems. It is a local cost obstruction before copies, physical frames, retention, hosting and restoration are priced.

## 1. Exact star-rectangle price

Write `S_i=supp(Xe_i)` and `T_b=supp(Xb)`. For n>=3,

```text
rank B[S_i,T_b] = 0                   if b=0;
                  n-2               if n is odd and b=c e_j, c!=0, j!=i;
                  n-1               otherwise.
```

Here is an all-parameter proof. The two rows associated with the two signs on an edge `{i,j}` agree on **every** column of B: they see their own edge as 1, an edge sharing exactly one endpoint as 0, and a disjoint edge as 1. Compress these duplicate rows to n-1 rows labelled `j!=i`. Columns on edge `{i,j}` are the standard vector e_j; columns on an edge `{j,k}` avoiding i are `1+e_j+e_k` over F2. Thus the rank is at most n-1.

If `b_i!=0`, at least one of `b_i+b_j` and `b_i-b_j` is nonzero for every j, so all standard columns occur. If `b_i=0`, put `J=supp(b)` (excluding i). All standard columns e_j with j in J occur. If `|J|>=2`, pass to the remaining coordinates Z. A column with both endpoints in J supplies `1_Z`, because at least one of their sum and difference is nonzero. Columns joining J to each k in Z supply `1_Z+e_k`. They span all Z; an empty Z needs no extra column. Thus rank is n-1.

The remaining nonzero case is `J={j}`. The supported edges are exactly the star at j. After ordering rows and columns the compressed matrix is

```text
[1] direct-sum (J_(n-2) + I_(n-2)).
```

For a k-dimensional vector x, `(I+J)x=0` forces `x=(sum x)1`. The nullity is one for odd k and zero for even k. This proves the displayed formula, including n=3. No finite direction alphabet is used.

## 2. Principal-support price

For every nonzero a,

```text
rank B[T_a,T_a] >= n-1;
rank B[T_a,T_a] >= n   if n is odd and |supp(a)|>=2.
```

Choose j with `a_j!=0`. For each k!=j at least one sign on `{j,k}` lies in T_a. Pick one such root per edge. Their principal block is `I_(n-1)`: distinct edges share j and hence are not orthogonal. This proves the first bound.

If support(a) has another coordinate k and n>=3, choose l distinct from j,k; at least one sign on `{k,l}` also lies in T_a. Its column against the chosen star has exactly n-3 ones. Adjoining this row and column to I yields Schur complement `1+(n-3 mod 2)`, which is 1 for odd n. Therefore the augmented n-by-n block is nonsingular over F2. This proof does not assume the chosen roots form an orthogonal frame over the reals.

## 3. Sharp strict gap and equality cases

Let `s=|supp(a)|`, and first assume a genuine member.

For even n, every nonzero b_i has price n-1 by section 1, and the extra term has price at least n-1 by section 2. The total is at least `n(n-1)+(n-1)`.

For odd n, a price drop to n-2 requires `b_i=c e_j` with j!=i. Necessarily `a_i!=0`, `1-lambda a_i^2=0`, and all nonzero coordinates of a lie in `{i,j}`. Since b_i is nonzero, this requires s=2. There are at most two such dropped coordinates. If s=2, the extra price is at least n, so the total is at least `n(n-1)-2+n`. If s>=3, none drops and the extra price is at least n. If s=1, every b_i remains a nonzero multiple of its own coordinate (genuineness), and the extra price is n-1. Both cases also exceed the claimed minimum.

The bound is attained in every dimension by

```text
a=e_1+e_2, lambda=1;
b_1=-e_2, b_2=-e_1, b_i=e_i for i>=3.
```

For the extra support, retain the sole supported sign on edge `{1,2}`, and compress the duplicate sign pairs on the edges from `{1,2}` to its k=n-2 outside vertices. Its binary principal matrix is

```text
[1] direct-sum [[I_k, I_k+J_k], [I_k+J_k, I_k]].
```

Elimination gives rank `1+k+rank((k mod 2) J_k)`, equal to n for odd n and n-1 for even n. Together with section 1, the total is exactly the stated formula. All n+1 terms are nonzero. For D3/D4/D5/D6 the sharp genuine costs are respectively **7,15,23,35**, versus baseline **6,12,20,30**.

Finally, if lambda=0 or a=0, the extra term vanishes and the original coordinate decoder costs n(n-1). Otherwise some b_i vanishes if and only if `a=c e_i` and `lambda c^2=1`. Then precisely one old term disappears and the extra term replaces it at price n-1, again giving baseline. Every other member is genuine and has the strictly positive gap above. These are exactly all baseline equality cases. The proof makes no assertion for n=1 or n=2.

## Source binding and verification

[DEPENDENCY.json](DEPENDENCY.json) preserves exact PR2518 README, source and certificate bytes at `5ccad6aa04409ee2805d5638aa0fc84c76bbb881`. Its source explicitly uses standard coordinates H=I for D_n. After every source pin passes, the checker extracts only the six named geometry/support-cell definitions from the source AST. It checks the doubled-root convention, compares source support cells with independent full binary rank calculations, and replays the recorded D4/D5 minimum witnesses as nongenuine replacements. It does not rerun or claim the predecessor's complete census.

```sh
python3.12 -I -B scripts/research_package.py --package research/dn-one-extra-gap
python3.12 -I -O -B research/dn-one-extra-gap/check.py
```

[RESULT.json](RESULT.json) retains all 360 rational family fixtures for n=3..12, both sharp and degenerate cases, and exhaustive ternary-vector star/principal checks for n=3..6. These checks support the implementation; the preceding proofs establish the universal real-parameter result. A separate checker imports no producer code and reconstructs all root rows, Boolean pairings, full Gram identities and prices for the 180 fixtures in n=3..7 using row-list elimination instead of integer bit pivots. It also checks the two parity block formulas for k=1..17.

Six semantic controls exercise omission of the extra bill, the zero-old-term exception, changed pairing, punctures, parity and a wrong extra coefficient. Git-free optimized replay verifies unchanged files, typed receipt corruption, source rejection before AST execution and output overwrite refusal. Default checks write nothing; `check.py --emit NEW_PATH` refuses existing files. Sources are pinned by SHA-256 and Git blob; [SOURCES.json](SOURCES.json) pins current main `b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority revision 5. The selected frontier is unchanged. No human review, proof-assistant proof or hosted CI pass is claimed.

## Decision and resource limits

The revision-5 family gate decision is **pause this full D_n standard-coordinate one-extra search family**. Even before unpriced native work, every genuine extra term strictly worsens its dense abstract bill. The new bound removes no physical obligation; it tells a director that wider direction searches cannot improve this local family. A different pairing, moving frame or punctured contract would reopen a different question and require its own complete cost ledger. No downstream implementation campaign is proposed.

Python uses managed allocation and arbitrary precision arithmetic. Loops are bounded by 12 coordinates/132 lines, ternary vectors through dimension six, 360 rational fixtures, and the retained source-cell examples. The isolated exports are verification artifacts, not a fixed-workspace native implementation. Exact rational arithmetic, a separate elimination representation and effective failure controls mitigate implementation risk; no native speed or allocation bound follows.

## Open next questions

Can changing the dense pairing or moving the original factor frame produce a lower fully charged decoder? First exhibit one exact non-replacement factorization that falls outside this theorem, then price its common pairing and physical boundary. The blockers are arbitrary-pairing consistency and the complete consumer/restoration ledger. Punctures also change the forced-star proof; simply choosing new values of a or lambda does not.

## Credit

Aaron Wang with opencode supplies PR2518's finite screen, source convention and exact minimum fixtures. Its one-extra identity and support-cell method credit 1337isnot1337's PR2240 and transvection work PR2247. DreamingOfClouds supplies the model, dense pairing and root-code floors in PR2125/2228, and PR2277 already proves the broader D5 floor for arbitrary term counts and D4/D6 realization floors. The pinned predecessor README preserves the geometry and decoder lineage. This strict-gap theorem and independent checks were prepared by ywz65 with substantial OpenAI Codex assistance; new work is Apache-2.0. No predecessor census, general lower bound or native construction is represented as newly discovered here.
