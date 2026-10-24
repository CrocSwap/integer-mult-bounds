# A dirty third register saves at most one call on two 3-cycles

**Exact computer-assisted partial result in a formal model. No new κ.**
The selected conditional exponent stays 60403/20000000.

## Result

The setting is the formal model `M_3(F2[GL_3(F2)])` of #4939/#4950/#4968,
with three scalar registers:

- A paid call is `D(g,N) = I + ([g]+[e])N`, where `g` is one of the six
  coordinate CNOTs and `N = uvᵀ` is one of the 28 rank-one binary idempotents
  of `M_3(F2)`. This gives 168 paid factors.
- Free scalar `GL_3(F2)` maps are allowed.
- Equality is formal, on arbitrary inputs. The third register is arbitrary
  and dirty, and must be restored exactly.

Let `c` be a coordinate 3-cycle. Then

```text
diag([c],[c],[e]) has no realizing word of length ≤ 10, and one of length 12.
```

So the cost is 11 or 12. At `R = 2` it is exactly 12 (#5005). The third
register can therefore save at most one of the twelve calls. Length 11 is
open.

| Check | Outcome |
|---|---|
| Upper bound | 12 calls (the `R = 2` word, register 2 untouched) |
| Length ≤ 8 | excluded in the registered replay (depth 3 + 5) |
| Length ≤ 10 | excluded in a recorded **local** run (depth 4 + 6, 53 min on 16 cores, 3.5·10¹¹ backward nodes) |
| Length 11 | **open** |

## Method

`search.c` extends the exact meet-in-the-middle engine of #5005 to three
registers. Free scalar maps are normalized away (#4939 step 1). Every paid call
is an involution, so a word of length `L ≤ f + b` gives `T·W = X`, with `X` a
product of at most `f` calls and `W` of at most `b` calls.

- **Forward ball.** A depth-first search from `I` stores a 61-bit fingerprint
  with the minimum depth. The distinct-state counts are 169, 22,051,
  2,705,791 and **325,910,698** at depth ≤ 1, 2, 3, 4. The radius-two count
  matches the merged order-7 package
  `research/gl3-order7-dirty-register-seed39ae` (1 + 168 + 21,882).
- **Backward search.** A depth-first search from `T` looks up every state. The
  search runs in forked workers that share the table.
- **Exact check of key matches.** A state at distance ≤ 4 is `A·B`, with `A`
  in the exact radius-two ball (stored as full states) and `|B| ≤ 2`. Every
  key match is tested this way. At depth 4 + 5 and 4 + 6 the runs record a few
  fingerprint collisions, and all of them are rejected.

Three word reductions are used. Each one keeps some shortest word, if any
exists:

1. **Cancellation.** Adjacent equal letters cancel, so they are skipped.
2. **Commutation order.** 9,912 of the 28,056 ordered pairs of distinct calls
   commute (an exact algebra test). Adjacent commuting letters are kept only in
   increasing order. Every commutation class has such a word: its
   lexicographically least one.
3. **Symmetry.** The target and the generator set are fixed by 36 maps. These
   are conjugation of `GL_3(F2)` by powers of `c`, optionally composed with
   inverse-transpose, times register conjugation by the `GL_2(F2) × GL_1(F2)`
   block matrices that fix `diag(1,1,0)`. These maps are algebra automorphisms
   that fix `T` and the ball, so the first two backward letters can be the
   lexicographically least pair of their orbit. That leaves 827 of the
   28,056 pairs. The commutation order then applies from the third letter on,
   so it never moves the chosen pair.

Parity cannot shortcut the remaining case. The five calls `0, 28, 84, 0, 84`
multiply to `I`. Their labels give the group relation `C01·C02·C12 = C12·C01`
on one register.

## Evidence

`verify.py` uses the standard library and a C11 compiler. In default mode it
checks:

1. **Compilation.** `search.c` compiles with `-Wall -Wextra -Werror`.
2. **Semantics.** The C products agree with the merged Python formal model
   (`research/swap-component-cut/formal.py`, `R = 3`) on 36 random words of
   length 0–5, as exact group-algebra states.
3. **Engine self-test.** The batched leaf fingerprints equal the direct ones
   on 33,600 children. The radius-two verifier accepts 400 words of length
   ≤ 4. The commuting-pair count is 9,912.
4. **State counts.** The distinct states at depth ≤ 1, 2, 3 are 169, 22,051
   and 2,705,791.
5. **Positive controls,** with and without symmetry:
   - `diag([c],[e],[e])` (cost 6, `research/three-cycle-address-floor`);
   - `diag([C7],[C7],[e])` (cost 6, the order-7 package);
   - two swaps `diag([s01],[s01],[e])` (cost 6, #4950).
   Each has nothing at length ≤ 5, and its length 6 is found.
6. **Upper bound.** The 12-call word and the odd relation are checked in
   Python.
7. **Main search.** No word has length ≤ 6 without symmetry, or length ≤ 8
   with it (36 symmetries, 827 pairs).

`verify.py --full` reruns the two local runs: depth 4 + 5 (length ≤ 9) and
depth 4 + 6 (length ≤ 10). Each needs about 9 GB of memory. `RESULT.json`
records their outputs, times, machine and the hash of the compiled source.

Changing `search.c` fails the hash binding to those runs. A broken generator
product (one dropped column update) also fails the semantic binding.

## Scope

Card `bit-new-register-model`, scope **changed** (see `TASK.json`). This is a
negative formal-model screen. It does not satisfy the card's native
construction gate.

This package covers only `n = 3`, `R = 3`. It does **not** settle:
- length 11;
- four or more registers;
- spectator address coordinates (`n ≥ 4`);
- native operations, tariffs or κ.

Base: canonical main `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority
revision 7.
Claim: [#1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19148597).

## Reproduce

```sh
python3.12 -I -B research/three-register-three-cycles/verify.py
python3.12 -I -B research/three-register-three-cycles/verify.py --full   # local, about an hour
python3.12 -B scripts/research_package.py --package research/three-register-three-cycles
```

## Open next questions

1. **Is there a word of length exactly 11?** *First step:* find a structural
   cut. Two examples: show that some call of a length-11 word must avoid
   register 2, which reduces to #5005; or extend #4974's support lemma to two
   targets. *Blocked by:* search size. The depth-5 forward ball has about
   4·10¹⁰ states.

## Credit

- Mihir Srivastava (#4939), for the formal model.
- JoyboyBrian (#4974), for the single-target support lemma.
- Cinna Davis (`research/gl3-order7-dirty-register-seed39ae`), for the
  `R = 3` ball count used as a cross-check.
- JoyboyBrian (`research/three-cycle-address-floor`), for the single-cycle cost
  6 used as a control.
- The predecessors credited in #4950/#4968/#5005.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review is claimed.
