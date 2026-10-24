# Boolean integrality lowers the three-cycle cut ceiling to 17/3

This is a **scoped proof conditional on a cited spectral theorem**, with an
exact finite certificate for the new arithmetic step. Every nonnegative
combination of register-independent permutation cuts has normalized value at
most `17t/3` for `t` coordinate-three-cycle target registers. Therefore final
rounding certifies at most 17 calls for three targets. It cannot certify the
direct `6t` tariff for any `t >= 3`.

Krzysztof Wojt's [PR #5063](https://github.com/CrocSwap/integer-mult-bounds/pull/5063),
head `9ad4c47068f900fa1619191292539adcced0d638`, proves the preceding ceiling
`beta*t`, where `beta = (27 + 9*sqrt(2))/7`. Its obstruction to proving `6t`
starts at `t = 4`. This package adds Boolean integrality and moves that threshold
to three. It takes that spectral inequality as a mathematical premise; it does
not replay or independently validate the predecessor's certificate.

The exact Boolean-cut optimum and actual multi-target word minimum remain
open. No shorter word, complete supplier, new kappa or selected-frontier change
is claimed.

## Model and cited premise

Use the formal coordinate-CNOT model of James Reed's
[#4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968) and its
credited predecessors. Work in `M_R(F2[GL_n(F2)])`, with `n >= 3` and `R >= t`.
A paid factor is `I + ([s]+[e]) N`, where `s = I+E_ij`, `i != j`, and `N`
is a rank-one idempotent. Scalar register mixing is free. Target roles carry
coordinate three-cycles, on possibly different triples and in either
orientation. Every other dirty register and address coordinate is restored.

For a finite permutation action and a subset `A`, let
`out_A(g) = |{x in A : gx not in A}|`. Each cut uses the same `A` in every
register. The credited crossing-rank formulas give paid cost `out_A(s)` and
target value equal to the sum of its role crossing counts.

The external spectral premise for the new rounding step is PR5063 equation (2).
For the six coordinate CNOTs `S` of any embedded `H = GL3(F2)` and either coordinate
three-cycle `c`, every finite permutation action satisfies

    6 out_A(c) <= beta sum_{s in S} out_A(s).

See its [pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/9ad4c47068f900fa1619191292539adcced0d638/research/three-cycle-cut-ceiling/README.md).
That pending theorem is cited, not copied or checked here. The new verifier
has no runtime dependency on the pending branch. Its local PASS establishes
the new rounding and lifting facts, not the truth of that external premise.

## 1. The regular-action integer constraints

The group `H` has `7*6*4 = 168` elements. For any subset `B` in its regular
left action put

    k = out_B(c),    d = sum_{s in S} out_B(s).

The order-three permutation `c` has 56 disjoint three-cycles. Each cycle
contributes at most one exit, so `0 <= k <= 56`.

Each CNOT is a fixed-point-free involution. Its regular-action edges form a
perfect matching. The six matchings form a loop-free 6-regular multigraph
with 504 edges. Counting degrees inside `B` gives

    d = 6 |B| - 2 e(B).

Thus `d` is even and `0 <= d <= 504`. Multiplicities cause no problem for
this degree identity. When `d = 0`, the cited inequality implies `k = 0`.
For `d > 0`, the cited inequality gives `6k/d <= beta`.

## 2. The new rational-gap lemma

Suppose `k,d` satisfy those constraints and `6k/d > 17/3`. Write `d = 2m`.
Then `9k > 17m`. Since `k <= 56`, we have `17m < 504`, hence `m <= 29`.
Integrality now gives `9k >= 17m+1`, and therefore

    6k/d = 3k/m >= 17/3 + 1/(3m) >= 17/3 + 1/87 = 494/87.

But `beta < 494/87`. After moving the rational part and squaring positive
quantities, this is exactly

    1109^2 - 162*87^2 = 3703 > 0.

This contradicts the cited spectral inequality. Consequently

    6k <= (17/3)d.

The bounded verifier independently enumerates all 57 choices of `k` and all
252 positive even choices of `d`. It compares the spectral inequality by
integer squares, with no floating arithmetic. The maximum admissible ratio
is `17/3`, achieved among these scalar pairs exactly at `(17,18)`, `(34,36)`
and `(51,54)`. These are arithmetic witnesses, **not asserted realizable cuts**.
Thus `17/3` is sharp for these scalar constraints only.

The hypotheses matter. Allowing odd `d` admits the scalar pair `(52,55)`;
allowing `k` up to 87 admits `(87,92)`. Both obey the spectral inequality but
exceed `17/3`. They are counterexamples to the weakened arithmetic statements,
not group-action constructions.

## 3. Every finite action, dimension and dirty-register count

Consider one `H`-orbit `O` of an arbitrary finite permutation action. Choose
`omega in O` and lift `A intersect O` to

    B = {g in H : g omega in A}.

The map `g -> g omega` intertwines left multiplication with the given action,
and each fiber has the same size `h = |Stab_H(omega)|`. For every label `u`,

    out_B(u) = h out_{A intersect O}(u).

Apply the new regular-action inequality, divide by the positive integer `h`,
and sum over the finitely many orbits. This proves

    6 out_A(c) <= (17/3) sum_{s in S} out_A(s)

for every finite `H` action. In `GL_n(F2)`, restrict to the subgroup on a
target's three coordinates. This restriction remains a finite permutation
action regardless of address spectators. Coordinate relabelling and inverse
cycles cover every target triple and orientation.

Now take arbitrary nonnegative cut weights, including mixtures of finite
actions. Let `C_s` be the aggregate crossing cost of paid label `s`, and let
`M = max_s C_s`, over all paid coordinate-CNOT labels. For each target role
`r`, its aggregate value `D_r` satisfies

    D_r <= (17/18) sum_{s in S_r} C_s <= (17/3) M.

If `M = 0`, all target values vanish. Otherwise summing over targets and
dividing by `M` bounds the normalized cut value by `17t/3`. Free scalar
register mixing and arbitrary restored dirty registers do not change these
credited cut formulas. Since `17t/3 <= 6t-1` for `t >= 3`, rounding the final
relaxation value up cannot prove `6t` for those target counts.

## Evidence and reproduction

From the repository root, use CPython 3.12 with no third-party dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/three-cycle-boolean-rounding
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/three-cycle-boolean-rounding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/three-cycle-boolean-rounding --check-source-history
```

The registered replay also runs the verifier with `-O`. The arithmetic check
covers all 14,364 bounded scalar pairs. The lifting calibration enumerates all
128 subsets of the seven-point natural action and their regular lifts. It
checks equal-size fibers, every six-label crossing count, boundary parity and
the crossing cap. It does not recompute the predecessor's spectral identity
or any word minimum. Three controls reject a smaller asserted ceiling, an
omitted parity hypothesis and an omitted crossing cap. A generated stdout
report binds the checked package files with SHA-256 hashes.

The mathematical result remains dependent on PR5063. No independent human
review, formal proof-kernel review, exact cut optimization, three-target word
search, native conversion, compiler/precision/storage admission, or selected
construction cold replay is supplied. There is no physical consumer or saving
claim requiring an expansion of this formal-model investigation.

## Verifier resource bounds

Power of Ten rule 3 has a managed-runtime deviation in `verify.py`: Python
allocates integers, fractions and collections during the check. The arithmetic
scan streams exactly 14,364 pairs. The orbit check retains 168 group elements
and seven maps of 168 entries, and streams 128 subsets. All loop bounds come
from these fixed fixtures; the verifier accepts no external parameters. The
registered warning-as-error normal and optimized runs verify the same bounds
and explicit failure controls. A fixed-allocation rewrite would require a
separate runtime and is deferred unless this small exact replay becomes a
resource bottleneck. All functions remain below 60 physical lines. No source
or output file is written by the verifier.

## Open next questions

1. Determine the exact Boolean-cut optimum on the 168-element regular action.
   Start with a rigorous cut-cone primal/dual pair and a complete optimality
   argument. No attaining cut or global optimization certificate is provided.
2. Decide three-target word additivity with an invariant beyond this cut cone.
   Start with a nonlinear or integer label-count constraint that distinguishes
   the three-target endpoint. No such invariant or complete word census is
   provided here.

The structured questions and blockers are also in [TASK.json](TASK.json).
Neither follow-up is reserved by this package.

## Credit

This contribution was produced by Nick Petalas. Krzysztof Wojt supplied the
spectral cut inequality and its all-action scope in PR5063. James Reed supplied
the cut-model formulas and preceding open question in PR4968, with the
single-target and two-target word results due to JoyboyBrian and James Reed in
PR4974 and PR5005. Credit also Mihir Srivastava, Ross Richardson,
commdata2338, Gareth Davidson, PR1541 and the retained register-model lineage.
Those results are cited and not claimed as new or independently reverified.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
