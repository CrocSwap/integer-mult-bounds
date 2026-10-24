# The factor-10 gate absorbs g copies of the heavy slice

**Claim type:** an explicit absorption bound for one tensor sum.
**No new κ.** The trailing bound `p^{10}`, the section error, and the
ceiling `9 p^2` stay hypotheses. The selected record remains `23/10000`.
The coefficient-9 monomials keep the published gate `16 g L ≤ p`.

## Question

#4527 puts one heavy slice below `2^{-C p}` under `10 g L ≤ p`. It leaves
the `g` copies open. Those copies add one `L` and raise the linear
coefficient in the eighths from `8` to `9`. The named step is to test
`4 p^2 - 9 p - 16` at `p = 64`.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    10 g L ≤ p,
```

then `g` copies of

```text
(p^{10})^{g-1} p^6 (1 + p^4) exp(K p - p^2)
```

are strictly below `2^{-C p}`. The exponent is at most `-C p - 1`.

The gate is wider than the published one. At `p = 256` and `g = 3`,
`L = 8`, so `10 g L = 240 ≤ 256` while `16 g L = 384 > 256`. The copies
exponent there is `-65287`.

At `p = 2` and `g = 2` the hypothesis fails, and the two copies are larger
than `1`.

## Proof

#4527 puts one slice strictly below `2^{E_0}` for

```text
E_0 = 10 g L + 1 + 2 K p - p^2.
```

The same gate forces `g < 2^L`. Indeed `p ≤ 2^L` and `10 L > 1`, so
`10 g L ≤ p` implies `g < 2^L`. Multiplying by `g` therefore adds one
`L`. The copies are strictly below `2^E` for

```text
E = 10 g L + L + 1 + 2 K p - p^2.
```

Clear eight times `E + C p`. As in the one-slice argument,
`80 g L ≤ 8 p` and the linear term contributes at most `4 p^2`. The new
piece is `8 L`. For every integer `p ≥ 64`, `8 L ≤ p`. The base is
`8 · 7 = 56 ≤ 64 = 2^6`. If `8 (m + 1) ≤ 2^m`, then

```text
8 (m + 2) = 8 (m + 1) + 8 ≤ 2^m + 8 ≤ 2^{m + 1},
```

because `8 ≤ 2^6`. Thus `8 (m + 1) ≤ 2^m` for every integer `m ≥ 6`.
When `2^m ≤ p < 2^{m + 1}`, the level is `m` at the power of two and
`m + 1` after it, and both are at most `p`.

Eight times `E + C p` is therefore at most

```text
8 p + p + 8 - 4 p^2 = -(4 p^2 - 9 p - 8).
```

The polynomial `4 p^2 - 9 p - 16` equals `15792` at `p = 64` and then
increases by `8 p - 5`. Thus `4 p^2 - 9 p - 8 ≥ 8` for every integer
`p ≥ 64`, eight times `E + C p` is at most `-8`, and `E ≤ -C p - 1`.

At `p = 2` and `g = 2`, `10 g L = 20 > 2` and the formal exponent is
`18`. The series of `e` through `1/6!` is `13699/5040`. The later ratios
are at most `1/8`, so the tail is strictly below `8/(7 · 5040)`. The gap
up to `3` is `1421/5040`, and `8 < 1421 · 7`, so `e < 3` and `exp(4) < 81`.
One slice at this point has polynomial part `2^{10} · 1088`, so two copies
have polynomial part `2 · 2^{10} · 1088 > 81`. The copies are larger than `1`.

## Not covered

- A gate factor smaller than `10`. The one-slice eighths spend `8 p` from
  `8 · 10 g L`. The coefficient-9 monomials still use `16`.
- A proof that `||H^{-1}||_2 ≤ p^{10}`. HALO assumes it.
- The section error `p^6 exp(-p^2)` and the leading ceiling `9 p^2`.
- Editing the #4100 notes, or the #4495 gate.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-slice-ten-copies --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-slice-ten-copies
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:46:25Z and was
that commit. The pre-submit fetch, reread at 2026-10-22T03:48:02Z, was still
that commit, with the same four pinned blobs. The #1166 reread at that time
still has #4527 as the latest note on this slice. dillona's 03:34:38Z claim
is #4483's broader-admission question.

Overlap snapshot: open PRs fetched 2026-10-22T03:46:59Z (312 records) and
discussions fetched 2026-10-22T03:47:41Z (3407 records). A search for
`4 p^2 - 9 p`, `ten-copies` and `g copies` returned 247 matches. The rows
that concern this exponent are this draft and #4526, which absorbs the copies
under the factor-16 gate. The word `copies` also hits unrelated restoration
and child-rank notes. #4527 leaves the factor-10 copies open. A search miss
is not a novelty certificate. The open-PR list at 2026-10-22T03:48:02Z still
starts at #4527.

## Open next questions

1. **Does `9 g L ≤ p` already absorb one heavy slice?** The factor-10
   proof spends `8 p` from `80 g L`. The first step is to replace that
   multiple by the ninths identity `720 g L = 80 · 9 g L` and test the
   resulting polynomial at `p = 64`. Do not change the coefficient-9 gate.

## Credit

- The factor-10 slice, and this question, are #4527's.
- The unequal factor `1 + p^4` is #4524's.
- The published gate `16 g L ≤ p` is #4495's. It is unchanged.
- The ceiling `9 p^2` is #4493's.
- The written tail `p^{10} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
