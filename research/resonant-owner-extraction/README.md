# A resonant original-owner partial target channel

Changing the second paid pencil from `P+2Q` to `P+Q` in the staggered
five-call preparation produces an exact **pure partial `Kx` channel**. Its
coefficient is nonzero at every positive even tensor width and zero at every
odd width. At width two its rank is exactly one out of 64 coordinates.
All independent original inputs, including the unused fresh-owner complement,
are retained. This is a constructive partial identity, not a complete `Kx,Ky`
unit, a restoration algorithm, a paid saving, or a multiplication theorem.

This changes the original-owner query excluded from the scope of
[PR #4751](https://github.com/CrocSwap/integer-mult-bounds/pull/4751).
That predecessor proves an obstruction with the original coefficient two,
even if the fresh-owner feed is changed arbitrarily. A resonant pencil alone
would not answer the continuation question: this package also supplies an
actual zero-`y` target identity and a nonvacuity proof for every even width.
The canonical claim is [Discussion #1166, comment 19131473](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19131473).

## Conventions and paid preparation

Base vectors are `e_j`, `j=j0+2j1+4j2`, with matrix words acting right to left.
Write `Xj,Zj` for the usual Pauli letters and

```
Cj = ((1+i) I + (1-i) Xj)/2
S e_j = i^(j0+j1+j2) e_j
U = CNOT(0 -> 2), V = SWAP(0,1), T = SWAP(0,2), V21 = SWAP(1,2)
P = S U S, Q = S V S, Q2 = S V21 S
W = Z0 Z2, N = Z1 V, L = N T, J = N C2, K = C0 C1 C2.
```

For **each actual base word** `g`, put `g_f=g tensor ... tensor g`, with
`f >= 1`. A sum `sum_g q_g g_f` keeps its rational coefficients fixed across
widths; it is not the tensor power of the width-one sum. The central word
`c=iI` is retained: `c_f=i^f I`, and `(-I)_f=(-1)^f I`.

Let `a=Y0 Z1`, `b=Y2`, with the Hermitian convention
`Pauli(x,z)=i^popcount(x&z) X^x Z^z`. Define the genuine free input projector

```
B_f = (I-a_f)(I-b_f)/4.
```

The two involutions commute, and `B_f` has rank `8^f/4` at every positive
width. Retain arbitrary original inputs `x,y` and their free copies. Execute

```
u = C0_f x
v = C0_f (P_f + Q_f) u
r = L_f^-1 J_f (W_f v + T_f B_f y)
t = C0_f (P_f + 2 Q_f) r
z = J_f (W_f t + Q2_f r + P_f v).
```

Every displayed line uses one paid `C` call. `J=N C2` applies one `C2`
call followed by the free monomial `N`; `L` is free. The changed second coefficient is one,
and the fourth coefficient remains two. This is the retained five-call
schedule of the predecessor, with that explicit change and the fresh feed.
The resonant pencil can be noninvertible. Its use here is a retained-register
linear calculation, with original `x` still present; no admission under an
invertible-pencil or full-rank prepared-unit contract is claimed.

The output projector is the following finite free-word expression, in the
written multiplication order:

```
D_f = (I+c_f^2)(I+c_f X0_f)(I+Z0_f)(I+Z1_f)(I+Z2_f)/32.
```

The factor `I+c_f^2` makes it zero at odd widths. At even widths, the other
four Pauli constraints commute and are independent; `D_f` is a projector of
rank `8^f/16`. The checker also verifies `D^2=D` coefficientwise in the actual
word algebra. In particular this definition never silently identifies `-I`
with `I`.

## A literal finite decoder

The following deterministic elimination recipe, together with the explicit
monomial records in `RESULT.json`, specifies the decoder without a search or
numerical nullspace. `RESULT.json` lists its coefficients **before** the common
left factor `D`, as permutations and fourth-root phases. A matrix record acts
by `e_j -> i^phase_i[j] e_permutation[j]`; rational coefficients are literal.
Thus it is also a direct instruction list for free copies and register sums.

Use formal rows with separate owners `x,y`. Let `H` be the group of
fourth-root monomial base matrices, and `p_h(w)` the coefficient of the
original `x` owner in the left coset `Hh`: a term `q g h x` contributes `q g`.
This notation is only used to derive the finite decoder; all its actual
monomials are independently certified to belong to the engine's free
alphabet below.

Set `A0=L^-1 J W`, `R4=C0 P C0`, `R7=C0 Q A0 C0 P C0`.
The resonant pivot `p_R7(z)=g1+g2` has the following monomials:

| | permutation on input columns 0,...,7 | phase exponents |
|---|---|---|
| g1 | 0 4 2 6 1 5 3 7 | 0 0 2 2 0 0 2 2 |
| g2 | 1 0 7 6 5 4 3 2 | 3 1 0 2 3 1 2 0 |

With `R=g1^-1 g2`, the checker establishes exact order four. Consequently

```
E = (I-R+R^2-R^3) g1^-1
E(g1+g2) = 0.
```

Start `e=E z`. For `(w,h)=(r,C2),(v,R4),(u,C0),(x,I)` in that order, the
pivot `p_h(w)` is a single nonzero term `q p`, with `p` free. Perform

```
e <- e - p_h(e) p^-1 w / q.
```

This gives fixed finite coefficients `d_w` such that `e=sum_w d_w w`.
The final output is

```
sum_w D_f (d_w)_f w = A_f K_f x,                 (1)
```

where `(d_w)_f` means the same wordwise evaluation, and `A` has 256 actual
free monomial terms. The coefficient of `y` is **exactly zero**. No term of
the `x` coefficient lies outside `HK`. All these statements are checked by
expanding the displayed preparation and decoder with exact Gaussian rational
base matrices, collecting equal actual words, and comparing coefficients.
The frozen receipt includes the target-coefficient SHA256, term counts and
its norm certificate; the verifier reconstructs all 256 terms.

Why this proves (1) for every width: evaluation `[g] -> g_f` is an algebra
homomorphism, since `(gh)_f=g_f h_f`. The checker obtains zero separately for
every actual word in the `y` residual, and obtains the target coefficient
wordwise. Applying any positive-width evaluation preserves this identity.
No converse, matrix-family independence assumption, or inference from width
one or two is needed for this positive result. In particular the distinct
central words `g,-g,ig,-ig` remain distinct throughout.

Every decoder, source-projector, output-projector and target-coefficient
monomial passes a stronger check than membership in `H`: its permutation is
`j -> Mj+s` with invertible binary `M`, and its phase has a mod-four Boolean
polynomial of degree at most two, whose quadratic coefficients are even.
These are actual free operations. Shifts and invertible XOR-linear address
maps supply the permutation; single-coordinate `S` gates supply the linear
phases. An even quadratic phase is generated by
`CZ_ij = S_i S_j S_(i xor j)^-1`, where a parity `S` is an address conjugate
of a coordinate `S`. Constant fourth-root phases and rational register sums
are also free. The receipt lists the affine columns and phase polynomial
for every emitted decoder term. This constructive claim does not rely on
allowing every fourth-root monomial for free.

## Exact nonzero characterization

Let `A=sum_g q_g [g]` be the target coefficient reconstructed above. Exact
Frobenius inner products give the all-width identity

```
||A_f||_HS^2 = sum_(g,h) q_g q_h (tr(g* h))^f
            = 8^f + (-8)^f - 20 (2^f + (-2)^f) + 32 (1 + (-1)^f).
```

Here `g*` is conjugate transpose; every `q_g` is real rational. The checker
collects **all 256² ordered pairs** (65,536), computes their exact base traces and
verifies that the only nonzero trace powers have precisely these six
coefficients. Zero trace bases contribute zero because `f` is positive.
This is a finite certificate of a formula for every width, not a fit to
small-width values.

For odd `f` the formula is zero, so `A_f=0`. For even `f`, it is
`2(8^f-20*2^f+32)`: at `f=2` it is 32; at every even `f>=4`, `4^f>20`
makes it strictly positive. Since `K_f` is unitary, `A_f K_f` has the same
rank and norm. Thus (1) is nonzero **exactly at positive even widths**.

Separate exact matrix controls give ranks zero at width one and one at
width two. At width two the free coefficient has entry `(18,0)=-2`, with
zero-based indices. The general even-width rank is not determined here.
In particular, nonzero is not a full-target claim.

## Information and cost ledger

| Item | Established here | Still owed for a complete construction |
|---|---|---|
| Paid preparation | Exactly five displayed `C` calls | Physical preparation and recursive supplier realization |
| Independent owners | Original `x,y` remain available | Full target `Kx` and `Ky` extraction |
| Fresh-owner feed | `B y`, rank `8^f/4` | Work on the unused source sector |
| Whole complement | `(I-B)y` retained; `By+(I-B)y=y` | Charged handling/return of this complement in a full protocol |
| Retained intermediates | `u,v,r,t,z` and free decoder copies may all remain | Space, routing, terminal frame and cleanup accounting |
| Output | Pure partial `A_f K_f x`, zero `y` contamination | Missing target coordinates; exact rank for general even width |
| Budget | No additional paid call for the finite free decoder in this model | A complete per-call profile and family expansion decision |

No dirty register is declared zero or discarded to establish (1). Keeping
`x,y` makes preservation of original information explicit; this does not
supply an in-place restoration schedule or price a physical encoding. No
recursive ceiling is evaluated because no complete supplier profile exists.
A later construction round must satisfy the family-level expansion gate.

## Reproduction and limits

```
python3 scripts/research_package.py --package research/resonant-owner-extraction
```

The registered Python 3.12, standard-library-only commands run exact checks
normally and under `-O`. The arithmetic input is authenticated before load.
Six controls reject omitting either projector, restoring the coefficient-two
pencil with this decoder, dropping the input complement, identifying the
central minus identity with identity, and extrapolating a width-one zero.
The committed receipt is compared structurally; a direct `--write` option is
only for explicitly regenerating it after a justified implementation change.

Local exact replay is not hosted CI or proof-kernel acceptance. No hook-rank
census, FFT replay, Lean, Docker, selected-frontier update, or full integer
multiplication theorem is claimed.

## Provenance and overlap

Canonical base is `624de9dc66858af0945e5f8a0942488d62280d43`, priority revision
7. `SOURCES.json` binds the task card, selected-record provenance, predecessor
proof and live arithmetic. The changed premise and stopped exploration are
recorded in `TASK.json`.

Credit Yiyang (@Lyy-iiis) for the phase-aligned two-image repair,
[PR #4710](https://github.com/CrocSwap/integer-mult-bounds/pull/4710), exact
head `b0d5192390af493d626054b060921895df3c94d2`, and the staggered continuation;
lee-phys for the original two-image prefix,
[PR #4688](https://github.com/CrocSwap/integer-mult-bounds/pull/4688), exact
head `264c4b3cb13c82d171de352ecf60486dfb8d2bd4`; and Jacob Sussman for the
small-unit model and free alphabet in
[PR #4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628), exact
head `ee4fd87f064017c23e5a86fc1dcfe0a5237caed3`. The fixed-original-owner
obstruction and retained arithmetic in
[PR #4751](https://github.com/CrocSwap/integer-mult-bounds/pull/4751), exact
head `2b7b84971377e389bb60bc99973e023084225dc9`, remain unchanged.
Prepared by JoyboyBrian with substantial OpenAI Codex assistance. Apache-2.0.

The initial fresh overlap checkpoint covered 299 open PRs, 3695 Discussion
records and 6319 local notes. Relevant predecessor heads were read live.
No matching resonant pure-target channel appeared; those checks are not a
novelty certificate. The predecessor's universal fresh-feed obstruction is
preserved because this construction changes its original-owner premise.

## Open next questions

1. Can a complete target and charged return use this channel? First write the
   independent-target/complement ledger and price every additional call.
   The remaining physical preparation, storage/routing, missing target,
   restoration and supplier obligations prevent any saving claim now.
2. What is `rank(A_f)` for general even `f`? Seek an analytic factorization of
   the frozen target coefficient. The exact nonzero norm alone cannot answer
   rank or the complete construction budget.
