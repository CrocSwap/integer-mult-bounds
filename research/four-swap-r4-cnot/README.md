# Four coordinate-SWAP targets at four registers: calls 2, 4, 6 excluded; q = 8, 10 remain

**Scoped register-model result; no new kappa.** The selected result, the selected
bit supplier and `upstream/` are unchanged; the bit side does not bind.

In the formal `F2[GL_2(F2)]` rank-one-idempotent register model with free
scalar mixing, this package asks for the exact paid-call minimum of four
coordinate-SWAP targets

```
T = diag([S],[S],[S],[S]),  S = aba = bab,
```

at exactly `r = 4` registers, every register an arbitrary dirty input restored
exactly. The upper bound is 12 calls (four disjoint `aba` words). Two written
invariants force any shorter word to have even length, so only `q = 8` and
`q = 10` can improve on 12. This package excludes `q = 2, 4, 6` by complete
finite meets and reproduces the known minima 3, 6, 6, 9 on the same engine.
The residual `q in {8, 10}` needs a meet at a measured ball of about 3e8
states; that obstruction is recorded exactly below and in `RECEIPT.json`.

This is the first `t = 4` case of the coordinate-CNOT line. PR1414 proves
`t = 2` costs 6 calls at any finite workspace; PR1491 proves `t = 3` costs 9
at exactly three registers; PR1541 proves `t = 3` costs 9 at any workspace
and records "**Four or more targets remain open**".

## 1. Model and complete operation alphabet

`G = GL_2(F_2) = S_3 = <a,b | a^2 = b^2 = (ab)^3 = 1>`, with `S = aba = bab`
(the coordinate swap). Work in the group algebra `F_2[G]`; factor order
matters and every coefficient is an exact formal coefficient. `r` registers
carry formal `F_2[G]` labels; a configuration is a column of `r` labels and a
word acts by left multiplication by its call matrices in `M_r(F_2[G])`.

A **paid call** is `C(g,N) = I + ([g]+1) N` with `g in {a,b}` and `N` any
binary rank-one idempotent over `F_2^r` (`N = v phi`, `phi(v) = 1`; 120 of
them at `r = 4`). Calls are unit-priced; this is the price rule of the
PR1333/1414/1491/1541 line and is a hypothesis of this result. Each call is
an involution, since `([g]+1)^2 = [g^2]+1 = 0`.

**Free scalar mixing**: arbitrary `GL_r(F_2)` basis changes cost zero and may
be interleaved anywhere between calls (the strongest convention of the line).
Invariant L2 below shows that for diagonal group-element targets this extra
freedom is useless: any word hitting `T` has mixing factor `U = I`.

The endpoint `diag([S],[S],[S],[S])` is accepted only on exact equality in
`M_4(F_2[G])`, so the statement covers arbitrary dirty inputs on all four
registers and their exact restoration. This is a finite-address identity
checked uniformly in the full formal algebra; natural-matrix equality is used
only as a necessary condition in the search and never as acceptance.

## 2. Three written invariants

Let a word of `q` calls hit `T = diag([S],...,[S],1,...)` with `t` SWAP
entries, and write `E_i = ([g_i]+1) N_i` so that call `i` is `I + E_i`.

**L1 (det parity).** Reduce `F_2[G]` through the sign homomorphism
`sigma: G -> C_2 = <x>`, `a,b |-> x`, onto `F_2[eps]/(eps^2)` with
`x = 1 + eps`. Then `[g]+1 |-> 0` for even `g` and `eps` for odd `g`, so a
call maps to `I + eps N_i` and `det(I + eps N_i) = 1 + eps` (rank one has
trace 1). The target maps to `I + eps D_t` with `D_t = diag(1_t, 0)`, so
`det = 1 + t eps`. Multiplicativity gives `q = t (mod 2)`. For `t = 4`, `q`
must be even.

**L2 (mixing is forced out; idempotent sum).** Since `eps^2 = 0`, a `q`-call
word maps to `I + eps sum_i N_i`. With free mixing, a mixed word is
`U (I + eps sum_i N_i)` for some `U in GL_r(F_2)`. Equality with
`I + eps D_t` forces `U = I` and `sum_i N_i = D_t` over `F_2`. At `t = r = 4`
this reads `sum_i N_i = I_4`; since `rank(N_i) = 1`, necessarily `q >= 4`,
and combined with L1, `q` is even and at least 4.

**L3 (inversion closure).** Each call is an involution, so the set of
`q`-call values is closed under inversion (reverse the word). The meet in
Section 4 uses this to avoid matrix inversion: `u v = T` has a solution in
the ball if and only if `v T` lies in the same ball.

## 3. Results

Engine A packs natural images (entrywise 2-dimensional representation of
`S_3`; states are `2r x 2r` binary matrices) and uses exact rank-1 fast
updates; engine B is written independently (tuple rows, index loops) and
agrees on every ball it checks. Every accepted word is verified exactly in
`M_r(F_2[G])` (formal engine, `RECEIPT.json`). All meets below returned zero
hits in the natural image, which is already sufficient for exclusion.

| instance | excluded calls | conclusion | predecessor |
|---|---|---|---|
| `t=1, r=1` | `q=1` direct, `q=2` by L1 | min 3 (`aba`) | folklore of the line |
| `t=2, r=2` | `q=2, 4` (meets) | min 6 | PR1414 two-register case |
| `t=2, r=3` (one dirty) | `q=2, 4` (meets) | min 6 | PR1414 workspace case at r=3 |
| `t=3, r=3` | `q=1,3,5,7` (meets), evens by L1 | min 9 | PR1491 |
| **`t=4, r=4`** | **`q=2, 4, 6` (meets)** | **`q in {8,10}` or 12** | none (PR1541 leaves t>=4 open) |

The `t=4, r=4` upper bound 12 is attained by four disjoint `aba` words on the
four diagonal idempotents; it is verified exactly in `M_4(F_2[G])`, and a
drop-one-call mutation fails. Ball sizes at `r = 4` (exact): 240, 32,651 and
3,639,920 states at depths 1, 2, 3. Engine-B cross-checks agree on all balls
through `r = 3` depth 4 (45,200 and 1,011,052 at depths 3, 4; close to but
not equal to PR1491's recorded 47,203 / 1,094,640, whose state notion appears
to refine the natural image; no exclusion here depends on that comparison).

A **natural-alias control** finds 252 pairs of distinct 3-call words at `r=3`
with equal natural image and unequal formal value. This is why the natural
image is used only for exclusion and every accepted word passes the full
formal algebra, consistent with PR1567's alias findings in the `GL_3(F_2)`
model.

## 4. The recorded obstruction for q = 8 and q = 10

By L1, a word with `q < 12` has `q in {8,10}`. A complete exclusion at `q = 8`
is a meet of the depth-4 ball against itself (L3), and `q = 10` needs the
depth-5 successor. The complete depth-4 stream at `r = 4` has
`240 * 3,639,920 = 873,580,800` products; a 2^28-slot bitmap sketch over the
whole stream estimates **2.74e8 distinct states** (the same estimator returns
2.97e6 against the exact depth-3 count 3,639,920, an 18% low bias, so the true
depth-4 count is plausibly about 3e8 or more). One exact depth-4 ball is
roughly 20 GB as a CPython set of 64-bit ints. The session's disk/install
policy excludes SAT or C++ tooling, and the search was stopped at the
pre-declared compute cap. This is a measured obstruction of the direct
route, not an impossibility statement: a sharded on-disk meet, a quotient
meet at `F_2[G]/J^3`, or a written coefficient-layer bound (the `J^2` layer
of `sum E_i + sum_{i<j} E_i E_j = T - I`) remain available.

## 5. Boundary: what this is not

No `q = 8` or `q = 10` word is found or excluded; the exact minimum at
`t = 4` is not settled. Nothing is claimed for `r > 4` (restored dirty
extras beyond the four target registers), for `t > 4`, for other target
tuples in `F_2[GL_2(F_2)]`, or for alphabets with non-rank-one couplings
(unit-priced rank-2 calls trivially halve the tariff and factor into two
rank-1 calls at twice the price; that changed hypothesis is not studied
here). No physical compiler, hosting, precision/tape, supplier, paid-moment
or analytic-transfer obligation is touched. No kappa claim; the selected
frontier and frozen inputs are unchanged.

## Open next questions

- **Question.** Is the exact minimum for `t = 4` at `r = 4` equal to 12?
  **Why it matters.** It decides whether the 3-calls-per-SWAP tariff holds at
  the first open target count of this line. **First step.** Sharded or on-disk
  4+4 meet at the measured depth-4 ball (~3e8 states, 4-8 passes), formal
  resolution of any hit; then the 5+5 meet or a written `J^2`-layer bound for
  `q = 10`. **Blocker.** Ball size (~20 GB exact, per-pass shard still
  multi-GB) and no solver tooling in this environment.
- **Question.** Does one restored dirty extra register (`r = 5`) change the
  `t = 4` picture? **Why it matters.** PR1541's `t = 3` result shows workspace
  can matter at the boundary of a claim. **First step.** L1/L2 extend verbatim
  (`sum_i N_i = D_t` with `t = 4 < r = 5`); run the depth-3 ball at `r = 5`
  and measure its growth before any deeper search. **Blocker.** Same ball-size
  growth (the `r = 5` depth-3 ball is expected to exceed the `r = 4`
  depth-3 count by at least an order of magnitude).

## Reproduce

Standard library only, Python 3.10+ (registered replay uses Python 3.12):

```sh
python3 -I -B research/four-swap-r4-cnot/verify.py          # quick, ~60 s
python3 -I -B research/four-swap-r4-cnot/verify.py --full   # + obstruction sketch, ~9 min
python3 -B scripts/research_package.py --package research/four-swap-r4-cnot
```

Expected final line of the quick run:

```text
PASS_FOUR_SWAP_R4_CNOT validation t2r2_min=6 t2r3_min=6 t3r3_min=9 t4r4 excluded={2,4,6} residual={8,10} upper=12 ball3=3639920 ball4_est=273823737 alias_pairs=252 no_new_kappa
```

## Task, overlap and credit

Task card: `bit-new-register-model` (chooser track `bit-mechanisms`, OS nonce
`b5ce6390976f7388a9834b2418b70942`, priority revision 3), refined to
`F2[GL2(F2)]/four-SWAP-targets/exactly-four-registers`; see `TASK.md` and
`TASK.json`. Final `find_overlap.py` refresh (complete pagination) for
`four coordinate swaps`, `four SWAP`, `four targets`, `r = 4 registers`,
`four-coordinate` found no four-target coordinate-CNOT claim; no matches is
not a novelty proof.

Credit Gareth Davidson (@bitplane, PR1333) for the model question;
commdata2338 for PR1414, PR1491, PR1495, PR1496; Cinna Davis
(1337isnot1337) for PR1541 and its open boundary; Ali Romman (PR468),
eumemic (PR288) and David Govea (PR720) for the register-model lineage.
Hanson Sun (@bbMisk) PR1567's natural-alias warning is independently
consistent with the alias control here. No predecessor executable or
enumeration is imported; engines A and B are written in this session.

Contributed by **Aaron Wang** with help from opencode. Apache-2.0.
