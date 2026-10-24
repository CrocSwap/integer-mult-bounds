# Exact common-chart multiplicities for square-zero radical targets

This scoped counting proof answers Open next question 1 of Nick Petalas's [PR #4766](https://github.com/CrocSwap/integer-mult-bounds/pull/4766): how many common projective chart pairs does each radical target admit? The [retained question and source theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/radical-all-field-count/README.md) are fixed at canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf. The result refines the existing reachable/unreachable count. No new kappa is claimed.

Let K=F_q, where q is any prime power. Let R=K plus J be a split central unital K-algebra, with J^2=0 and finite d=dim_K J. A target M is a two-by-two matrix with entries in J. A chart pair means one projective nonzero row [phi] and one projective nonzero column [v] over K. It is admissible when phi M v=0. Let k(M) be the number of these pairs. Pairs that differ only by nonzero scalar factors are counted once.

Put z=q^d and A_r(z)=product_(0<=i<r)(z-q^i), with A_0=1. Across all dimensions, exactly six values of k(M) can occur. At each fixed d their target counts are:

| Admissible pairs k | Number of targets |
| --- | --- |
| 0 | A_4+(q^3-q)A_3+q^2(q-1)^2 A_2/2 |
| 1 | (q+1)^2 A_3+(q+1)^2(q-1)A_2 |
| 2 | q^2(q+1)^2 A_2/2 |
| q+1 | 2(q+1)A_2+(q^3-q)A_1 |
| 2q+1 | (q+1)^2 A_1 |
| (q+1)^2 | 1 |

Here all A_r have argument z. Some counts vanish at small d. The six displayed k values are distinct for every q>=2. Products with r>d vanish, and the table includes d=0. The zero target is the unique target with all (q+1)^2 admissible pairs.

For q=3,d=2, the counts at k=0,1,2,4,7,16 are respectively 864,1536,3456,576,128,1. Thus 1,536 targets have exactly one common chart, while no target has exactly three. A uniform random projective pair succeeds with probability k/(q+1)^2 for a fixed target. This probability statement does not supply a physical sampler or its cost.

**Proof.** Choose a basis of J and write M=sum_l A_l epsilon_l, with A_l in V=M_2(K). Let S be the orthogonal complement of span(A_l) under the nondegenerate entrywise pairing on V. The admissible pairs are exactly the projective rank-one matrices in S: the matrix with entries phi_i v_j pairs with A_l as phi A_l v. The rank-one locus Q in projective three-space is the determinant quadric. It has (q+1)^2 points, parametrized by P^1(K) times P^1(K).

The following table gives, for each vector dimension s of S, the number of subspaces with each intersection size k=|P(S) intersect Q|:

| s | k : number of subspaces |
| --- | --- |
| 0 | 0 : 1 |
| 1 | 0 : q^3-q; 1 : (q+1)^2 |
| 2 | 0 : q^2(q-1)^2/2; 1 : (q+1)^2(q-1); 2 : q^2(q+1)^2/2; q+1 : 2(q+1) |
| 3 | q+1 : q^3-q; 2q+1 : (q+1)^2 |
| 4 | (q+1)^2 : 1 |

For s=1, projective points outside Q are the invertible matrices modulo scalars, of which there are |GL_2(K)|/(q-1)=q^3-q. For s=2, the projective lines contained in Q fix either projective factor, giving 2(q+1) lines. Two points on Q with neither factor in common span a line with exactly two points on Q: the determinant of a combination of their two rank-one matrices is a nonzero multiple of the product of the two combination coefficients. Counting such unordered pairs gives q^2(q+1)^2/2 secants.

Through each point of Q there are q^2+q+1 projective lines. Two lie on Q and q^2 are secants. The remaining q-1 lines meet Q only at that point. This gives (q+1)^2(q-1) tangents. The total number of projective lines in three-space is (q^2+1)(q^2+q+1), obtained by dividing the number of independent vector pairs by |GL_2(K)|. Subtracting contained lines, secants and tangents gives q^2(q-1)^2/2 external lines. This proof includes characteristic two.

A hyperplane is the kernel of one nonzero matrix functional, up to scalar. A rank-one functional restricts on Q to a product of two linear forms, so its zero set is the union of two ruling lines and has 2q+1 points. There are (q+1)^2 such hyperplanes. An invertible functional gives exactly one projective column for each projective row, hence q+1 points; there are q^3-q such hyperplanes. This proves the s=3 row. The other two dimensions are immediate.

For fixed S of dimension s, its orthogonal complement has dimension 4-s. The coefficient tuple (A_1,...,A_d) must span that fixed complement. Such tuples are full-row-rank (4-s)-by-d matrices and number A_(4-s)(q^d). Multiply each subspace count by this number and collect equal k values. The displayed target table follows. This is a complete finite-field proof, not extrapolation from examples.

**Evidence.** A standalone standard-library verifier directly forms each scalar matrix's projective bilinear-zero mask, intersects masks for every coefficient tuple, and counts the surviving pairs. It covers q=2 with d=0 through 4, q=3 with d=0 through 3, and q=4,5 with d=0 through 2: 1,065,033 target tuples. It independently enumerates 1,928 subspaces in unique reduced row-echelon form and counts their rank-one projective points. Both calculations agree with every cell of the table. Six controls cover predecessor calibration, one-chart targets, a forbidden chart count, F_4 versus integers modulo four, the common-chart condition, and the bounded field domain. Normal and optimized warning-strict CPython 3.12.14 runs pass.

Credit Nick Petalas's [PR #4766](https://github.com/CrocSwap/integer-mult-bounds/pull/4766) for the all-field reachability count and explicit multiplicity question, and his [PR #4745](https://github.com/CrocSwap/integer-mult-bounds/pull/4745) for the arbitrary-word square-zero reachability theorem. The [pinned reachability proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/square-zero-radical-reachability/README.md) supplies the paid-cost interpretation: k>0 gives exact formal cost two, while k=0 is unreachable at any word length. That theorem is cited, not independently re-audited here. ToikY's [PR #4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334) supplies the shared-chart interface; Wentao Li's [PR #4099](https://github.com/CrocSwap/integer-mult-bounds/pull/4099) supplies the right-vector alphabet. The finite-geometry incidence counts are classical; no general literature-priority claim is made.

**Limits.** Only radical targets, two roles, a scalar residue field and square-zero radical are covered. Separate charts for separate radical coordinates are not allowed. Native chart preparation, routing, precision, restoration, stock and the complete supplier/outer bill remain unknown. No selected cold replay, predecessor scientific suite, native build, Lean or Docker run was used. No independent human or proof-kernel acceptance is claimed. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/radical-chart-multiplicity
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_RADICAL_CHART_MULTIPLICITY`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Bind a restricted common-chart policy to a physical caller and price its choice and emission. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
