# Port the 134/329 contact to the original 74-CLEAR word

**Conditional κ = 0.003650982374396.** This applies the literal [#7612 contact
rechart](https://github.com/CrocSwap/integer-mult-bounds/pull/7612) at
`e814828ee5b869c9468282d57ba28c364b07d130` to
[exact #7642](https://github.com/CrocSwap/integer-mult-bounds/pull/7642)
at `d7f82810689ed2cd649ec9aaaf3b1485b585c82e`, κ `0.003650666180757`.
The exact campaign increase is `0.000000316193639`, or **+0.0086612586%**.
The exact percentage is `31619363900/3650666180757 %`. The admissible point exceeds #7642's exact raw upper bound.

The common ADD at old clock 41051 moves from chart 618 to 373. Role
134 begins at chart 3 and returns in chart 913 with the old signed
contribution of role 329. Role 329 begins at 373 and returns in chart
733 with its own value. This removes a paid sender MOVE, with the
normalized scalar tape, complete owned interfaces, 74 lifetimes and
required public outputs preserved. [Exact proof](PROOF.md)

The literal candidate has canonical SHA-256
`dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02`.
The same [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
signed caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d` invokes
it 17 times. The paid delta is `{1:-34,2:+34,3:-17,4:-17,5:+17}`.

| Complete signed resource | #7642 | This word |
| --- | ---: | ---: |
| Paid positions | 110,349 | 110,332 |
| Productive positions | 22,461 | 22,461 |
| Rank surplus | 1,424 | 1,424 |
| Ordinary upper bound | 782,685,204 | 782,668,204 |
| Context precision coefficient | 2,430 | 2,430 |
| Elementary tape records upper bound | 25,448,575,552 | 25,445,676,576 |
| Signed catalogue maps | 3,040 | 3,041 |

The complete local native and signed stages exited 0 in 351.77
and 244.16 seconds. The exact phase gate checked the seven
changed routes and three compositions on every forward and adjoint
column. Retained controls reject a missing MOVE, wrong chart, omitted
ADD and wrong absolute phase. The signed stage checked both exact
prices, 104 boundaries, and 54 strict plus four functional outer
inequalities, including the complete caller, ordinary, precision and
tape costs. [Pinned receipts](receipts/)

## Reproduce

Use CPython 3.12, Git and a POSIX environment. From the repository root:

```sh
python3.12 -I -B research/p104-contact134-329-original-clear/replay.py --work ../contact134-329-replay
python3.12 -B scripts/research_package.py --package research/p104-contact134-329-original-clear
```

The first command resolves exact #7605 and #7642 dependencies and
runs the complete native and signed stages with 480 seconds each.
Pass explicit source checkout roots to reuse authenticated dependencies.
The second command covers the sealed bindings and directed invoice.
The generated word is authenticated by canonical decompressed bytes.

## Credit

Clear1nsight's #7612 supplies the exact contact rewrite. SYLforge's
[#7616](https://github.com/CrocSwap/integer-mult-bounds/pull/7616)
previously ported it in a larger composition with extra lifetimes.
This isolates its interaction with #7642 on exactly 74 lifetimes.
DreamingOfClouds's #7610 supplies the existing main-46 merge. Ali
Romman's #7605 supplies the native and application lineage through
Hao Yan's #7604. Rohan Arun supplied #7113. Retained compiler, pricing
and recovery authors are attributed in the dependency and notice.
OpenAI Codex and subagents materially assisted the proof, port and
verification.

## Open next questions

- Check the exact all-size application and interface transfer through
  substantive review. The existing five conditional premises remain.
  Start with the compiler maps and complete signed receipt.
- A further paid reduction requires a distinct exact candidate and
  the same complete cost checks. No additional candidate is part of
  this package.
