# Two 3-cycles cost twelve calls

**Exact computer-assisted result in a formal model. No new κ.**
The selected conditional exponent stays 60403/20000000.

## Result

The setting is the formal model `M_2(F2[GL_3(F2)])` of #4939/#4950/#4968:

- A paid call is `D(g,N) = I + ([g]+[e])N`, where `g` is one of the six
  coordinate CNOTs and `N = uvᵀ` is a rank-one binary idempotent.
- Free scalar `GL_2(F2)` maps are allowed.
- Equality is formal, on arbitrary inputs.

Let `c` be a coordinate 3-cycle. Then

```text
diag([c],[c]) has no realizing word of length ≤ 11, so its cost is exactly 12.
```

The upper bound 12 is a shortest 3-cycle word (length 6) on each register. So
two 3-cycles share no paid work across the two registers: the cost is additive.

This answers the open question of [#4968](https://github.com/CrocSwap/integer-mult-bounds/pull/4968)
for its smallest case. #4974's support lemma gives exactly `ℓ_{GL_n}(g)` for a
single target, but support alone only bounds the largest target. The
permutation cuts of #4968 do not even certify a single 3-cycle; they reach
about 3.5 of 6.

## Method

`search.c` is an exact meet-in-the-middle search. Free scalar maps are
normalized away (#4939 step 1). Every paid call is an involution, so a word of
length `L ≤ 11` gives `T·W = X`, with `X` a product of at most 5 calls and `W`
of at most 6 calls. Consecutive equal letters cancel and are skipped.

- **Forward.** A depth-first search from `I` to depth ≤ 5 stores a 61-bit
  fingerprint with the minimum depth for each of the **16,292,362** distinct
  states.
- **Backward.** A depth-first search from `T` to depth ≤ 6 looks up every
  state. Fingerprints are deterministic, so a real solution always matches its
  key. A key match would be re-verified by an exact forward re-search. The
  run records **zero key matches**, which excludes every word of length ≤ 11.
- **Symmetry.** The target and the generator set are fixed by 36 maps:
  entrywise automorphisms of `GL_3(F2)` that fix `c` (conjugation by powers of
  `c`, optionally composed with inverse-transpose), times conjugation by
  `GL_2(F2)` on the registers. These maps are algebra automorphisms that fix
  `T`. If `T·W = X`, then `T·φ(W) = φ(X)`, and `φ(X)` lies in the same forward
  ball. So the backward first letter can range over orbit representatives, and
  here all 36 generators form one orbit. The search is also repeated **without
  this reduction**, over all 36 first letters in parallel shards, again with
  zero key matches.

## Evidence

`verify.py` uses the standard library and a C11 compiler. It takes about
75 s locally with 9 parallel shards. It checks:

1. **Compilation.** `search.c` compiles with `-Wall -Wextra -Werror`.
2. **Semantics.** The C products agree with the merged Python formal model
   (`research/swap-component-cut/formal.py`) on 84 random words of length
   0–6, as exact group-algebra states.
3. **State counts.** The distinct states at depth ≤ 1, 2, 3, 4 are 37, 1,033,
   26,551 and 663,496, matching the Python search.
4. **Positive controls.** `diag([c],[e])`, `diag([s01],[s12])` and
   `diag([s01],[s01])` have nothing at length ≤ 5, and their shortest length 6
   is found. The two swap cases match #4950/#4968.
5. **Upper bound.** The 12-call attaining word is checked in Python.
6. **Main search.** It runs with symmetry (36 symmetries, one orbit) and
   without it (36 first letters). Both give zero key matches.

Breaking the generator product in `search.c`, or perturbing the forward-ball
count, makes the verifier fail.

## Scope

Card `bit-new-register-model`, scope **changed** (see `TASK.json`). This is a
negative formal-model screen. It does not satisfy the card's native
construction gate.

This package covers only `n = 3` and `R = 2`. It does **not** settle:
- a third dirty, restored register;
- spectator address coordinates (`n ≥ 4`);
- other multi-target cases, such as transposition paths or stars on four or
  more coordinates;
- native operations, tariffs or κ.

Base: canonical main `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority
revision 7.
Claim: [#1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19139334).

## Reproduce

```sh
python3.12 -I -B research/two-three-cycle-additivity/verify.py
python3.12 -B scripts/research_package.py --package research/two-three-cycle-additivity
```

## Open next questions

1. **Does a dirty third register or a spectator coordinate let two 3-cycles
   share work?** For swaps, neither helps. For 3-cycles, only `R = 2`, `n = 3`
   is settled here. *First step:* run the same engine at `R = 3`, with 168
   generators. First measure the growth of the ball and add symmetry under
   register conjugation fixing `diag(c,c,e)`. *Blocked by:* search size only.

## Credit

- Mihir Srivastava (#4939), for the formal model.
- JoyboyBrian (#4974), for the single-target support lemma.
- PR1989, the GL2 corollary, commdata2338 (PR1414/PR1495), PR1541 and Gareth
  Davidson (PR1333), as credited in #4950/#4968.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review is claimed.
