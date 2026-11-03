# Proof: price-null exchanges need irreducible cycles

## Model

This is the register-tax model of PR6345 (`research/p104-frontier-symmetric-ladders`,
DreamingOfClouds). A register's timeline is a chain `c = (c_0, …, c_m)` of integer
dimensions. Its tax is the multiset `{|c_{i+1} − c_i|}` of step sizes, minus one copy of the
span `c_m − c_0` when the register is a helper. The price of a word depends on the word only
through the summed tax over all registers. A change replaces some chains by others. Write
`Δ_r = tax(new_r) − tax(old_r)` as a signed multiset. The change is **price-null** when
`Σ_r Δ_r = 0`.

PR6345 names three freedoms:

- **F1.** A helper with one step may re-span; PR6345 shows its tax stays zero.
- **F2.** One register keeps its endpoints and its step multiset and reorders its stops (`Δ_r = 0`).
- **F3.** A stop move in one register cancels a stop move in another (`Δ_A + Δ_B = 0`).

A *one-stop window chain* is `(a, s, b)` with `a < s < b`. Its steps are `{s − a, b − s}` and
their sum is the window length `L = b − a`. Endpoints stay fixed in every change below, so a
helper's span term cancels inside its own `Δ`. The statements below hold for helpers as well as
main registers.

## Theorem 1: no pairwise exchange across window lengths

Let `A` and `B` be one-stop window chains with lengths `L_A ≠ L_B`, and let each change only its
stop. If `Δ_A + Δ_B = 0`, then `Δ_A = Δ_B = 0`.

*Proof.* Write `P = {s, L_A − s}` and `P' = {s', L_A − s'}` for `A`'s old and new step pairs, and
`Q`, `Q'` for `B`'s. If `s'` lies in `P`, then `s' = s` or `s' = L_A − s`, so `P' = P` and
`Δ_A = 0`. Then `Δ_B = 0` too. Otherwise `P'` and `P` are disjoint, so `Δ_A = P' − P` has the
two-element positive part `P'`. The hypothesis says `P' − P = Q − Q'`, whose positive part is
contained in `Q`, which has two elements. Therefore `P' = Q` as multisets, and summing gives
`L_A = L_B`. This contradicts `L_A ≠ L_B`. ∎

**Corollary (F1–F3 do not connect the fibre).** Take a configuration consisting only of
one-stop window main chains with pairwise distinct window lengths. Every configuration reachable
by any finite sequence of F1, F2 and F3 moves gives every register its original step multiset.
F1 does not apply to main chains, F2 keeps the multiset by definition, and by Theorem 1 every F3
move between two such registers has `Δ_A = Δ_B = 0`.

## Theorem 2: irreducible cycles of every length

Let `k ≥ 3`. Take positive integers `u_1, …, u_k` and `c > 0` such that the `2k` numbers
`u_j` and `u_j + c` are pairwise distinct. Indices are mod `k`. Register `i` has window
`[0, L_i]`, `L_i = u_i + u_{i+1} + c`, and moves its stop from `u_i` to `u_i + c`. Its steps
change from `{u_i, u_{i+1} + c}` to `{u_i + c, u_{i+1}}`. Then:

1. both stops are interior, since `u_i > 0` and `u_{i+1} > 0`;
2. the whole change is price-null;
3. no nonempty proper subset `S` of the registers has `Σ_{i∈S} Δ_i = 0`.

*Proof.* `Δ_i = [u_i + c] + [u_{i+1}] − [u_i] − [u_{i+1} + c]`. All `2k` values are distinct,
so in `Σ_{i∈S} Δ_i` the coefficient of `[u_j]` is `[j − 1 ∈ S] − [j ∈ S]`, and that of `[u_j + c]`
is `[j ∈ S] − [j − 1 ∈ S]`. All coefficients vanish exactly when `j ∈ S ⇔ j − 1 ∈ S` for every
`j`, that is when `S` is empty or everything. Taking `S` = everything gives (2). ∎

With `u_j = 2^{j−1}` and `c = 2^k`, the values `u_j < 2^k < u_j + c` are distinct. The windows
`2^{i−1} + 2^i + 2^k` (and `2^{k−1} + 1 + 2^k` for the wrapping register) are pairwise
distinct because their binary forms differ. The corollary then applies: for every `k ≥ 3` this
price-null change is not reachable from its start by F1–F3, even through intermediate states.

## Smallest three-register example

The checker searches every change of three one-stop window chains with distinct lengths
`L_1 < L_2 < L_3`. For each `L_3` from 4 up, it checks every unordered old and new stop with
every register changed. None exists with `L_3 ≤ 5`. At `L_3 = 6` the first is

| window | old steps | new steps |
|---|---|---|
| 4 | {1, 3} | {2, 2} |
| 5 | {2, 3} | {1, 4} |
| 6 | {2, 4} | {3, 3} |

Old and new totals are both `{1, 2, 2, 3, 3, 4}`. By Theorem 1 no two of these changes cancel.
Every dimension in the example is at most 6, inside the rank range 1..9 that PR6345 reports
for its helpers.

## Scope

This is a statement about the tax model and the three freedoms as PR6345 states them. It does
not say whether the PR6167 frame table, event order and legality checker admit such a cycle in
the actual word, or whether the 59 words PR6345 found contain one. A legal word must also keep
the frame table, inventories and replay fields fixed; the tax model ignores those constraints.
