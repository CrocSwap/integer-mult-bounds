# Addendum to #6833: why whole idles of rank 48 to 64 need no new compiler proof

**Verdict: no rank-dependent gap found.** The compiler (finite precompilation plus strictification) names no bound on
paid rank, and the package's own tail ratios already contain every rank-64 job. Rank enters exactly one
constant, `gamma`, with slack 0.0283 at rank 64; it would fail only near rank 79 (208 jobs). Two things are NOT
proved here: (a) the compiler text is a written argument conditional on the `compiler` assumption, as in every
predecessor; (b) the author did not read Sussman's Lean proof of Thm 1G, only its use in the two documents below.

Sources read: `research/bit-g20-nine-owned-relations/vendor/g20/inputs/FINITE-PRECOMPILATION.md`
(origin/main; it quotes Thm 1G of PR #4268, proof at `wht-power-saving-lean@563b4e6`) and
`research/higher-moment-strictification/README.md` section 2 (the paid-tail theorem). Check: `check_idle_rank.py`
(stdlib, exact enough Decimal at 60 digits; the package's interval engines remain the certificates).

## 1. What the compiler requires of a paid job

From FINITE-PRECOMPILATION section 1, the only hypotheses touching a paid job are:

1. Paid rounds are rank `r_j * c` jobs, in chronological order, acting on actual current owners (all-column native word).
2. Disjoint splitting: a rank `a+b` job is a rank `a` job then a rank `b` job on disjoint coordinates.
3. Whole-job adapters between units are priced. 4. Finite-program closure.

No hypothesis bounds `r_j`. The condition `r_max < k_min` is established by the strictification theorem
(README section 2): take the tensor power `v`, split every product paid rank `R > J = c^v` as `R = qJ + r`, complete every
target to `L = b^v`. Then `max paid <= J < L = min target` for ANY original paid ranks. Original ranks enter only through
`alpha = P_t/T_t`, `gamma = P_(t+u)/(c^u T_t)`, `delta = B b/(c^C T_t)`, `delta` has no paid input.
The split-charge inequality `qJ^t + r^t <= 2 R^(t+u) J^-u` needs only `t+u >= 1`, not any bound on `R`.

## 2. Lemma (whole idle)

**Lemma.** Let `I` be an `IDLE_ONE` at one time on one register of the word, with distinct stage set `W`, `|W| <= 18`. Suppose
(i) per port its `8|W|` positive axes are orthonormal and fresh (`physical.py`, checked for all 104 ports); (ii) the
operator is the product over `s` in `W` of the diagonal Gaussian `D_s` on stage `s`'s own 8-axis block, so it factors over any
partition of `W` (hypothesis 2, trivially, as the factors act on disjoint axes and commute); (iii) it commutes with each
site operator it passes (PROOF.md Lemma 3 hypotheses, checked at every `IDLE_ONE` by `independent/check_root.py`); (iv) both boundaries
are charged 1000 per two-axis exchange. Then `I` is a legal paid job of rank `8|W|` in the sense of section 1, and the
unit's `(T, P)` histograms with `I` counted at rank `8|W|` are the input of the unchanged compiler.

*Proof.* (i)-(ii): a rank-`8|W|` Gaussian on disjoint axes is one paid round in hypothesis 1 and splits per hypothesis 2. (iii) is the algebra
that makes the word's output the target `Q^-1 Prod D_s` times input (exact replay, 400 coefficients). Nothing else about
the job is used by section 1.

**Dependence of each constant on the rank** (`check_idle_rank.py`, histograms of RESULT.json):

| constant | uses rank? | at max rank 64 |
|---|---|---|
| raw crossing | via `P_t`, exponent `t<1` (concave: merging helps) | .00337180047549 |
| `alpha` | `P_t`, concave | `1 - 1.694e-10`, needs `< 1 - 1e-27` |
| `gamma` (u=1/7, c=11) | `P_(t+u)`, `t+u = 1.139 > 1` (CONVEX: merging hurts) | **.940443 < 31/32 = .96875** |
| `delta` | no (counts `B`, floor 12) | .878155 |
| `11^64 < 12^63`; `2(11^p)^64 <= (145^p)^63` | no: 64 here is the exponent `theta = 63/64`; 145 is the max TARGET | exact integers |
| compiler grid `(tested-claim)/7`, threshold `H` | no | unchanged |
| precision `2^(1e9 + R f)` | paid rank mass 166,812 (less than #6726's 178,044) | inside the 1e9 allowance; adapters 100.5M of 488.2M |
| rank-8|W| axes, exchanges | counted per exchange, no cap | 100,464 exchanges |

**Margin at rank 64 (the one sensitive constant).** `gamma` is increasing in idle rank. Replacing the 208 rank-64 idles
by rank `R` (all else fixed): R=40 .8982, 64 .9404, 72 .9551, first failure R about 79, R=144 1.095. So the claim
holds with a factor 1.25 in rank at the pinned `u=1/7`. `u` is a free parameter of the strictification theorem
(only `t+u >= 1`; the compiler grid does not depend on it): on a grid `u=0.24` gives `gamma = .92858`. Rank 64 is therefore not at a
cliff, and the 18-stage maximum (rank 144) is a genuine limit that this package does not use.

## 3. Precedent and what remains an assumption

- #6716 PROOF s2 and #6726 (rank 40) use the same job. The strictification README's own p7 inventory already
  carries paid ranks 16, 32, 48 (`P = {..., 48:448}`) in the same theorem.
- The only step beyond predecessors is the chain-merge across sites with different bases. That is not a compiler matter: it is Lemma 3 of
  PROOF.md plus the exact replay, and the compiler sees only the resulting physical job and the endpoint.
- Remaining conditional: the `compiler` assumption itself (finite precompilation is "a written argument, not a formal proof").
  This addendum shows #6833 uses it with no new rank-specific hypothesis. It does not discharge it.

## 4. Escape if a reviewer rejects rank 64 anyway

Cap idles at 56: kappa .0032987 (exact), below #6805 (.0033081). Cap 64 is required to lead.
