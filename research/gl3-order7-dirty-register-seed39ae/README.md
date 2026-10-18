# A dirty register does not shorten a GL3 order-seven target pair

**Scoped exact minimum in a finite formal register model. No selected supplier or new `kappa` is claimed.**

## Model and result

Work over the formal group algebra `R = F2[GL3(F2)]`. The six paid address labels are all coordinate CNOTs

```text
C01 = I + E01,  C12 = I + E12,  C20 = I + E20,
C10 = I + E10,  C21 = I + E21,  C02 = I + E02.
```

They generate all 168 elements of `GL3(F2)`. Let

```text
C = C01 C12 C20 = [[0,1,1], [1,1,1], [1,0,1]].
```

`C` has order seven and shortest coordinate-CNOT word length three. There are exactly three scalar registers. The endpoint is

```text
diag([C], [C], 1)
```

on arbitrary inputs, including an arbitrary dirty third register restored exactly. Scalar `GL3(F2)` mixing is free. Every paid call has the form

```text
F(g,N) = I + ([g] + 1) N,
```

where `g` is one of the six labels and `N=uv^T` is a rank-one idempotent over `F2` (`v^T u=1`). In characteristic two these calls are involutions. There are 28 allowed `N` and 168 paid factors total.

The exact minimum is **six paid calls**. Three calls implement `C` on the first register, three on the second, and the third stays fixed. Exhaustive formal group-algebra search finds no five-call word, even with the free scalar mixing and dirty register.

The free mixing normalization is exact: augmentation sends every address `[g]` to 1, so the scalar matrices in any successful boundary word multiply to the identity. Moving them through the paid calls conjugates each standard rank-one projector into some `uv^T` with `v^T u=1`. The census includes all 28 such projectors at each of the six paid labels. It includes every free scalar mixing pattern without charging or fixing a frame.

## Complete finite evidence

The verifier stores every coefficient in the 168-element group basis of `F2[GL3(F2)]`; it never accepts equality from the natural three-dimensional representation. A radius-two identity ball has unique-state shells `1, 168, 21,882`, for 22,051 states. On the target side, the verifier streams every raw word of length zero through three rather than storing duplicate states:

| Target-side suffix length | Words checked |
|---:|---:|
| 0 | 1 |
| 1 | 168 |
| 2 | 28,224 |
| 3 | 4,741,632 |

None of the 4,770,025 target-side endpoints lies in the identity-side ball. Any word of length at most five splits into a prefix of length at most two and a suffix of length at most three. Every paid factor is its own inverse, so a target factorization would put `target * suffix^-1` in both sets. This excludes every word through length five.

The six-call direct word is checked on all `3*168 = 504` basis rows in the faithful regular action. The verifier checks all 168 factor inverses, confirms the join logic with one-target three-call and identity positive controls, rejects the wrong CNOT order, and rejects omission of each direct call.

## Scope and overlap

This refines the `bit-new-register-model` card by changing the address algebra from rational abelian frames to the nonabelian formal algebra `F2[GL3(F2)]`, and by adding one arbitrary dirty scalar role to a two-target order-seven endpoint.

The closest work is:

- [PR #1567](https://github.com/CrocSwap/integer-mult-bounds/pull/1567) gives exact minima for all 27,308 two-register GL3 target pairs with the full six-label coordinate-CNOT alphabet and direct cost at most nine. This package asks whether a restored third role changes one such order-seven target pair.
- [PR #1495](https://github.com/CrocSwap/integer-mult-bounds/pull/1495) adds a third role for two order-two swap targets using all six labels. The target order differs.
- [PR #1496](https://github.com/CrocSwap/integer-mult-bounds/pull/1496) covers two order-four GL3 targets with two scalar registers and all six labels.
- [PR #1491](https://github.com/CrocSwap/integer-mult-bounds/pull/1491) covers three GL2 coordinate swaps; [PR #1720](https://github.com/CrocSwap/integer-mult-bounds/pull/1720) uses an S4 adjacent-transposition alphabet and a four-cycle target.

The live REST census covered all 419 open PR records through 2026-10-14 08:22 UTC. The latest complete cached Discussion snapshot had 371 records, fetched 08:16 UTC; the exact GL3 order-seven three-register query returned no match. [OVERLAP.json](OVERLAP.json) records the heads, coverage and API refresh limit. No literature-priority claim is made.

This is a finite model result, not a multiplication supplier. It establishes no physical source access, selected-supplier occurrence, compiler or hosting cost, precision contract, recursive-moment change, new `kappa`, or full multiplication theorem. The selected record and its inherited assumptions are unchanged.

## Reproduce

From the repository root with Python 3.12 and the standard library:

```sh
python3.12 -I -B research/gl3-order7-dirty-register-seed39ae/verify.py
python3.12 scripts/research_package.py --package research/gl3-order7-dirty-register-seed39ae --check-only
python3.12 scripts/research_package.py --package research/gl3-order7-dirty-register-seed39ae
```

Expected direct result line:

```text
PASS_GL3_ORDER7_DIRTY_REGISTER registers=3 factors=168 prefix=22051 suffix_words=4770025 hits=0 minimum=6
```

## Open next questions

Can a second dirty role change the minimum for this same order-seven target and all six labels? First derive the fully charged target and direct bill for exactly four registers, then use an optimistic bound to decide whether a radius search can affect that bill. The larger rank-one projector inventory and target-side ball are the main blockers.

## Credit

Prepared by Cinna Davis with substantial OpenAI Codex assistance in task refinement, algebra, exact search, verification and writing. No independent human review or proof-assistant formalization is claimed. New work is Apache-2.0. Predecessor work is attributed above and pinned in [SOURCES.json](SOURCES.json).
