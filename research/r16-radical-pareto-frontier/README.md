# Complete count-vector Pareto frontier for the R16 radical-triple fanout

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration; no new kappa.** The new
attainment is proved here for every commutative unital local ring and checked
literally in three finite rings. Completeness of the frontier also uses the written
lower-bound case analysis of lee-phys's
[PR6210](https://github.com/CrocSwap/integer-mult-bounds/pull/6210)
(`research/r16-radical-triple-fanout`), which is cited and not replayed. An
independent exhaustive search corroborates it for all words of at most nine gates
in R16.

## Result

Take PR6210's model unchanged: three arbitrary dirty rows, one preserved source
`p`, gates `P_r(beta)` (`A_r += beta p`) and `E_ab(alpha)` (`A_a += alpha A_b`)
with every nonzero coefficient, any finite word, every dirt column restored, and
final source column `lambda = (e, h, e+h+z)` over `R16 = F2[e,h,z]/(e,h,z)^2`.
Write a word's **count vector** as `(P_0,P_1,P_2; K_0,K_1,K_2)`: insertions per row
and incoming ADDs per row. The attainable count vectors have exactly **13
componentwise-minimal elements**:

| Family | Vectors | Number | Source |
|---|---|---:|---|
| `D` | `(1,1,1; 0,0,0)` | 1 | PR6210 |
| `T_i` | `P = 2 e_i`, `K = 2(1,1,1) - 2 e_i` | 3 | PR6210 |
| `R_ij;k` | `P = 2 e_i + e_j`, `K = 2 e_k` | 6 | PR6210 |
| `V_k` | `P = (1,1,1) - e_k`, `K = (2,2,2)` | **3** | **this package** |

PR6210's positive-price envelope exposes the first ten. It left open the branch
with one unit insertion in each of two rows, none in the third, and `K = (2,2,2)`,
because the average-cost inequality (its equation (2)) shows that branch is never
the unique cheapest. **That branch is attainable**: the explicit word below has
count vector `V_k`. So the componentwise frontier is strictly larger than the
price envelope, by exactly the three unexposed vectors `V_0, V_1, V_2`.

## The new word

Let `R` be any commutative unital local ring with maximal ideal `m`, let `i,j,k`
be the three rows, and let `lambda_i, lambda_j in m` and `lambda_k != 0`. Put
`beta = 1 + lambda_i` (a unit), `gamma = -lambda_k beta^-1` (nonzero) and
`a = lambda_j - 1` (a unit). In time order the word is

    E_ki(gamma), P_i(beta), E_ki(-gamma), E_ji(a), E_ij(1), P_j(1), E_ij(-1), E_ji(-a)

Contents of the changed row after each gate (`x` is the dirt, `p` the source):

| Gate | Row | Contents |
|---|---|---|
| `E_ki(gamma)` | k | `x_k + gamma x_i` |
| `P_i(beta)` | i | `x_i + beta p` |
| `E_ki(-gamma)` | k | `x_k - gamma beta p` |
| `E_ji(a)` | j | `x_j + a x_i + a beta p` |
| `E_ij(1)` | i | `(1+a) x_i + x_j + (1+a) beta p` |
| `P_j(1)` | j | `a x_i + x_j + (a beta + 1) p` |
| `E_ij(-1)` | i | `x_i + (beta - 1) p` |
| `E_ji(-a)` | j | `x_j + (1 + a) p` |

Since `beta - 1 = lambda_i`, `1 + a = lambda_j` and `-gamma beta = lambda_k`, the
word sends every row to `x_r + lambda_r p` and restores all dirt, for every width.
All eight coefficients are nonzero. Rows `i`, `j`, `k` each receive two ADDs and
rows `i`, `j` one insertion each, so the count vector is `V_k`. Independence of the
demand classes is not needed for this construction; it is needed only for the lower
bound. The first unit insertion is carried into row `j` by the two unit ADDs and the
second unit insertion cancels its residue modulo `m`; PR6210 shows that a two-insertion
word needs both coefficients to be units. The echo through row `k` delivers the third
class around the first insertion.

## Why the frontier is exactly these 13

PR6210's case analysis, cited, covers every finite word. By the rows receiving
insertions: all three rows gives a vector at least `D`; one row gives at least
`T_i`; two rows with two insertions in one of them gives at least `R_ij;k`; and
exactly one insertion in each of two rows `i,j` gives `K_i, K_j, K_k >= 2` (return
lemma), so at least `V_k`. These bounds are componentwise. The 13 vectors are
pairwise incomparable (checked in `verify.py`). With `V_k` attained, each is
attained, so the minimal attainable vectors are exactly the 13. The statement holds
for every commutative unital local ring and demand triple with independent classes
in `m/m^2`, using PR6210's general words and lower bound together with the words
above.

**Corollary for prices that may vanish.** Cost is monotone in counts, so the exact
optimum is the minimum over the 13 vectors for every price vector with `mu_i, c_i >= 0`.
Moreover `(T_i - V_k) + (T_j - V_k) = -2(c_i + c_j) <= 0`, so `V_k >= min(T_i, T_j)`.
The optimum is therefore still the minimum of PR6210's ten terms when prices are only
nonnegative. This follows from the cited lower bound and the frontier above.

## Evidence

[verify.py](verify.py) uses only the standard library and imports no predecessor code.

1. **Rings.** It builds `R16`, `F3[e,h,z]/(e,h,z)^2` and `Z/4[x,y]/(x,y)^2` (where
   `m^2 != 0`) from digit arithmetic and checks the ring axioms exhaustively.
2. **The word.** For every independent demand triple (168, 11,232 and 10,752 triples)
   and every ordered choice of rows `(i,j)`, the product of the eight gates equals the
   target matrix and has count vector `V_k`. It also checks the relaxed hypothesis
   (`lambda_i, lambda_j in m`, any nonzero `lambda_k`) in all three rings. Total:
   256,704 words.
3. **Literal inputs.** For the requested R16 demand, all six row orders are run on every
   scalar dirty and source input, forward and inverse: 6 x 65,536 = 393,216 cases.
4. **Controls.** Five mutated words (dropped gate, wrong echo coefficient, swapped
   moves, non-unit second insertion, dropped first echo gate) are rejected.
5. **Exhaustive search.** Over `R16 = F2 + m` with `m^2 = 0`, every coefficient is `a0 + x`
   with `a0 in F2` and `x in m = F2^3`. Residues evolve by row operations in `GL_3(F2)`;
   the `m`-parts evolve linearly and the three coordinates `e,h,z` are independent. A
   word type (ADD or insertion, residue 0 or 1, for each row pair) is solvable for an
   independent demand exactly when the span of its propagated first-order generators
   contains every pure-source vector. The search enumerates all 18 gate types for every
   word of at most nine gates, pruning only by the exact order-zero return distance, the
   pure-source dimension bound, and strict domination of a frontier vector. It visits
   20,362,086 nodes and finds **no solvable word type whose count vector lies outside the
   up-set of the 13**. It attains all 13, including the three `V_k` independently of the
   explicit word, and rebuilds each as a literal word with nonzero coefficients that
   matches the target matrix.
6. **Sensitivity.** Relaxing the target to any two-dimensional pure-source subspace
   (words of at most six gates) yields 7,842 solvable word types whose count vectors lie
   outside the up-set, and deleting `T_0` from the frontier list makes the search flag
   the vector of `T_0`.
7. **Cited premise.** The pinned bytes of PR6210's README and the five sentences of its
   case analysis used above are checked.

Reproduce from the repository root (about 47 s and 520 MB locally):

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/r16-radical-pareto-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/r16-radical-pareto-frontier/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/r16-radical-pareto-frontier
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/r16-radical-pareto-frontier --check-source-history
```

Expected marker: `PASS_R16_RADICAL_PARETO_FRONTIER frontier=13 search_gates=9`.
Each run also prints a generated receipt bound to the hashes of `verify.py` and
`VERIFY.json`.

## Limitations

- Completeness for words longer than nine gates, and for rings other than R16, rests on
  PR6210's written case analysis. It is cited, not replayed or machine checked here. The
  search is independent finite corroboration up to nine gates in R16.
- The first-order criterion is exact only when `m^2 = 0`. For `Z/4[x,y]/(x,y)^2` only the
  word identity is checked.
- Counts are aggregated by receiving row, as in PR6210. This is not a per-edge frontier,
  not a dependent-class frontier, and the model has no auxiliary rows.
- No physical supplier, kappa change, proof-kernel verification or independent human
  review is claimed.

## Open next questions

Also recorded in [TASK.json](TASK.json).

1. **Dependent demands.** What is the frontier for a rank-two demand such as `(e,h,e+h)`
   over R16? PR6210 records a cheaper word there (14 against 15 at prices
   `(3,5,10;1,3,2)`). First step: run the first-order search with the two specific
   pure-source targets of that demand; the registered control relaxes only to any
   two-dimensional subspace. Blocker: no written lower bound exists for dependent
   classes.
2. **Directed edges.** What are the minimal per-edge ADD count vectors, and the exact
   tariff with independently priced directed edges (PR6210's question 2)? First step:
   label each ADD by its directed edge in the search. Blocker: the return lemma does not
   strengthen per edge, and the number of minimal vectors may be large.
3. **Rings with `m^2 != 0`.** Does a second-order search corroborate the cited lower
   bound for `Z/4[x,y]/(x,y)^2`? First step: add quadratic terms to the propagated state
   for words of at most seven gates. Blocker: the conditions become nonlinear.

## Credit

Model, lower bound and the ten price-envelope words: lee-phys, PR6210. Retained
lineage: PR5259, PR5514, Ali Romman PR5310, Krzysztof Wojt PR5045, Ross Richardson
PR3063 and PR3121, and Nick Petalas PR4916, PR5208 and PR5948 (the Boolean demand
`(1,2,4)` frontier, a different ring and demand). The word `V_k`, the corollary and the
exhaustive first-order search are new here.
