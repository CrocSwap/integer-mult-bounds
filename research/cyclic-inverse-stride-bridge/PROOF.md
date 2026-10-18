# Linear-traffic rounded inversion for every cyclic stride

## Result and scope

PR628 inverts PR621's kernel `P(tau Z_L^w)` for neighbouring strides with
precision `p+O(r^4)` that does not depend on `L`. For other strides it routes
the cycles into contiguous order with two merge sorts, at a cost of
`O(L(B+log L)log L)`. That sort cost brings back a `log L` traffic factor.
This note removes the sort. The solver below handles every stride `w` with
`O(L)` sequential record moves and `O(L)` rounded operations per factor. Its
error bound does not depend on `L`.

**Theorem 1 (one stable factor, any stride).** Let `L>=1`, let `w` be any
integer, and let `0<beta<=1/2`. Assume `|b_i|<=1-beta` and `|x_i|<=B`. The
algorithm `solve` of `stride.py` returns `yhat`. Here `y` is the unique
solution of `y_i = x_i + b_i y_((i-w) mod L)`. Let `K` be the number of
non-base recursion levels, so `K <= floor(log2 L)+1`. Every complex
operation is rounded once to a grid of spacing `u`. Assume the admission
conditions `u<=beta/3` and `4(K+1)u<=beta`. Then

    max_i |yhat_i - y_i| <= kappa (u/beta)(5 + 4B/beta) + u,
    kappa = min(max(K,1), 1/beta).

Traffic is at most `40L` record moves: a level of length `L_k`, with
stride `w_k <= L_k/2`, costs at most `13L_k+5w_k` plus `4L_k` for an
optional reversal, and `sum_k L_k <= 2L`. The solver performs `O(L)`
rounded multiply-adds. All of this runs on a fixed number of sequential
tapes.

The bound stays finite as `L` grows because `kappa <= 1/beta`. The only
dependence on `L` is in the admission condition `4(K+1)u<=beta`. That
condition is `w_bits >= g+2+log2(K+1)`, where `beta=2^-g`. Any execution
budget for target precision `p >= log2(log2 L + 2)` already meets it.

## Algorithm

Normalize `w` modulo `L`. If `2w>L`, reverse the arrays. Reversal turns the
stride into `L-w`, which is at most `L/2`. A tape reads one array backwards
while it writes another forwards, which costs `2L` record moves each way.
If `w=0`, return `x_i/(1-b_i)` rounded.

Otherwise the residue classes modulo `w` form chains. Chain `c` contains
`c, c+w, c+2w, ...`. Each chain has at least two members because `w<=L/2`.

1. **Pass A.** Scan `i=0..L-1`. Read the lag-`w` predecessor from a FIFO
   that starts with `w` start markers. Compute the zero-seed value
   `zhat_i = rnd(x_i + b_i zhat_(i-w))` and the chain product
   `pihat_i = rnd(b_i pihat_(i-w))`. At a chain start, `zhat=x` and
   `pihat=b` exactly.
2. **Closure.** The last `w` positions `e=L-w+k` are the chain ends. The
   start of chain `c` has predecessor `c-w+L`, which is end `k=c`. Hence the
   end values satisfy

       Y_k = zhat_(L-w+k) + pihat_(L-w+k) Y_((k+L) mod w).

   This is the same problem on `w` entries with stride `(-L) mod w`.
   Solve it recursively.
3. **Pass C.** Scan `i=0..L-1` again. This time the FIFO starts with
   `Y_0..Y_(w-1)`. Compute `yhat_i = rnd(x_i + b_i * pop())` and push it.

Each level at least halves the length, so `sum_k L_k <= 2L` and
`K <= floor(log2 L)+1`. A FIFO built from two stacks moves each record at
most four times: a push, a transfer pop, a transfer push and a pop. A stack
on a tape keeps its head at the top. Pass A, the closure handoff, pass C and
the two reversals therefore cost at most a fixed multiple of `L_k` record
moves at level `k`. In the finite replay through `L=131072` the maximum is
29.68 per entry. For comparison, PR628's two sorts make
`4L ceil(log2 L)` record moves. A record holds the `O(B)` bits of one or
two numbers. Moving it costs `O(B)` tape cells. Loop counters need only
amortized `O(1)` bit changes per step, plus `O(log L)` per level for the
values `L_k` and `w_k`. Stride arithmetic over all levels costs
`O(log^2 L)` bit operations.

## Proof of Theorem 1

**Notation.** `Shat_k` is the computed system at level `k`, with data
`xhat^k` and coefficients `bhat^k`. `Ytilde^k` is its exact solution, and
`m_k = min_i (1-|bhat^k_i|)` is its margin. `S*` is the exact Schur
complement of `Shat_k` on the chain ends. The solution of `S*` is the
restriction of `Ytilde^k` to those ends.

**Lemma 1 (PR764's shared-suffix identity).** Let `q_1..q_l` lie in
`[0,1-m]`. Put `P_j = q_(j+1)...q_l` and `G = sum_j P_j`. Then

    sum_j (1-q_j) P_j = 1 - q_1...q_l,   hence   G <= (1-|pi|)/m.

The quantity `pi` is the chain product. A rounded recursion multiplies its
previous error by `b` and adds at most `u`, so after a chain its error is at
most `uG`. Therefore

    |zhat_e - z_e| <= u(1-|pi_e|)/m_k,   |pihat_e - pi_e| <= u(1-|pi_e|)/m_k.

**Lemma 2 (margins never shrink below beta).** From Lemma 1,
`1-|pihat| >= (1-|pi|)(1-u/m_k)`. A chain has at least two members, so
`1-|pi| >= 1-(1-m_k)^2 = m_k(2-m_k)`. Hence `m_(k+1) >= f(m_k)` with
`f(m)=(2-m)(m-u)`. The function `f` is concave on `[beta,1]`. At the
endpoints,

    f(beta) = (2-beta)(beta-u) >= (3/2)(2beta/3) = beta   when beta<=1/2 and u<=beta/3,
    f(1) = 1-u >= beta.

Therefore `m_k >= beta` at every level. The bound does not depend on depth.
The replay checks `|bhat|<=1-beta` exactly at every level of all 2052
generic cases.

**Lemma 3 (weighted data).** Suppose `|xhat^k_i| <= A_k(1-|bhat^k_i|)`.
Then the telescoping identity gives `|z_e| <= A_k(1-|pi_e|)`. Lemma 1 adds
at most `u(1-|pi_e|)/m_k`, and Lemma 2 compares `1-|pi|` with `1-|pihat|`.
Together they give the same invariant at level `k+1` with

    A_(k+1) = (A_k + u/beta)/(1-u/beta),   A_0 = B/beta.

The admission condition `4(K+1)u <= beta` gives `A_k <= 2A_0+1` at every
level.

**Lemma 4 (weighted inverse).** Suppose `|v_i| <= C(1-|b_i|)`. Then the
solution of `Y = v + b W Y` satisfies `|Y_i| <= C`. The Neumann series has
weights `P_j(1-q_j)`, and these telescope to at most one. In particular,
`|Ytilde^k| <= A_k`.

**Error recursion.** `Shat_(k+1)` differs from `S*` only by the pass-A
rounding. The two solutions satisfy

    (I - Bhat W)(Ytilde^(k+1) - Y*) = Delta x + Delta B * W Y*.

By Lemma 1, each entry of the right side is at most
`(u/beta)(1+A_k)(1-|pi_e|)`, and `1-|pi_e| <= (1-|pihat_e|)/(1-u/beta)`.
Lemma 4 then bounds the solution difference by
`(u/beta)(1+A_k)/(1-u/beta) <= 2(u/beta)(1+A_k)`. Pass C seeds every chain
with the closure value. The seed error is multiplied by the chain prefix
product. That product contains at least one coefficient, so its modulus is
at most `1-beta`. Pass C's own rounding adds at most `u/beta`. Let
`e_k = |Yhat^k - Ytilde^k|`. Then

    e_k <= (1-beta)(e_(k+1) + 2(u/beta)(1+A_k)) + u/beta,
    e_K <= u   (base case: one exactly rounded division, |1-b|>=beta).

Sum this recursion. At level 0 the data are exact, so `Ytilde^0 = y`. With
`A_k <= 2B/beta+1` and `sum_(k<K)(1-beta)^k <= min(K,1/beta)`, the theorem
follows.

## Theorem 2: the full kernel at any stride

This theorem keeps PR628's certified factorization `Q`, its bound
`||P(U)^-1-Q(U)^-1|| <= 2^(-p-1)`, its preparation charges and its phase
charges. Every factor of `Q(U)^-1` with `U = tau Z_L^w` uses one call to
Theorem 1:

* **Outer root.** `(U-rho)^-1 = -rho^-1 (I - (tau/rho) Z^w)^-1`. Apply one
  stride-`w` solve, then one rounded multiplication by `-1/rho`.
* **Inner root.** `(U-rho)^-1 = conj(tau)(I - rho conj(tau) Z^-w)^-1 Z^-w`.
  Apply an exact rotation by `w`, one stride-`(-w)` solve and one rounded
  multiplication by `conj(tau)`.

A tape performs the rotation by copying the tail and then the head, which
costs `O(L)` record moves. Let `E_j` be the execution error after `j`
factors, and let `N_j = r beta^-j` bound the exact prefix norm. Then

    E_j <= E_(j-1)/beta + bound_1(N_(j-1)+E_(j-1)) + u,

where `bound_1` is the bound of Theorem 1. The replay evaluates this
recurrence exactly for each certified kernel. It requires
`E_n + perturbation <= 2^-target`. In closed form, `kappa <= 1/beta` turns
the per-factor constant into at most `C=(5+4B)/beta^3+2u`. PR628's `T_j`
argument then gives

    w_bits = p + (n+2) g + O(log r),   g = log2(1/beta) = O(r^3).

This has the same order as PR628's neighbouring budget and contains no `L`
term. For strides with small `K`, `kappa=K` applies instead, and the budget
improves to `p+(n+1)g+O(log(rK))`. That form follows PR764's `beta^-2`
shape. The replay uses the exact `min`.

## What is paid, and the verdict on PR621's gain

PR621's gain is an inverse whose cost per entry is independent of the
cyclic length: `L`-uniform precision and work linear in `L`. The table
charges each cost that the K492 review lists. All four apply to one kernel
inverse at an arbitrary stride on fixed sequential tapes.

| Cost | Charge | Source |
|---|---|---|
| Preparation | `soft-O(r^3(p+r^4))` bit operations, independent of `L`, with Pan's factorization and fast elementary functions; phases are paid per oracle call | PR628 (cited theorems, not implemented) |
| Rounded execution | precision `p+O(r^4)`, uniform in `L`; per factor `O(L)` rounded operations | Theorems 1–2 here; PR764's identity |
| Restoration | the input tape is never written; all scratch tapes are erased at `O(LB)` | this note, sequential-tape model |
| Tape | at most `40L` record moves per factor at any stride, versus PR628's `O(L(B+log L)log L)` sorts | Theorem 1 here |

The total for one kernel inverse is

    soft-O(r^3(p+r^4)) + O(r L) M(p+r^4) + O(r L (p+r^4)),

where `M` is the cost of integer multiplication. The per-entry cost does not
depend on `L`, so **the gain survives payment at the level of one kernel
inverse.** The only `L`-dependent term is the admission requirement
`p >= log2(log2 L+2)`.

## Not closed here

* PR628's dirty-array contract allows `ceil(log2(r-1))` borrowed arrays and
  only `O(1)` clean scalars. That contract arises in the exact-width word
  model. The stride solver here uses blank scratch tape, which is free in
  the sequential-tape model and is erased at linear cost. It has not been
  recast for borrowed arrays. That case still uses PR628's
  `O(p+log(D+1)+r^5)` precision and neighbouring-stride leaves.
* The guard `O(r^4)` is a proof bound. Numerical probes for `r<=32` put
  `min_|z|=1 |P(z)|` near `2^-10`, while PR621's bound gives up to
  `2^-27880`. A sharper lower bound would shrink every budget above.
  This package does not certify those probe values.
* Composition across the complete transform, the transform's phase
  collection, normalization and the integer-multiplication reduction remain
  open. No integer kappa, complex b, or BIT c changes.
