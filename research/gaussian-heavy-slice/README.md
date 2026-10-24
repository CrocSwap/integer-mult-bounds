# The heaviest trailing slice fits the same gate

**Claim type:** an explicit absorption bound for one tensor slice.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record remains `23/10000`.

## Question

#4524 absorbs the unequal errors with every ceiling at `9 p^2`, and asks
whether the same gate absorbs the heaviest slice when a trailing factor is
`p^{10}`. The named step is to clear

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(-p^2).
```

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then both

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

and its `g` copies are strictly below `2^{-C p}`. The case `K = 0` is the
slice in the question. Each exponent is at most `-C p - 1`.

This is the heavy end of the telescope. Since `p^8 ≥ 256 > 9`,
`p^{10} > 9 p^2` for every integer `p ≥ 2`. Replacing a trailing `p^{10}`
by a leading `9 p^2` makes the product smaller, so the slice with every
completed factor equal to `p^{10}` dominates. For `g = 1` there is no
trailing factor and the slice is the unequal sum from #4524.

The published gate is not optional. At `p = 2` and `g = 2`, `16 g L = 32 > 2`,
and the slice is already larger than `2^{10} > 1`.

## Proof

The power count is exact when the `1` in `1 + p^4` is dropped:

```text
(p^{10})^{g-1} p^6 p^4 = p^{10 g}.
```

Since `p^4 > 1` and `p ≤ 2^L`,

```text
1 + p^4 < 2 p^4 ≤ 2^{4 L + 1},
```

so the slice is strictly below `2 p^{10 g}`. With `p^{10 g} ≤ 2^{10 g L}`,

```text
(p^{10})^{g-1} p^6 (1 + p^4) < 2^{10 g L + 1}.
```

The usual comparisons `exp(-p^2) < 2^{-p^2}` and `exp(K p) ≤ 2^{2 K p}`
then put the slice strictly below `2^E` for

```text
E = 10 g L + 1 + 2 K p - p^2.
```

Clear eight times `E + C p`. The gate gives `80 g L = 5 · 16 g L ≤ 5 p`.
The constant `1` contributes `8`. The linear factor contributes at most
`4 p^2` once `p ≥ 4 K + 2 C`. The sum is at most

```text
-(4 p^2 - 5 p - 8).
```

The polynomial `4 p^2 - 5 p - 16` equals `16048` at `p = 64` and then
increases by `8 p - 1`. Thus `4 p^2 - 5 p - 8 ≥ 8` for every integer
`p ≥ 64`, eight times `E + C p` is at most `-8`, and `E ≤ -C p - 1`.

The gate and `L ≥ 1` also force `g < 2^L`, because `16 g L ≤ p ≤ 2^L` and
`16 L > 1`. Multiplying by `g` adds one `L` to the exponent. That extra
piece scales by `8 L ≤ p`, which holds for every integer `p ≥ 64`. The
polynomial becomes `4 p^2 - 6 p - 16`, equal to `15984` at `p = 64` and
increasing by `8 p - 2`. The `g` copies stay at most `-C p - 1` as well.

## Not covered

- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Whether the factor `16` in the gate can fall to `10` for this slice.
  The coefficient-9 monomials still use `16`.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-heavy-slice --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-heavy-slice
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:32:42Z and was
that commit. The pre-submit fetch in this round was still that commit, with
the same four pinned blobs. A #1166 reread at 2026-10-22T03:36:10Z still has
#4524 as the latest note on this slice. dillona's 03:34:38Z claim is #4483's
broader-admission question.

Overlap snapshot: open PRs fetched 2026-10-22T03:33:19Z (310 records) and
discussions fetched 2026-10-22T03:34:03Z (3403 records). A search for
`heaviest slice`, `(p^{10})^{g-1}` and `trailing factor` returned this draft
and the #4524 handoff, which leaves the trailing `p^{10}` slice open. A search
miss is not a novelty certificate. The open-PR list at 2026-10-22T03:36:10Z
still starts at #4524 and does not contain this slice.

## Open next questions

1. **Does `10 g L ≤ p` already absorb this slice?** The exponent spends
   `10 g L`, while the published gate allows `16 g L`. The first step is
   to replace `16` by `10` in the eighths and test `4 p^2 - 8 p - 16` at
   `p = 64`. Do not change the coefficient-9 gate.

## Credit

- The unequal factor `1 + p^4`, and this question, are #4524's.
- The gate `16 g L ≤ p` is #4495's.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` and the tensor shape
  `g p^{10 g} exp(-p^2)` are #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
