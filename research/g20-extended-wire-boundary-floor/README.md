# Extra wires do not lower the G20 boundary below 38 ADDs

This scoped proof was produced by Nick Petalas. **No new κ.** It answers the
open question of unpaidmoon's
[PR6641](https://github.com/CrocSwap/integer-mult-bounds/pull/6641)
(`5af623f5912f997163639e061feca4ebcf7e189e`): neither a priced scratch wire
nor a gate that leaves the 32 boundary wires lowers a legal GL(2)-commutant
side of the pinned PR5840 G20 boundary below **38 unit ADDs**. This holds for
any number of extra wires, under any nonnegative tariff, and whether each extra
wire is clean, dirty and restored, or left holding garbage. The scratch-free
words attain 38, so the exact minimum stays **38 per side and 76 per port**.

## Lemma

Work over F2 on `N = n + k` wires. A unit ADD is `x_d <- x_d + x_s` with
`d != s`; a SWAP costs three ADDs. A word of length `T` has matrix `M`. Let `A`
be the `n x n` block of `M` on a fixed set of n data wires (data outputs as
functions of data inputs). Let `v(A)` be the number of components of the
undirected graph on the data wires with an edge `{i, j}` when `A_ij = 1` or
`A_ji = 1`, and let `z(A)` be the number of zero diagonal entries of `A`. Then

```text
T >= n - v(A) + z(A).
```

Nothing is assumed about the extra wires' inputs or outputs, or about the
other three blocks of `M`.

**Proof.** This is the counting argument of Bu, Fan and Joo (arXiv:2408.07898,
Lemma 3.6 and Theorem 5.2), as written out for 32 wires in JoyboyBrian's
[PR6105](https://github.com/CrocSwap/integer-mult-bounds/pull/6105), run on
all `N` wires and then restricted to the data block. Let `P_t` be the partition
of the `N` wires into components of the graph of the first `t` gates.

1. *Support invariant.* `M_t[i][j] = 1` implies `i, j` lie in one block of
   `P_t`. This holds at `t = 0`. A gate `d <- d + s` changes only row `d`, to a
   row supported in the blocks of `d` and `s`, which the gate merges.
2. *Potential.* Put `Φ_t = N - |P_t| + z_N(M_t)`, where `z_N` counts zero
   diagonal entries over all `N` wires, so `Φ_0 = 0`. If a gate joins two
   blocks, `|P|` drops by one and `M_t[s][d] = 0` by step 1, so no diagonal
   entry changes. Otherwise `|P|` is unchanged and only entry `d` can change.
   Either way `Φ` grows by at most one per gate, so `Φ_T <= T`.
3. *Restriction.* The data block of `M` is `A`, so `z_N(M) >= z(A)`. If
   `A_ij = 1`, then `i, j` share a block of `P_T` by step 1. Each block of `P_T`
   that meets the data wires is therefore a union of support components of
   `A`, so at most `v(A)` blocks meet them. The other blocks lie among the `k`
   extra wires. Hence `|P_T| <= v(A) + k` and
   `T >= Φ_T >= n + k - v(A) - k + z(A) = n - v(A) + z(A)`. ∎

## Consequence for the G20 boundary

The consumer reads the 32 labelled wires, so a word that implements one side
must have that side as its data block, with the data block's inputs on the
same 32 labels. For a legal basis `S` in PR6641's commutant `GL(2, F2)^16`,
the side is `S^{-1} L` or `R S`. PR6641 proves that the minimum of
`n - v + z` over that commutant is 38 on each side. By the lemma, every
extended word for every legal side therefore costs at least 38. A scratch
tariff is added on top, and the published scratch-free words reach 38, so no
nonnegative tariff helps.

The same lemma settles the scalar part of the two-helper question in
[PR5898](https://github.com/CrocSwap/integer-mult-bounds/pull/5898): any bank
exchange `(a, b) -> (A b, B a)` has `z = 4` and `v <= 2`, so it costs at least
six ADDs with any number of helpers.

## Evidence

`verify.py` uses only the standard library and writes nothing:

- **Pinned boundary.** Both programs replay to the stored rows of the
  SHA256-pinned controller, each expands to 38 ADDs and each side has
  `n - v + z = 38`.
- **Eight extended-wire controls.** On a 33rd wire, per side: a clean scratch
  that copies data and is cleared from final rows (47 left, 41 right), a garbage
  scratch (39), a clean relay that carries wire 31 through the whole word (42)
  and a dirty live wire that carries wire 31 and is restored exactly (44). Each
  realizes the same data block, respects the floor and costs more than 38.
- **Potential trace.** On 400 seeded random words with one to three extra
  wires, every step checks the support invariant, the unchanged diagonal at
  joins and `Φ_t <= t`. 47 words meet the floor with equality.
- **Complete width four.** Breadth-first search gives exact distances for all
  20,160 elements of GL(4, F2). All 302,400 (state, data subset) pairs respect
  the floor. As a statistic, 140 of the 480 reachable data blocks of width one
  to three meet it at their least distance.

The finite checks test the lemma's arithmetic. The proof above is the claim.

## Reproduce

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/g20-extended-wire-boundary-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/g20-extended-wire-boundary-floor
```

Expected output:

```text
PASS_G20_EXTENDED_WIRE_FLOOR side=38 port=76 witness=38/38 controls=8 control_lengths=[39, 41, 42, 44, 47] random_words=400 random_tight=47 gl4_states=20160 gl4_checks=302400 gl4_blocks=480 gl4_attained=140 no_new_kappa
```

Use another CPython 3.12 path on another machine. The run takes under a second.

## Limits

This is a scoped proof for unit two-wire XOR words, plus SWAPs at three ADDs.
It is not a multiplication theorem or a supplier admission. Selected
conditional κ and its five framework assumptions are unchanged. Not covered:

- outputs that end on different physical wires, with the consumer relabelled;
- nonlinear gates, multi-target XORs at unit cost and non-unit tariffs;
- a changed controller, target diagonal or basis outside PR6641's commutant;
- native, ownership, compiler, precision and caller obligations.

The commutant minimum of 38 is PR6641's result, cited at its head and not
replayed here. No Lean, Docker, native or selected-frontier replay was run.

## Open next questions

1. Can a side that leaves its data on other physical wires, with the consumer's
   relabelling charged, beat 76 ADDs per port? The first step is to price the
   relabel and compute `n - v + z` for the row-permuted data block.
2. Does a priced multi-target or nonlinear gate lower either side? The
   potential count above uses two-wire XOR gates only. Test one priced
   multi-target XOR on the four-wire exchange corner first.

## Credit

unpaidmoon posed the question and proved the commutant floor (PR6641).
JoyboyBrian proved the fixed-boundary 38-ADD floor and wrote out the counting
proof extended here (PR6105). Alan Bu, Evan Fan and Robert Joo own the
`n - v + z` bound. Ali Romman supplied the PR5840 controller, retained by
Charan . in PR5851. Nick Petalas's PR5898 posed the two-helper question.
