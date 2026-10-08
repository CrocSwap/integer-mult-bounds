# Contiguous-pair coordinate pricing, two-round carry exchange, and min-cost circuit reclamation

## 1. Structural defect in prior coordinate permutations (Stage A)

The aligned-composition compiler (`scripts/experiments/aligned_composition_engine.py`, PR #91) builds frame regions anchored on consecutive coordinate pairs $(0,1), (2,3), \dots, (2\lfloor h/2\rfloor-2, 2\lfloor h/2\rfloor-1)$ plus one odd singleton coordinate $h-1$ (`22` at $h=23$, `24` at $h=25$).

In PR #91 (and inherited through PRs #93, #94, #95, and #98), the coordinate permutations had two structural discontinuities that broke contiguous diagonal pivot runs in the fixed-basis profile matrices:

1. **At $h=23$**: the singleton coordinate `22` was mapped to index `4`, splitting the chain of 11 pairs between indices `0..3` (pairs `(18,19), (20,21)`) and indices `5..22` (pairs `(0,1)..(16,17)`). Moving the singleton to index `0` and shifting the first two pairs to `1..4` via
   $$P_{23} = [6, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 17, 19, 20, 21, 22, 1, 2, 4, 3, 0]$$
   makes all 11 pairs contiguous across indices `1..22`.
2. **At $h=25$**: coordinates `17` and `18` were swapped to `(23, 22)`, splitting both pair `(16,17)` and pair `(18,19)`, while singleton `24` was mapped to index `4`. Reuniting `(16,17)` and `(18,19)` and moving singleton `24` to index `23` via
   $$P_{25}^{\text{oracle}} = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 1, 0, 2, 3, 23],$$
   $$P_{25} = [5, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 24, 1, 0, 2, 3, 23]$$
   makes all 12 pairs contiguous.

When $P_{25}^{\text{oracle}}$ is passed to the **unchanged PR #91 engine** (`ORACLE_COORDINATES`), the unaltered compiler reclaims an extra auxiliary role at $h=25$ (**$R_{25} = 34,771$**, down from $34,772$, reducing physical width from $W = 130,417,912$ to $W = 130,416,141$) and certifies the Stage A intermediate bound

$$\kappa_{\text{Stage A}} = \frac{26400279929441}{500000000000000000} = 5.2800559858882 \times 10^{-5}$$

($+9,098,235,180$ grid steps over PR #98 and $+10,942,923,661$ over PR #91, with zero engine modifications).

## 2. Two-round carry exchange and min-cost circuit reclamation (Stage B)

Stage B (`engine.py`) refines the legal carrier and reclamation choices while keeping every admissibility guard, frame inclusion check, $\mathbb{F}_2$ independence check, literal XOR realization, and arbitrary-dirty restoration invariant unchanged:

1. **Two outer rounds of carry exchange**: runs two outer rounds (`outer_exchange_rounds = 2`) of the existing 1-for-1, 2-for-2, and 3-for-3 carry exchange passes, allowing 3-cycle updates in round 1 to unlock further 1-for-1 and 2-for-2 improvements in round 2.
2. **Minimum-cost pending order and retired-circuit toggling**: during `acquire(g, anchors)`, orders eligible pending live slots by `(profile_cost(s, g), order[s])` and includes all zero-sum $\mathbb{F}_2$ circuits formed by anchor, eligible pending, and eligible retired slots when toggling the clearing support `aa = bits(e ^ (1 << s))` of a reclaimed retired slot $s$. Every toggled support still satisfies $\bigoplus_{a \in \{s\} \cup aa} \text{slots}[a] = 0$ and `contains(frame[a], frame[g])`, verified immediately by `raise_(a, g)` and `assert not slots[s]`.

Together with contiguous-pair coordinate pricing, Stage B produces:
- At $h=23$: $R_{23} = 26,399$, reducing the internal profile cost from `182.015366` to `181.896779` (`-1,074` singleton blocks).
- At $h=25$: **$R_{25} = 34,768$** (reclaiming **4 fewer roles** than PRs #91–#98), reducing the internal profile cost to `256.083020`.

## 3. Paid recursive profile and exact arithmetic

Set $m = 575$, $N = \binom{23}{3}\binom{25}{3} = 4,073,300$, and $q_h = N / \binom{h}{3}$ ($q_{23} = 2,300, q_{25} = 1,771$). For Stage B ($R_{23} = 26,399, R_{25} = 34,768$):

- Physical width: $W = 2N + q_{23} R_{23} + q_{25} R_{25} = 130,438,428$.
- Decreasing-rank loss: $L = \sum_{h \in \{23,25\}} q_h h(h-1) = 2,226,400$.
- Internal rank sums: $\sum_t t H_{23}(t) = 23 R_{23} + 506 = 607,683$ and $\sum_t t H_{25}(t) = 25 R_{25} + 600 = 869,800$, both verified across all three CRT primes ($2^{61}-1, 2^{31}-1, 2^{19}-1$) with zero disagreements.
- Complete paid child histogram:
  $$C(t) = 19N[t=1] + 2N([t=21]+[t=17]+[t=481]) + \sum_{h \in \{23,25\}} \bigl(q_h H_h(t) + q_h R_h([t=h]+[t=m-2h]) + 2N([t=1]+[t=h-2])\bigr),$$
  satisfying $\sum_{t=1}^{529} t C(t) = mW - N + L = 75,000,249,200$.

Every auxiliary exterior, copied-center charge, side-growth contribution, and early/late restoration gate remains paid in full. At bit saving

$$a = \frac{52808007812753}{1000000000000000000},$$

the rational upper moment enclosure is strictly below $1$, the next $10^{-18}$ grid point has a lower enclosure strictly above $1$, and the independent moment audit confirms both inequalities. Both PR #98's complete profile and Stage A's complete profile have lower moment enclosures strictly above $1$ at $a$. The regenerated finite bridge (`maxchild = 529`, `halving_degree = 9`, `row_degree = 2000`) satisfies all 47 strict constraints and 7 margins at

$$\kappa = \frac{26402609637081}{500000000000000000} = 5.2805219274162 \times 10^{-5},$$

and rejects the next $10^{-18}$ grid point. This is a conditional finite witness under the inherited analytic, routing, recovery, and fixed finite-alphabet multitape hypotheses; no unconditional theorem, global optimality, or practical runtime speedup is claimed.

 Attribution follows `README.md` and `NOTICE`. Prepared by Thomas Marchand with Google Antigravity assistance.
