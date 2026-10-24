# Rigidity of nine E8 totals at coordinate hyperplanes

## Scope

Repository inspected: `wht-power-saving-lean` at commit `9c94857bbaee886f8649edee0bc2d3c738f9555e`.

This result uses the canonical rank-eight E8 coefficient space. It does not cover all fitting matrices or all sets of nine frames. It does not prove a global copy-cost floor of 72.

Let the 120 source indices consist of triples and pairs from nine points. For a triple T, set a(T) to its incidence vector, t(T)=1, and p(T)=a(T) over F_2. For a pair i<j, set a(P_ij)=e_i-e_j, t(P_ij)=0, and p(P_ij)=1+e_i+e_j over F_2. These definitions match the certificate ports.

Define the rational coefficient space

E = { T -> w dot a(T) : w in Q^9, sum_i w_i=0 }.

This is the space spanned by the eight totals a_k-a_8. It has dimension eight. The pair values w_i-w_j show that the map from zero-sum w to a coefficient function is injective.

Let F_i={p : p_i=0}. Suppose there are nine rational totals g_i such that:

1. g_i(T)=0 whenever p_i(T)=1;
2. the span of the nine g_i contains E.

Then, for each i, there is a nonzero rational c_i with

g_i(T)=c_i(a_i(T)-t(T)).

Each g_i has 64 nonzero coefficients. Their binary source labels span F_i. Thus no one of these nine totals can use a proper subspace of F_i, even if all nine coefficient vectors can change. The result excludes all single-total frame reductions within the nine coordinate hyperplanes.

## Link to the scatter matrix

The canonical fitting matrix is

B(S,T)=(a(S) dot a(T)-t(S)t(T))/2.

Set q(S)=a(S)-(t(S)/3)1. Since sum_i a_i(S)=3t(S), the coordinates of q(S) sum to zero. Direct expansion gives B(S,T)=q(S) dot q(T)/2. In particular, every row of B belongs to E.

For the pair source S=P_i8, where 0<=i<8, the row of B is (a_i-a_8)/2. These eight rows form a basis of E. Hence rowspace(B)=E exactly. Any factorization B=RG through nine retained totals has E contained in rowspace(G), as required by the proposition.

The nine canonical totals g_i=a_i-t do reconstruct B. Set

R_i(S)=(a_i(S)-t(S)/3)/2.

Their sum over i is zero. Therefore

sum_i R_i(S)g_i(T)
=sum_i R_i(S)a_i(T)
=(a(S) dot a(T)-t(S)t(T))/2
=B(S,T).

Thus the proposition concerns the coefficient space of the actual canonical scatter. It does not assume that the nine totals are the eight published totals plus one unused register.

The support condition is necessary for phase A in the current gcert format. Each source X_T starts at the binary line spanned by p(T). Each helper starts with zero coefficients of the X sources; its arbitrary initial dirt is a separate input. Frame moves only enlarge the frame, and every scalar gate uses one common frame for all of its ports. Induction over these moves and gates shows that a nonzero X_T coefficient in a register at frame U requires p(T) in U. Cancellation does not break this invariant. The checks for these rules are in the pinned [tools/gx/gx.py](https://github.com/jacobalansussman/wht-power-saving-lean/blob/9c94857bbaee886f8649edee0bc2d3c738f9555e/tools/gx/gx.py): the source starts, nested frame moves, common gate frame, and scalar replay. Therefore, if each of the nine retained frames is constrained to lie inside its coordinate hyperplane, the result forces that frame to equal the entire hyperplane. The sum of their dimensions, and hence their copy cost in this format, is 9*8=72. This does not exclude a design with other frames or a mechanism with frame moves that are not nested.

## Full-support lemma

Every nonzero element of E has source labels that span F_2^9.

To prove this, suppose w dot a(T) is zero whenever z dot p(T)=1, for a nonzero binary z. Let A be the support of z, and let s=|A|.

If s is even, the pair indices with one point in A and one outside A have z dot p=1. Their equations give w_i=w_j across the cut. Both parts are nonempty, so all nine coordinates of w are equal. Their sum is zero, so w=0.

If s is odd, the pair equations give one constant a on A and one constant b on its complement. If s=1, a triple with one point in A gives a+2b=0. The zero-sum equation gives a+8b=0. Thus a=b=0. If 3<=s<=7, a triple contained in A gives 3a=0. The zero-sum equation then gives b=0. If s=9, all coordinates are equal and their sum is zero. Thus w=0 in every case.

Every proper binary subspace is contained in a hyperplane. The claim follows.

The repository already states the resulting floor of 72 for eight totals at the canonical scatter. This lemma is an independent proof of that existing claim.

## Proof of the nine-total result

Let T be the span of the nine totals. Each total has support in a proper binary subspace. By the full-support lemma, E has no nonzero element with such support.

Since E is contained in T, T has dimension at least eight. If its dimension were eight, every g_i would be in E and hence zero. Therefore T has dimension nine. The nine totals are independent, and each has a nonzero image in the one-dimensional quotient T/E.

Scale each total by a nonzero rational number so that all nine images in T/E agree. These scale changes preserve support. Now g_i-g_j belongs to E for every i,j.

Write g_i-g_j=w dot a, where the coordinates of w sum to zero. For each k other than i,j, the triple {i,j,k} lies outside both F_i and F_j. Both totals are zero there, so

w_i+w_j+w_k=0.

The seven coordinates outside {i,j} have one common value c. The equation above gives w_i+w_j=-c. The zero-sum condition then gives 6c=0. Thus c=0, and w_i=-w_j. It follows that

g_i-g_j=alpha_ij(a_i-a_j).

For three distinct indices, use (g_i-g_j)+(g_j-g_k)=g_i-g_k. The coefficient map on zero-sum vectors is injective. Comparison of its i,j,k coordinates shows that alpha_ij=alpha_jk=alpha_ik. Hence there is one common alpha and

g_i=g_0+alpha(a_i-a_0).

For each source index, choose an i with p_i=1. Such an index exists because every port is nonzero. At that source, a_i=t: both are one for a triple that contains i, and both are zero for a pair whose binary label contains i. Since g_i=0 there, g_0=alpha(a_0-t). Therefore

g_i=alpha(a_i-t).

The common alpha is nonzero, because the totals span a space that contains E. Undo the individual scale changes to obtain the stated result.

For each i, a_i-t is nonzero on the 56 triples that omit i and on the eight pairs that contain i. Its support therefore has size 64. The weight-three labels on the other eight points span all of F_i: their pairwise differences span the even-weight subspace, and one triple supplies an odd-weight vector. Thus the binary support rank is eight.

## Independent finite checks

The `coordinate/coordinate_totals_rigidity.py` file uses only the standard library. It imports no repository module. It checks the 120 certificate ports against the definitions above.

It also checks the exact linear equations for nine supported totals. After quotient normalization, write g_i=f+e_i, with e_i in E, and choose e_0=0. There are 64 rational variables for e_1,...,e_8. If a port lies outside both F_i and F_j, impose (e_i-e_j)(T)=0.

For the nine coordinate hyperplanes, the equation matrix has rational rank 63. Its kernel has dimension one and gives the totals t-a_i. An independent modular elimination gives rank 63 over both F_101 and F_103.

To reduce F_0 by one dimension, add a normal b with b_0=0. A nondegenerate reduced frame requires b to have odd weight. The stabilizer that permutes the other eight coordinates gives four cases, with weights 1, 3, 5, and 7. Their orbit sizes are 8, 56, 56, and 8, for a total of 128. Each case has rational rank 64 and zero kernel. Both modular checks also give rank 64. This covers all 128 nondegenerate seven-dimensional subframes of F_0. Permutation of the nine points gives the same result for every other F_i.

The analytic result is stronger: it excludes every proper subspace of every F_i, including degenerate subspaces, and permits changes to all nine coefficient vectors.

Run from the repository root:

```
python3 -B research/e8-small-redundancy/verify.py
```

The checker also verifies all 14,400 entries of the nine-total scatter identity with exact rational arithmetic. The saved JSON records the exact ranks, the modular ranks, the kernel, the support counts, the orbit sizes, and the certificate hash. These checks do not run Lean or verify the complete E8 circuit.
