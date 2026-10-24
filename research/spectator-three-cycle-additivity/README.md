# A spectator coordinate does not help two 3-cycles

**Exact computer-assisted result in a formal model. No new κ.**
The selected conditional exponent stays 15108879/5000000000 (#4610).

## Result

The setting is the formal model `M_R(F2[GL_n(F2)])` of #4939/#4950/#4968
at `n = 4`, `R = 2`:

- A paid call is `D(g,N) = I + ([g]+[e])N`, where `g` is one of the 12
  coordinate CNOTs of `GL_4(F2)` and `N = uvᵀ` is one of the 6 rank-one binary
  idempotents of `M_2(F2)`. This gives 72 paid factors.
- Free scalar `GL_2(F2)` maps are allowed.
- Equality is formal, on arbitrary inputs.

Let `c` be the coordinate 3-cycle on coordinates 0, 1, 2. Address coordinate 3
is a spectator: the endpoint fixes it, but calls may write it. Then

```text
diag([c],[c]) has no realizing word of length ≤ 11, so its cost is exactly 12.
```

The upper bound is #5005's word: a shortest 3-cycle word on each register.
So a spectator coordinate gives two 3-cycles no shared paid work, just as at
`n = 3` (#5005). This answers the `n ≥ 4` part of #5005's open question for its
smallest case. A single 3-cycle already costs 6 with any spectators
(`research/three-cycle-address-floor`).

| Check | Outcome |
|---|---|
| Upper bound | 12 calls |
| Length ≤ 9 | excluded in the registered replay (depth 4 + 5) |
| Length ≤ 10 | excluded in a recorded **local** run (depth 4 + 6) |
| Length ≤ 11 | excluded in a recorded **local** run (depth 5 + 6, 721,626,127 forward states) |

## Method

`search.c` is an exact meet-in-the-middle search with a **sparse** state.
Each of the four matrix entries is a sorted set of `GL_4(F2)` indices with F2
coefficients. A product of `L` calls has at most `2^L` terms per entry, so the
20,160-element group needs no dense bitsets. The search structure is the same
as in #5005 and #5292:

- **Cancellation.** Adjacent equal letters cancel.
- **Commutation order.** 1,584 of the 5,112 ordered pairs of distinct calls
  commute (an exact algebra test). Adjacent commuting letters are kept only in
  increasing order.
- **Symmetry.** The target and the generator set are fixed by 36 maps:
  conjugation of `GL_4` by the coordinate permutations commuting with `c`,
  optionally composed with inverse-transpose, times `GL_2(F2)` register
  conjugation. The first two backward letters are the lexicographically least
  pair of their orbit, which leaves 142 of 5,112 pairs. The commutation order
  applies only from the fourth backward letter on.
- **Exact check of key matches.** A state at distance ≤ 5 is `A·B`, with `A`
  in the exact radius-two ball (4,297 stored states) and `|B| ≤ 3`. Every key
  match is tested this way. The final run recorded one key match, and the exact
  test rejected it. An earlier length-11 run used a build whose exact test only
  reached distance 4. It was discarded and rerun with the final source.

The distinct-state counts are 73, 4,297, 240,565, 13,231,207 and 721,626,127
at depth ≤ 1, …, 5.

## Evidence

`verify.py` uses the standard library and a C11 compiler. In default mode it
checks:

1. **Compilation.** `search.c` compiles with `-Wall -Wextra -Werror`.
2. **Semantics.** The C products agree with the merged Python formal model at
   `n = 4`, `R = 2` on 36 random words of length 0–5, as exact group-algebra
   states.
3. **Engine self-test.** There are 1,584 commuting pairs and the exact
   radius-two ball. Twelve random words of length 3–5 verify within their
   length, and `diag(c,c)` is rejected at distance ≤ 5.
4. **State counts.** The distinct states at depth ≤ 1, 2, 3, 4 are as listed
   above.
5. **Positive controls,** with and without symmetry:
   - `diag([c],[e])` (cost 6, as in `three-cycle-address-floor`);
   - two swaps `diag([s01],[s01])` (cost 6, as in #4950).
   Each has nothing at length ≤ 5, and its length 6 is found.
6. **Mixed target.** `diag([c],[s01])` has nothing at length ≤ 8. A recorded
   local depth 4 + 5 run finds its length 9.
7. **Upper bound.** The 12-call word is checked in Python.
8. **Main search.** Nothing at length ≤ 6 without symmetry, and nothing at
   length ≤ 9 with it.

`verify.py --full` reruns the local depth 4 + 6 and 5 + 6 runs. The second needs
about 8 GB of memory. `RESULT.json` records their outputs, times, machine and
the hash of the compiled source.

Changing `search.c` fails the hash binding to the recorded runs. Dropping one
column update in the generator product fails the semantic binding.

## Scope

Card `bit-new-register-model`, scope **changed** (see `TASK.json`). This covers
only `n = 4` (one spectator) with `R = 2`. It does **not** settle:
- `n ≥ 5`;
- a dirty third register (#5292 leaves length 11 open at `R = 3`);
- other targets;
- native operations, tariffs or κ.

Base: canonical main `1ec1119972c9aefe42525172d07b332fcff81cb4`, priority
revision 7.

## Reproduce

```sh
python3.12 -I -B research/spectator-three-cycle-additivity/verify.py
python3.12 -I -B research/spectator-three-cycle-additivity/verify.py --full   # local, about 8 GB
python3.12 -B scripts/research_package.py --package research/spectator-three-cycle-additivity
```

## Open next questions

1. **Every `n ≥ 4`.** *First step:* adapt the written-spectator reduction of
   `three-cycle-address-floor`. A short word can write only a few spectator
   rows. Restrict the unwritten ones to their zero subspace, which reduces the
   question to finitely many `n`, including this one. *Blocked by:* a written
   argument for two targets.

## Credit

- Mihir Srivastava (#4939), for the formal model.
- JoyboyBrian (#4974, `three-cycle-address-floor`), for the single-cycle
  spectator theorem.
- The predecessors credited in #4950/#4968/#5005/#5292.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review is claimed.
