# H4 block fitting rank and root-linear centre cost

I certify the block fitting rank of the 60 H4 root lines as **15k over every field**. I also prove a **52-unit COPY lower bound** for root-linear scalar factorizations of their Gram matrix, with any finite number of terms. Under the retained one-unpaid-coordinate staging and halving conditions, these bounds imply **a < 0.001** even with favorable packing. This rules out this H4 supplier class as an improvement over the selected complex primitive. I do not construct a supplier or improve the multiplication exponent.

The result concerns new port geometry relative to the selected E8 unit. The all-field block theorem is independent of the supplier accounting; the copy theorem retains the H4 root-linear decoder interface. I make no claim of literature priority.

## Geometry and fitting convention

Put phi = (1 + sqrt(5))/2. Generate the 120 doubled roots from

- all permutations of `(±2,0,0,0)`;
- all sign choices in `(±1,±1,±1,±1)`;
- all even permutations of `(0,±1,±phi,±(phi−1))`.

Identify opposite roots. For reproducible indices, represent `a+b*phi` by the integer pair `(a,b)`, keep the lexicographically larger of each vector and its negative, and sort the 60 survivors. Write R for these rows divided by two and N = R R^t. Thus N has rank four and unit diagonal.

A block fit B over a field F has 60-by-60 blocks of size k, with `B_ii=I_k` and `B_ij=0` whenever `i != j` and `N_ij != 0`. Symmetry is optional. A “zero clique” below means a set of pairwise **nonorthogonal** distinct roots, so its principal block in B is an identity matrix.

Denney et al. give these coordinates and the 600-cell interpretation in [The Geometry of H4 Polytopes, section 2](https://arxiv.org/html/1912.06156v1). Bao et al. give the root-matroid flat census in [Matroid automorphisms of the root system H4, section 3](https://arxiv.org/html/1005.5492v1). I recompute the finite geometry used below.

## Exact block rank: 15k

In characteristic two, use these five zero cliques:

```text
C1 = 8 9 14 23 24 26 27 28 35 39 40 43 44
C2 = 2 8 11 22 24 26 28 33 35 39 44 48 51
C3 = 7 9 10 12 14 18 23 27 40 42 43 44 52
C4 = 0 2 5 11 12 19 22 33 39 45 48 51 55
C5 = 0 5 7 10 12 18 19 22 23 42 45 52 55
T  = 12 22 23 39 44
```

Their symmetric difference is T, which is also a zero clique. Factor a rank-r block fit as `B_ij=X_i Y_j`, with `X_i` of shape k-by-r and `Y_i` of shape r-by-k. Define `P_i=Y_i X_i`. Since `X_i Y_i=I_k`, each P_i is a rank-k idempotent. Distinct vertices in a zero clique satisfy `P_i P_j=0`.

For a zero clique C, the idempotent `S_C=I+sum_{i in C} P_i` has rank `r−|C|k`. In characteristic two, the five-clique identity gives `sum_j S_Cj = S_T`. Rank subadditivity gives

```text
r − 5k <= 5(r − 13k),  hence r >= 15k.
```

This uses Thiago Goulart / @Tuafo's idempotent clique-sum method from [PR1744](https://github.com/CrocSwap/integer-mult-bounds/pull/1744). The H4 five-clique certificate is the new finite instance here. The proof applies to asymmetric blocks and all k; it uses no solver result.

For characteristic other than two, extend F to contain a root of `x²−x−1`. Evaluate the doubled coordinates there and form `G=R R^t`. Coordinate identities give diagonal one, rank at most four, and zeros on the original orthogonal pairs. Consequently

```text
B Hadamard (G tensor J_k) = I_(60k).
```

For matrices A and C, tensoring their rank factorizations proves `rank(A Hadamard C) <= rank(A) rank(C)`. Since `rank(G tensor J_k) <= 4`, we obtain `60k <= 4r`. Field extension preserves the rank of B. This includes characteristic five, where the polynomial has a repeated root; only evaluation at a root and invertibility of four are needed.

Fifteen disjoint orthogonal tetrads attain 15k: put `J_4 tensor I_k` on each tetrad and zero elsewhere. `verify.py` lists and checks the partition. Therefore the block minimum is exactly 15k over every field. Equivalently, the fractional Haemers bound of the orthogonality graph is 15 over every field, with this fitting convention.

## Support lemma and COPY floor

For a nonzero complex vector alpha, let `S_alpha={i : r_i^t alpha != 0}`. I check the following finite premises:

1. For any two root-spanned hyperplanes with nonorthogonal normals, their common complement contains a zero clique of size 13.
2. For any two root-spanned hyperplanes, their common complement contains a zero clique of size at least 10.

I enumerate independent triples to obtain all 1,320 hyperplanes, then close their sets under the 60 exact root reflections. The four orbits have sizes 60, 360, 600 and 300; their flats contain 15, 6, 4 and 6 rays. For one representative of each orbit, I check all 1,320 partners. Reflection transport covers all ordered pairs:

| Normal pairing | Ordered pairs | Checked clique size |
|---|---:|---:|
| Nonzero | 1,659,480 | 13 |
| Zero | 82,920 | 10 |

To pass from root-spanned hyperplanes to arbitrary alpha and beta, let Z_alpha span the roots on which alpha vanishes. Its dimension is at most three. Extend a root basis of Z_alpha to a basis of four roots. The dual vectors corresponding to the added roots form a basis of `Z_alpha^perp`; each is the normal of a root-spanned hyperplane containing Z_alpha. Do the same for beta. If `alpha^t beta != 0`, at least one pair of these normals has nonzero pairing. Otherwise bilinearity would force `alpha^t beta=0`. The finite premise therefore supplies a zero clique inside `S_alpha intersect S_beta` of size 13 when the pairing is nonzero, and at least 10 without that condition. This argument also covers complex coefficients and lower-dimensional zero sets.

Let B now be any scalar binary fit. The clique principal minor lies in the rectangular restriction `B[S_alpha,S_beta]`, so

```text
rank_F2 B[S_alpha,S_beta] >= 13 if alpha^t beta != 0;
rank_F2 B[S_alpha,S_beta] >= 10 for nonzero alpha,beta.
```

Consider a root-linear factorization

```text
N = sum_{ell=1}^q (R alpha_ell)(R beta_ell)^t,
C = sum_{ell=1}^q rank_F2 B[S_alpha_ell,S_beta_ell].
```

Delete zero terms. Since R has full column rank, exactness gives `sum alpha_ell beta_ell^t=I_4`, so q is at least four. If q=4, the two square factor matrices are inverse transposes, and each `alpha_ell^t beta_ell=1`. Thus C is at least 52. If q>=5, taking traces gives `sum alpha_ell^t beta_ell=4`, so at least one pairing is nonzero. Then `C>=10q+3>=53`.

This proves C>=52 with no upper bound on q. Every minimal four-term factorization of N lies in this root-linear class. For more than four terms I retain that hypothesis; I do not cover additional factors outside the root column spaces whose contributions cancel.

## Consequence under the retained staging model

Use the coverage and compressed-window assumptions from [format-limits, A.1](../format-limits/README.md), and the halving condition from [complex-local-word-ceiling](../complex-local-word-ceiling/README.md). For T replicas and s stages, with one unpaid coordinate per live family,

```text
h >= 15,  m >= 1+s(h−1) >= 14s+1,
W >= 60T(s−1),
D = mW − sum_r n_r r <= T[60(s−1)−52s] = T(8s−60).
```

If D<=0 there is no positive saving. Otherwise put delta = D/(mW). For all real s>1,

```text
delta <= (8s−60) / [60(14s+1)(s−1)] < 1/2900.
```

To verify the strict bound, subtract `2900(8s−60)` from the denominator. The resulting quadratic is `840s²−23980s+173940`; it has positive leading coefficient and discriminant −9,398,000.

If each paid child satisfies `2r²<m²`, the normalized moment at a>=0 is at least

```text
(1−delta) 2^(a/2) > (2899/2900) 2^(a/2).
```

At `a=1/1000`, this exceeds one: the exact integer check is `2*2899^2000 > 2900^2000`. Thus **a<0.001** is necessary. I allow all paid mass the largest favorable child ratio and omit extra implementation charges, so actual charges cannot evade this upper bound.

I do not apply this conclusion to changed coverage laws, multiple unpaid coordinates, nonlinear decoders, or factor spaces outside the stated class. I also do not infer a universal lower bound for integer multiplication.

## Verification

Run with Python 3.12 or later, standard library only:

```sh
python3 -I -O -B research/h4-root-linear-copy-floor/verify.py
python3 scripts/research_package.py --package research/h4-root-linear-copy-floor
```

I reconstruct the coordinates, check the five-clique certificate and the rank-15 partition, enumerate the hyperplanes and reflection orbits, and validate 5,280 support witnesses. The search routine only supplies a clique; a separate check validates its support and all pairwise inner products. I verify the budget with integers and reject eight corrupted witnesses or hypotheses. Exceptions remain active under `-O`. The verifier imports no search solver, predecessor verifier or stored result and writes no files.

The replay checks finite premises. A reviewer must also assess the written linear-algebra and accounting implications. I have not claimed independent human review or formal verification of the multiplication theorem.

I ran the registered replay with Python 3.12 and the isolated optimized replay with Python 3.14.6. Both passed with support-receipt SHA256 `8b0a00c1e8bc012e7f9b620e0ed2c23384f08ea51f7a023f03279e34e9704ab6`.

## Open next questions

- Can factors outside the H4 root column spaces lower the complete cost? Start with an explicit overcomplete factorization and its binary fit, then price each support and the restored word. The present proof does not cover cancellations between such external factors.
- Can a different staging interface obtain multiple unpaid coordinates from these ports? Start by deriving its coverage identity and all frame charges. The exact block rank 15k remains applicable to the same fitting graph, but the moment argument would need new hypotheses.

## Attribution and coordination

Jose Manuel / @jmbarrancoml prepared this package with substantial OpenAI Codex assistance in the research, proof, code and prose. Read-only mathematical subagents supplied the initial geometry screen and five-clique witness. The root agent checked that witness and implemented the support census and verifier. Apache-2.0.

Credit: Denney et al. for the coordinates and A5 geometry; Bao et al. for the hyperplane census; Thiago Goulart / @Tuafo, PR1744, for the clique-idempotent method; Joel Pulikkan / @GamingPuzzled, PR620, for the related extension-ring screens; DreamingOfClouds, PR595, for the format accounting; and the PR1012/complex-local-word-ceiling lineage for coverage and favorable moment comparisons. `SOURCES.json` pins repository provenance. I copied no predecessor implementation.

I coordinated the geometry change in [Discussion1860](https://github.com/CrocSwap/integer-mult-bounds/discussions/1860). The initial complete overlap check covered 519 open PRs and 485 Discussion records at 11:56–11:58 UTC on 2026-10-14 and found no precise geometry match. I treat that search as a scope check, not evidence of literature priority.
