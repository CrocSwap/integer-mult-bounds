# Exact reachability of quadratic lifts of a split radical pencil

This scoped proof classifies every quadratic lift of one split two-role radical pencil over R=F_2[x,y]/(x,y)^3. It follows the cube-zero reachability question in Nick Petalas's [PR #4764](https://github.com/CrocSwap/integer-mult-bounds/pull/4764), while keeping its pure-quadratic cost-three target separate. No new kappa is claimed.

Let J=(x,y), l=x+y, and let Q=(q_ij) be any matrix with entries in J^2. Use the paid factors I+u v^T, with u in R^2 and v in F_2^2, and arbitrary free GL_2(F_2) maps. A word acts on all R^2 inputs. There are no additional roles. Put

```text
M_Q = [[x,y],[y,x]] + Q,
omega(Q) = q_11+q_12+q_21+q_22,
L = l J = span_F2{x^2+xy, xy+y^2}.
```

**The exact answer is cost(M_Q)=2 if omega(Q) is in L, and cost(M_Q)=infinity otherwise.** This is an all-word theorem in the stated alphabet, not a bounded search failure. Of the 4,096 lifts, exactly 2,048 have cost two and 2,048 are unreachable. Every lift has the same reachable image modulo J^2, so reachability in that quotient is not sufficient for reachability in R.

Only 512 lifts have an exact common nonzero base-field row/column pair phi M_Q v=0. A further 1,536 lifts are reachable with two factors despite having no such pair. Thus simply copying the square-zero common-zero criterion to this larger algebra also fails. For explicit examples, put all q_ij=0 except q_22. The choice q_22=x^2 is unreachable. The choice q_22=x^2+xy has cost two but no exact common base-field zero.

**Two-factor construction.** Let G=H=[[1,1],[0,1]], both in GL_2(F_2). They are their own inverses. Then N=G M_Q H has entries

```text
a=N_11=l+q_11+q_21,   N_12=omega(Q),
c=N_21=y+q_21,       d0=N_22=l+q_21+q_22.
```

If omega is in L, choose b in {0,x,y,x+y} with l b=omega. Since J^3=0, a b=l b. Therefore

```text
[[a,0],[c,1]] [[1,b],[0,d0-cb]] = N.
```

The two factors are I+(a-1,c)^T e_1^T and I+(b,d0-cb-1)^T e_2^T. The free maps G and H recover M_Q. Its scalar residue is zero, while one paid factor has residue rank at least one, even after free maps. Thus the cost is exactly two.

**All-word lower bound.** Every target in this family has determinant l^2=x^2+y^2, which is a nonzero element of J^2. Quadratic corrections cannot change it because J^3=0. Call a paid factor singular when its determinant is in J. An invertible paid factor has an invertible scalar residue. A singular paid factor has scalar rank exactly one: it fixes the nonzero kernel of its base-field right row and cannot have rank zero. The zero scalar residue of M_Q therefore requires at least two singular factors. Three singular factors would put the determinant in J^3=0. Thus any realizing word contains exactly two singular factors.

Each singular paid factor is equivalent, by invertible matrices over R, to diag(a,1), where a is its determinant in J. To see this, change its nonzero base-field right row to e_1^T by a constant conjugation. The factor then has form [[a,0],[c,1]]. Right multiplication by [[1,0],[-c,1]] gives diag(a,1). Collect all intervening invertible matrices. Every hypothetical realization must have

```text
M_Q = U diag(a,1) V diag(b,1) W,
U,V,W in GL_2(R),  a,b in J.
```

This is a relaxation for the lower bound; the construction above uses only the stated free GL_2(F_2) maps. Every unit in R is 1+j with j in J. Since ab is in J^2, multiplication by any such unit leaves ab unchanged. Taking determinants gives ab=l^2. Hence the upper-left entry of U^(-1) M_Q W^(-1) is ab V_11, which belongs to L.

Let r be the first row of U^(-1) and c the first column of W^(-1). Their scalar residues r_0,c_0 are nonzero. Because r M_Q c has no linear part, r_0 [[x,y],[y,x]] c_0=0. Over F_2 the only such nonzero pair is r_0=c_0=(1,1): the two coefficient matrices are I and the coordinate swap, whose unique common projective eigenline is span(1,1). This can also be checked directly on the three nonzero rows and columns.

Write r=(1,1)+r_1 and c=(1,1)^T+c_1, with r_1,c_1 in J in each component. Terms involving Q and one of these radical corrections, or involving two corrections and the linear pencil, vanish in J^3. Since the pencil sends (1,1)^T to (l,l)^T and (1,1) sends it to (l,l),

```text
r M_Q c = omega(Q) + l*(r_1,1+r_1,2+c_1,1+c_1,2).
```

Consequently its class in J^2/L is the class of omega(Q). But the normal-form corner above belongs to L. Thus omega(Q) must belong to L for every realizing word. Together with the two-factor construction, this proves the exact classification.

**Counts and the two lifting boundaries.** The four entries of Q have 12 independent binary coefficients. Membership of omega in L is one nonzero linear parity condition, because a quadratic A x^2+B xy+C y^2 belongs to L exactly when A+B+C=0. Hence exactly 2^11 lifts are reachable. An exact common base-field zero must use the unique first-order pair (1,1),(1,1), and its response is omega. The condition omega=0 imposes three independent linear equations, leaving 2^9=512 lifts. This proves both reported counts without extrapolation.

**Evidence.** The standard-library checker constructs the 64-element ring from its monomial table. For all 4,096 lifts it checks the fixed determinant, computes the exact two-factor criterion across all 18 projective row/basis choices using literal principal-ideal sets, and replays each of the 2,048 stated constructions as a matrix identity. It checks the obstruction class for all 256 linear row/column corrections on every lift: 1,048,576 covariance checks. Quadratic row/column corrections vanish from this calculation by J^3=0. It separately checks all 1,024 pairs of nonunit determinants, including the 64 pairs with the required product, and verifies the normal-form corner class for every ring scalar. Controls distinguish the two explicit lifts, exact common-zero counts, square-zero versus cube-zero multiplication, and the nonzero determinant premise. Normal and optimized warning-strict CPython 3.12.14 runs pass. These finite computations corroborate the written all-word proof.

Credit Nick Petalas's [PR #4764](https://github.com/CrocSwap/integer-mult-bounds/pull/4764) and [pinned cube-zero proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/cube-zero-three-factor/README.md) for the higher-nilpotency question and separate cost-three example. His [PR #4276](https://github.com/CrocSwap/integer-mult-bounds/pull/4276) and [pinned exact two-factor criterion](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/right-vector-two-factor-criterion/README.md) supply the finite criterion used for corroboration. His [PR #4776](https://github.com/CrocSwap/integer-mult-bounds/pull/4776) and [pinned pencil proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/split-radical-pencil/README.md) supply the square-zero split-pencil result and determinant lineage. The [square-zero theorem, PR #4745](https://github.com/CrocSwap/integer-mult-bounds/pull/4745), applies only under its original algebra hypothesis. Wentao Li's [PR #4099](https://github.com/CrocSwap/integer-mult-bounds/pull/4099) supplies the right-vector alphabet, and ToikY's [PR #4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334) supplies the common-chart context. Classical determinant and local-ring arguments retain their credit.

**Limits.** This classifies one binary first-order pencil with all its quadratic lifts. It does not classify arbitrary cube-zero targets, additional roles or other coefficient fields. In particular the predecessor's pure-quadratic target has determinant zero and can use three singular factors; the nonzero-determinant argument here does not apply to it. No predecessor executable or scientific census is imported or replayed. Native coefficient preparation, routing, restoration, precision, stock and the complete supplier/outer bill remain unknown. No selected cold replay, native build, Lean or Docker run was used. No independent human or proof-kernel acceptance is claimed. Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/cube-zero-lift-obstruction
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_CUBE_ZERO_LIFT_OBSTRUCTION`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Classify another first-order pencil or the determinant-zero cube-zero stratum before proposing a general reachability theorem. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
