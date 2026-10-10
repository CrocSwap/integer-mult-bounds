# Deferred bit word under one-child accounting: finite certificate and scope

## 1. Claim

Under the analytic and fixed-tape interfaces retained by PR #104,

$$
\kappa=\frac{1044939}{10^{10}}=1.044939\times10^{-4}.
$$

The witness has three parts.

- **Bit side.** Swapnil Jain's round-seven deferred word at h = 23 (PR #97 import,
  `research/deferred-signed/`), charged by PR #104's one-child rule.
- **Complex side.** A new h = 24 producer with all 24 centers disjoint (decoder Σ A_i / 21),
  in PR #104's complex framework.
- **Assembly.** PR #104's stopped-product assembly at its own PHASE_STOP = 10^-6.

`scripts/deferred_product_network.py` checks the claim:

- coarse bit saving 620523/(5·10^9), via PR #104's coarse enclosure;
- ordinary saving 0.999·coarse + 0.001·OLD;
- complex saving 26129/(2.5·10^8), via PR #104's sharp moment;
- 47 strict constraints and 7 margins;
- the next κ grid point is rejected.

The complex side binds.

## 2. Every bit residual is a projector residual

PR #104's rule (`notes/stopped-product-factorization.tex`) makes every proper rank-r projector
residual ONE child of width r. It needs one common generic rational basis for the finite list
of residuals, together with the opposite-bank convention diag(I, C_n).

The round-seven word charges only the following, per stage and invocation. Each is the
difference of nested G-orthogonal projectors (G = I − J/9), or a commuting-idempotent endpoint
in the partial-swap form D_A.

- Slot chains: start frames, lifted node frames U_n, late-copy intersections, root frames, F.
  All are nested and G-nondegenerate (`check_lifted.py`, `check_frames.py` part X).
- Slot exteriors:
  - stage one: E_1 = I − (I − σ_u)⊗Q, from D_(I−A) D_T = D_(E_1) with A = σ_u⊗Q ≤ T = I⊗Q;
  - stage two: E_2 = (I − P)⊗I + P⊗σ_u.
  Plain slots have σ_u = 0. The rank is m − r_u with r_u = h − dim σ_u (#97 PROOF.md).
- Centre copies U_c → 0, of rank h − 1.
- y_T chains 0 → σ levels → t_T^⊥ and X_S chains ⟨t_S⟩ → s_i → F. These are nested in time
  order and nondegenerate (`check_frames.py` part Q).
- Data connectors (I − P)⊗(I − Q), of rank (h−1)², and one rank-one copy correction per pair.

Garbage readouts y_T −= C_{T,u} z_u are scalar gates at common frames and carry no residual.
Nothing else is charged.

For each projector the leading principal minors of sizes 1, …, r are nonzero for a generic
basis; similarity to diag(I_r, 0) gives a witness. The list is finite, so PR #104's argument
gives one common rational basis. Stage two is the complement time-reversal, with the same
residual multiset; #97's `round7_literal_frame_ledger.py` checks reflected continuity and the
event histogram.

## 3. Child list and moment

Each stage and invocation contributes:

- a child [m − r_u] for every slot;
- a child [r] for every slot chain step and every y_T and X_S chain step;
- h children [h − 1] for the centre copies.

Globally there are 2N connectors [(h−1)²] and N corrections [1]. With
m = 529, v = 1771, R = 28866, N = v², W = 2N + 2vR = 108516254 and L = 2vh(h−1), the rank sum is

    s = Wm − N + L = 57403754177,

as in #97. The largest child is 528, a gauged exterior with r_u = 1. The coarse saving is the
largest 10^-10 grid point accepted by PR #104's `coarse_moment` enclosure; the next point fails.
PR #104's stopped-adapter conversion then gives the ordinary saving AB.

## 4. Complex producer

`certificates/deferred-product-complex-dag.json.gz` lists the operand pairs and roots of an
h = 24 paired-triple / pair-star / centre-disjoint producer with 91,770 additions.
`scripts/deferred_product/replayed.py` recomputes every support, label and rank and runs PR #104's
complex checks (root supports, the ÷21 decoder and scatter identity, nesting, nondegeneracy).

PR #104's unchanged matcher then gives:

- R = 28,705 roles (PR #104's producer: 44,918);
- the histogram in `certificates/deferred-product-complex-input.json`;
- a_c = 26129/(2.5·10^8) under PR #104's profile and sharp moment.

The 3,308 alternating rank-2 residuals use the one-child Gauss normal form that PR #104
already states for all binary residuals. An independent gate-frame replay of the full signed
two-stage word gave:

- 0 violations once alternating residuals are allowed;
- reflected continuity;
- a histogram equal to the row.

## 5. Bridge, assembly and scope

PR #104's bridge is reused with one change. The maximum bit child is 528, so the coarse halving
degree is 367, and the product row stock is the smallest multiple of 1000 above (51/25) times
the coefficient (p^22000), by `copied_centers_network.py`'s rule. The stock enters only the
row-product slack and eventual cutoffs.

The assembly bit is min(AB, (1 − PHASE_STOP)·a_c − 10^-10), which is complex-bound here.

PR #104's written interfaces remain assumptions:

- opposite-bank factorization and atom streaming;
- ordinary conversion;
- the common odd-denominator grid;
- the retained analytic and tape transfer.

This is a finite conditional certificate. It makes no claim of global optimality, practical
speedup, or a formalized theorem.
