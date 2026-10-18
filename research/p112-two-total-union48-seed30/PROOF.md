# Two-column retained loss at source union 48

This is a scoped exact matrix statement with a finite premise certificate. It
is not a formal proof of the multiplication theorem or a proof-assistant
theorem. The geometry, the separate-total COPY model and the added-term price
lemma are inherited (PR845, PR1432, PR1787, PR1827, PR1197, PR2382).

## Setting

`X` is the pinned integer `112 x 8` matrix, `l_t` the source labels and `v_i`
the dual labels of `research/p112-single-lift/reference-geometry.json`.
`S_j = supp(x_j)`, `|S_j| = 56`. The pairing rank is

    beta(d, s) = rank_F2 [(v_i . l_t)]_(i in supp d, t in supp s).

For reader `j` let `C_j` be the F2 span of the literal pairing rows
`t -> v_i . l_t` (`t in S_j`, `i in S_j`). For a port set `V` put
`K_j(V) = {c in C_j : supp c subset V}` and `g_j(U) = dim K_j(U)`;
`L(U) = sum_j g_j(U)` is the geometric loss of a deletion set `U`.

A two-column correction is `Y = X - W`, `W = Z A^t`, `Z` `112 x 2`, `A`
`8 x 2`, so `rank W <= 2` over `C`; `U` is the set of nonzero rows of `Z`. The
retained loss is `delta_j = 8 - beta(x_j, y_j)`.

## Finite premises (all checked by `verify.py`, no symmetry assumed)

P1. Each `C_j` has 256 words with weights `0^1 24^63 28^128 32^63 56^1`, and
the duals `{v_i : i in S_j}` span an 8-dimensional F2 space. Hence
`u -> (u . l_t)_(t in S_j)` is a bijection from the reader's dual span onto
`C_j`.

P2. For every ordered pair `j != k`, `|S_j cap S_k| = 24`; the cut
`C_jk = S_j cap S_k` is a word of both `C_j` and `C_k`; it is the only nonzero
word of `C_k` inside `S_j`; every other nonzero word of `C_k` has at least 12
ports outside `S_j`.

P3. The 112 source labels are distinct. On each of the 28 cuts, the product
`x_j x_k` takes the value `+1` on 12 ports and `-1` on 12 ports.

P4. Closed supports (unions of codewords) of each `C_j` up to size 48 are
enumerated completely by breadth-first union (any closed support is reached
through prefix unions, which only grow). Per reader: sizes 24..32 have
dimension 1; dimension 2 has sizes 36, 40, 44; dimension 3 has 44, 46, 48;
dimension 4 occurs only at size 48 (315 supports). No closed support has size
33..35.

## Reduction to configurations

Let `kappa_j` be the kernel of the pairing map of reader `j` against
`supp y_j`; `dim kappa_j = delta_j` (P1). For `u in kappa_j`, the word `c_u`
vanishes on `supp y_j cap S_j`. Off `U`, `y_j = x_j`, which is nonzero on
`S_j`, so `supp c_u subset U`, and `y_j = 0` on `supp c_u`. Let `P_j` be the
union of `supp c_u` over `kappa_j`. Then

* `P_j` is a closed support of `C_j`, `P_j subset U`,
  `delta_j <= dim K_j(P_j)`;
* `W[t, j] = X[t, j]` for every `t in P_j`.

**Condition N.** For every set `K` of at least three readers with `P_k`
nonempty, let `R_K` be the intersection of the `P_k`. Then
`X[R_K, K] = W[R_K, K]`, so `rank_Q X[R_K, K] <= 2`. This is necessary for
any two-column correction; it uses no reality, positivity, full-rank or
on-column hypothesis.

So the realizable retained loss is at most the maximum of
`sum_k dim K_k(P_k)` over configurations of closed supports with
`|union P_k| <= |U|` that satisfy N. N is monotone (adding a reader only adds
constraints), so depth-first search may prune on failure.

## Complete case split on the largest support `s = max |P_k|` (reader `j`)

* `s > 36`, or `s = 36` with cap 47. Every other `P_k` satisfies
  `|P_k \ P_j| <= cap - s < 12`. By P2 each word in `P_k` is then the cut
  word, so `P_k = C_jk`. The search runs over all closed `P_j` and all
  cut-reader subsets.
* `s = 36` with cap 48. All other closed supports with
  `|P_k| <= 36` and `|P_k \ P_j| <= 12` are enumerated (words and
  36-port planes).
* `s <= 32`. Every `P_k` is a single codeword (P4). All tuples of words
  from distinct readers with union `<= 48` are enumerated, with pairwise
  compatibility pruning.

The same split, with `L(U)` evaluated exactly for each union, gives the
geometric maximum. When `s > 36`, the union is a closed support of `C_j`, and
`L = dim K_j(U) + #{k : C_jk subset U}`.

## Results

| union cap | geometric max `L` | max loss passing N | price min | full-rank COPY floor |
|---|---|---|---|---|
| 47 | 5 | 4 | 6 | 66 |
| 48 | **8** | **5** | 6 | **65** |

At cap 47 this is an independent reproduction of PR2382's statements (geometric
maximum 5, rank-two bound 4, floor 66). The census of single-word unions also
matches PR2382 exactly: `2032, 280252, 9072, 42, 0` by reader-subset size.

At 48 the geometric maximum jumps to 8. For example, reader 0 has a
four-dimensional 48-port support containing four cuts: loss vector
`(4,0,1,1,1,1,0,0)`. There are also seven 8-reader single-word unions. Every
such configuration violates N: the recorded witness has a rank-3 integer minor
on rows `{0,1,2,3,12,13,14,15}` and columns `{0,2,3}`.

N-passing configurations with total loss 5 occur in shapes `4+1`, `3+1+1`,
`2+1+1+1` (lead dimension at least 2) and `1+1+1+1+1` (448 single-word
tuples). Nothing passes at 6 or more.

**Attainment.** Let `V` be the first four-dimensional 48-port support of reader
0 that contains a cut, here `C_01`. Take `Z = [x_0 1_V, x_1 1_(C_01)]`,
`A = [e_0, e_1]`. Both have rank 2, `U = V` has 48 ports, and `rank[X Z] = 10`.
The identity `XX^t = XY^t + (XA)Z^t` is checked on all 12,544 ordered pairs.
The exact retained COPY ranks are `(4,7,8,8,8,8,8,8)`, so retained loss is 5.
The added COPY ranks are `(8,7)`, giving a total bill of **74**.

So PR2382's "retained loss at most 4" bound, which PR2382 states only through
47, **does not extend to 48**: the two-column bound there is exactly 5. The
representative `A = [e_0, e_1]` lies in PR1197's disjoint-coefficient class;
the same `W = ZA^t` in an overlapping basis (`Z -> ZG`, `A -> A G^{-t}`)
keeps retained loss 5, but that representative's added bill was not computed.

**Floor.** In the full-rank on-column (PR1197 residual) case both added terms are nonzero. By the
inherited PR845/PR1432 price lemma, an added source with `m` active labels
has COPY rank at least `p(m) = min{r >= 1 : m <= 2^(r+1)}`. By P3,
`m_1 + m_2 >= 48`. The exhaustive integer minimum is `p(1)+p(47) = 6`. So the
COPY rank sum is at least `64 - 5 + 6 = 65` when `|U| = 48` (a lower bound,
not an attained minimum). The result does
**not** show that 65 is attained: the loss-5 witness costs 74. PR1197's
complementary rank-one/off-column reductions are inherited unchanged, as in
PR2382, so the general fixed-reader no-saving statement (COPY at least 64)
holds at union 48 as well.

**Partial sharpening for shape `4+1`.** Here `P_j` is a four-dimensional
48-port support, and `P_k = C_jk` must lie inside it, since the budget is 0.
In the full-rank case, `col Z = col W = span(w_j, w_k)`. On `C_jk`, a
combination `a w_j + b w_k` equals `a x_j + b x_k`.

- If `a` and `b` are both nonzero, it vanishes only where `x_j x_k = -a/b`.
  By P3 at least 12 of the 24 ports remain nonzero.
- If `b = 0`, the support has at least 48 ports.
- If `a = 0`, the support has at least 24 ports.

So both added sources have at least 12 active labels. With
`m_1 + m_2 >= 48`, the price minimum is then `p(16) + p(32) = 7`, and every
`4+1` correction has COPY at least `59 + 7 = 66`. This is a written
argument; verify.py machine-checks its premise P3 but not the constrained
price minimum 7 (independently recomputed by review). The shapes `3+1+1`,
`2+1+1+1` and `1^5` are not analysed this way. Hence the overall floor
stated is still 65.

## Scope

All helpers, source access, frames, restoration and recursion are free in this
screen. Only the separate-total pairing-rank sum is bounded. Condition N is a
necessary condition; except for `4+1`, the sufficiency of the N-passing
shapes is not decided, and it is not needed for the stated floor. Bands 49 and
above, changed readers, masked exactness and physical delivery are
unexamined. A finite enumeration is not a formal proof of the written
implications.
