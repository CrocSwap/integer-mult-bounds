# Even (order-3) diagonal targets: the 2-calls-per-target tariff is exact through t = 4

**Scoped register-model result; no new kappa.** The selected result, the selected
bit supplier and `upstream/` are unchanged; the bit side does not bind.

In the formal `F2[GL_2(F2)]` rank-one-idempotent register model with free
scalar mixing, this package asks for the exact paid-call minimum of `t` copies
of the **even** order-3 target

```
T_t = diag([c],...,[c]),  c = ab = (ba)^2,  order 3,
```

at exactly `r = t` registers, every register an arbitrary dirty input restored
exactly. This is the first even-target tuple class of the coordinate-CNOT
line: the predecessors study transposition (SWAP) targets, where the sign
quotient gives `sum_i N_i = D_t` with `t > 0`. For even targets the same
argument gives `t = 0`, so the inherited invariants change and no predecessor
conclusion transfers.

**Result.** The direct word is two calls per target,
`(I + ([a]+1)N)(I + ([b]+1)N) = I + ([c]+1)N`, i.e. `q = 2t`. It is optimal
in all four cases studied:

| instance | excluded calls | conclusion |
|---|---|---|
| `t=1, r=1` | `q=1` (direct check) | min 2 |
| `t=2, r=2` | `q=2` (meet) | min 4 |
| `t=3, r=3` | `q=2, 4` (meets) | min 6 |
| **`t=4, r=4`** | **`q=2, 4, 6` (meets)** | **min 8** |

So cross-register sharing does not beat `2t` through `t = 4`, in contrast to
nothing known either way for SWAP targets (where the tariff is `3t` and the
`t = 4` residual is open). A side observation: at `t = 2` exactly seven pairs
of 2-call words reach `T_2` in the natural image, and the same count holds in
the full formal algebra.

## Maintainer review supplement: the all-size question is settled in this model

The original finite census and its exact recorded results are retained below.
A subsequent [maintainer rank argument](../community-efficient1300-audit/combined-1763-rank-bound.md)
proves the tariff is exactly **2t for every t and every r >= t**, including
restored dirty extras, under this same paid-call/free-scalar model.
Augmentation forces the total free mixing to identity; each paid call has
natural-image rank difference one, while the target has rank difference 2t.
Rank subadditivity proves the lower bound and the direct formal word attains it.
Thus the general-t questions in the original **Open next questions** section
are historical, rather than a reason to spend inference on larger censuses.
The supplement gives no SWAP tariff, richer-alphabet or native supplier claim.
The finite census and corrected degree-filter analysis remain Aaron Wang's work.

## 1. Model and complete operation alphabet

`G = GL_2(F_2) = S_3 = <a,b | a^2 = b^2 = (ab)^3 = 1>`, with `c = ab`
(order 3) and `S = aba = bab` (the coordinate swap). Work in the group
algebra `F_2[G]`; `r` registers carry formal `F_2[G]` labels and a word acts
by left multiplication by its call matrices in `M_r(F_2[G])` (first call
leftmost).

A **paid call** is `C(g,N) = I + ([g]+1) N` with `g in {a,b}` and `N` any
binary rank-one idempotent over `F_2^r` (`N = v phi`, `phi(v) = 1`; 120 of
them at `r = 4`). Calls are unit-priced; this is the price rule of the
PR1333/1414/1491/1541/1705 line and is a hypothesis of this result. Each
call is an involution, since `([g]+1)^2 = 0`.

**Free scalar mixing**: arbitrary `GL_r(F_2)` basis changes cost zero and may
be interleaved anywhere. Invariant L2' below forces any word hitting `T_t`
to have mixing factor `U = I`.

The endpoint `[c] I_r` is accepted only on exact equality in `M_r(F_2[G])`,
covering arbitrary dirty inputs on all registers and their exact
restoration. Natural-matrix equality is used only as a necessary condition
for exclusion and never as acceptance.

## 2. Written invariants (L1', L2')

Write `x = [a]+1`, `y = [b]+1` in `F_2[G]`.

**L1' (det parity).** Reduce `F_2[G]` through the sign homomorphism
`sigma: G -> C_2 = <z>`, `a,b |-> z`, onto `F_2[eps]/(eps^2)` with
`z = 1 + eps`. An odd `[g]+1` maps to `eps`, an even one to 0. Since `c` is
even, the target maps to `I_r` and `det = 1`. A call maps to `I + eps N_i`
with `det = 1 + eps`. Multiplicativity gives `q = 0 (mod 2)`: every word
hitting `T_t` has even length. (Odd lengths are therefore never searched.)

**L2' (mixing forced out; idempotent sum zero).** Since `eps^2 = 0`, a
`q`-call word maps to `U (I + eps sum_i N_i)` for the total mixing
`U in GL_r(F_2)`. Equality with `I_r` forces `U = I` and `sum_i N_i = 0`
over `F_2`. (For SWAP targets the corresponding identity is
`sum_i N_i = D_t`; that premise is gone here.)

## 3. Free-layer system (degree 1-3): screening filter, not necessary

**Correction** (review of
https://github.com/CrocSwap/integer-mult-bounds/pull/1763). An earlier
version of this section claimed the degree 1-3 system below as "necessary
conditions for any hitting word". That claim is false. Counterexample: at
`r = 1` set every projector to `[1]` and take the word `b a b a`. Each call
is then `I + ([g]+1)[1] = [g]`, so the word value is `[baba] = [(ba)^2] =
[ab] = [c]`, an exact target word; but the claimed condition `sum_ba = 0`
fails, because the word has three ordered b-before-a pairs and `sum_ba =
[1]`. The package's own engine confirms it:
`formal_is_target(formal_word_value(word,1),1)` is `True` while
`layer_ok_even_target(word,1)` is `False` (regression
`test_layer_counterexample_baba` in `test_verify.py`).

Where the old derivation went wrong: it expanded `prod_i (I + E_i) = [c] I_r`
with `E_i = ([g_i]+1) N_i` in the free filtered algebra
`F = F_2<x,y>/(x^2, y^2)`, `x = [a]+1`, `y = [b]+1`, `[c]+1 = x + y + xy`, and
matched degrees 1-3 against the kernel elements

```
R = xyx + yxy + x + y          (from [S]+1 = xyx+xy+yx+y = yxy+yx+xy+x)
Z = z + z^2 + z^3,  z = x+y+xy (from [c]^3 = 1),
```

claiming the kernel of `F -> F_2[G]` up to degree 3 is spanned by `R` and `Z`.
But `Z` carries degrees up to 6, and its truncation to degree at most 3,
`x + y + yx`, maps to `[ba] + [e] != 0`: it is not in the kernel. Up to degree
3 the kernel is 1-dimensional, spanned by `R` alone (the seven monomial
images `1, x, y, xy, yx, xyx, yxy` have rank 6 over `F_2`; both facts are
machine-checked in `test_verify.py`). Matching degrees 1-3 is therefore
justified only when the word length is `q <= 3`, where the difference
`prod_i (I + E_i) - I - (x+y+xy) I_r` itself has degree at most 3. For
`q >= 4` kernel elements of degree 4 and higher absorb the low-degree
mismatch, which is exactly what happens for `b a b a`.

**Corrected statement (class: words of length `q <= 3`).** For a hitting
word of length at most 3, the difference lies in `<R> tensor M_r(F_2)` and
comparing degrees 1-3 gives, for some `lam in M_r(F_2)`:

```
sum_a N_i        = sum_b N_i        = I_r + lam
sum_{ab-pairs} N_i N_j               = I_r
sum_{ba-pairs} N_i N_j               = 0
sum_{aba-triples} N_i N_j N_k        = lam
sum_{bab-triples} N_i N_j N_k        = lam
```

The counterexample `b a b a` has length 4 and lies outside this class. An
exhaustive check over all 1898 words of length 1-3 at `r = 1, 2` finds
exactly one hitting word, and it satisfies this system (`test_verify.py`).
No claim is made for words of length 4 or more.

**What remains of the old system.** `layer_ok_even_target` keeps the looser
old form (`sum_ab = I_r + nu`, `sum_ba = 0`, triples `lam + nu`) as a
screening filter only. It accepts every attaining word used here
(`word_even`, `t = 1, 2, 3, 4`) and rejects the wrong-target control, but it
rejects genuine target words (the counterexample above) and accepts
non-target words (at `r = 2`, `a b` on one projector passes the filter and
is not a target), so it is neither necessary nor sufficient and is never
used to exclude candidates. All exclusions below come from L1', the `q = 1`
direct check and the meets; the reported minima are unchanged if the filter
is made vacuous (`test_minima_do_not_rely_on_layer_condition`).

## 4. Meets and their completeness

Exclusion runs in the entrywise natural image (2-dimensional representation
of `S_3`), a homomorphic image of `M_r(F_2[G])`: an empty meet there excludes
the formal word too. For `q = 2k` the meet enumerates all values `u` of
`k`-call words and tests `u^{-1} T` for membership in the same set (calls are
involutions, so the inverse value is tracked by reversed updates). Every
accepted word is verified exactly in `M_r(F_2[G])` by engine B.

**Completeness with cross-depth value recurrence.** The BFS keeps one value
per state, but values recur across depths (`C C = I`, `C C C = C`), so the
meet covers `u, v` in `N_k` (values first reached at depth `k`). Any omitted
pair has a factor of length `j < k`, putting `T` in `V_{j+k}` with `j + k <
2k`; those lengths are excluded by L1' (odd) or by the shorter meets
(`q = 2, 4`). The `q = 6` exclusion at `t = 4` is therefore complete given
the `q = 2, 4` exclusions and L1'.

**Engine calibration.** At `r = 4` the exact counts of word *values* at
depths 1-3 are `240 / 32,651 / 3,639,920`, exactly the ball counts PR1705
records for the same generator set. (The counts of values first reached at
each depth are `240 / 32,650 / 3,639,680`; the differences are the identity
value at depth 2 and the 240 one-call values at depth 3, both verified in
`RECEIPT.json`.) Two engines, packed natural rank-1 updates and an
independently written formal coefficient implementation, agree on every
small meet and on all minima.

## 5. Boundary: what this is not

No word shorter than `2t` is found or excluded beyond `t = 4`; `t = 5` and
`r > t` (restored dirty extras) are untouched. Nothing is claimed for other
even or odd target tuples in `F_2[GL_2(F_2)]`, for other alphabets (the
generator-priced `AGL_2` alphabets or `UT_3(F_2)` commutators are different
models), or for alphabets with non-rank-one couplings. No physical compiler,
hosting, precision/tape, supplier, paid-moment or analytic-transfer
obligation is touched. No kappa claim; the selected frontier and frozen
inputs are unchanged.

## Open next questions

- **Question.** Is `q*(t) = 2t` for even order-3 targets at `t = r = 5` and
  beyond, or does cross-register sharing first pay there?
  **Why it matters.** It decides whether the tariff pattern is a general law
  of the even-target line. **First step.** Run the same engine at `t = r = 5`
  (480 generators) and measure the depth-3 ball before any deeper search.
  **Blocker.** Ball growth: the `r = 5` depth-3 ball should exceed the
  `r = 4` count of 3.6e6 states by at least an order of magnitude.
- **Question.** Can a written degree-complete kernel analysis exclude
  `q < 2t` at general `t = r`, without a meet? (The degree 1-3 free-layer
  system of section 3 cannot: it is necessary only for words of length
  `q <= 3`.)
  **Why it matters.** A written exclusion removes the exponential meet from
  the even-target line. **First step.** Compute the kernel of
  `F -> F_2[G]` in degree 4 (the smallest case where the low-degree matching
  breaks) and re-derive conditions on the degree 1-4 layer sums there.
  **Blocker.** From `q = 4` on, kernel elements of degree 4 and higher
  absorb the low-degree mismatch (the `b a b a` counterexample of section 3
  is the smallest instance); controlling those higher-degree kernel terms is
  the missing step.

## Reproduce

Standard library only, Python 3.10+ (registered replay uses Python 3.12):

```sh
python3 -I -B research/even-target-cnot-census/verify.py --check-receipt   # ~50 s
python3 -I -B research/even-target-cnot-census/test_verify.py              # rejection controls
python3 -B scripts/research_package.py --package research/even-target-cnot-census
```

Expected final line of the verifier:

```text
PASS_EVEN_TARGET_CNOT_CENSUS t1r1_min=2 t2r2_min=4 t3r3_min=6 t4r4_upper=8 t4r4_excluded={2: 0, 4: 0, 6: 0} balls4=240,32651,3639920 pr1705_ball_match=True no_new_kappa
```

## Task, overlap and credit

Task card: `bit-new-register-model` (chooser track `bit-mechanisms`, OS nonce
`96dd0470d4d1febfb9db9174583232e0`, priority revision 3), refined to
`F2[GL2(F2)]/even-order3-targets/exactly-r=t`; see `TASK.md` and `TASK.json`.
`find_overlap.py` refreshes for `order-3 target`, `3-cycle target`, `cyclic
target`, `even target`, `diag([ab]`, `order-three` and the four-swap terms
found no competing even-target claim; no matches is not a novelty proof.
The concurrent balanced ten-call four-SWAP residual
(https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-18919080)
is a different object (transposition targets at `r = 4`).

Credit Gareth Davidson (@bitplane, PR1333) for the model question and scalar
normalization; commdata2338 (PR1414, PR1491, PR1495, PR1496), Cinna Davis
(1337isnot1337, PR1541), Aaron Wang (PR1705, whose recorded `r = 4` ball
counts calibrate the engine here), Ross Richardson (PR1722, label
saturation), juper997 (PR1478) and steph4n-gh (PR1573) for the surrounding
register-model line; Ali Romman (PR468), eumemic (PR288) and David Govea
(PR720) for the lineage. No predecessor executable is imported; engines A
and B are written in this session.

Contributed by **Aaron Wang** with help from opencode. Apache-2.0.
