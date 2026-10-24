# Uniform constant for accepted reservoir layouts

**Scoped comparison. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

The #4174 constructor accepts only integer `p ≥ 1` and
`ell ≥ max(2, ceil(log2(p+2)))`. For every such `p`,

```text
ceil(log2(p+2)) ≥ 2,
```

because `p+2 ≥ 3` and `(3-1).bit_length() = 2`. Thus `ell` and the
logarithm are each at least 2, and the guard

```text
G = 64 (ell + ceil(log2(p+2)))
```

satisfies `G ≥ 256`. The bound is achieved: `p = 1`, `ell = 2`, and
65,536 widths of 1 give `G = 256`, `L = 65536`, and `r_max = 2`.

PR #4646 factors the sharp window term as

```text
2/B + β = 2^{-G} (2 + 2^{1−62G} − 2^{2−63G}).
```

For every integer `G ≥ 256` the exponent `1−62G` is at most `−1`, so the
positive correction is at most `1/2`. The exact factor is therefore
strictly less than `5/2`, and in particular strictly less than 3. At
`r = r_max`,

```text
r (2/B + β) < 3 r_max 2^{-G} = (3 r_max / p) p 2^{-G}.
```

So `C = 3 r_max / p` is sufficient for every layout the constructor
accepts. The same majorant covers the published term `8B/2^K`, whose
correction `2^{3−62G}` is also at most `1/2` once `G ≥ 256`.

On the equality-case layout the constant is `3 · 2 / 1 = 6`. Both `C = 1`
and `C = 1/6400` fail there. The constructor rejects `ell = 1`, so the
weaker floor `G ≥ 192` from an `ell ≥ 1` domain is not a layout this
constructor emits.

If a layout also has `L ≤ p`, then

```text
r_max ≤ L/(100G) ≤ p/(100 · 256) = p/25600,
```

and `3 r_max / p ≤ 3/25600 < 1/6400`. The production plan
`r_max = 5`, `p = 9240576` satisfies `3 · 5 · 25600 ≤ p`. The constant
`1/6400` remains sufficient on every accepted layout that also has
`L ≤ p`.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the open
question of the single-layout constant. The argument uses the
constructor's inequalities and one equality witness. It does not
enumerate layouts, multiply by the `E` envelope, or rerun the
104,864-plan census. No multiplication theorem is claimed.

Canonical main fetched 2026-10-22T23:52:56Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-reservoir-uniform-constant/verify.py
python3.12 -B scripts/research_package.py --package research/crt-reservoir-uniform-constant
```

The direct command prints `PASS_CRT_RESERVOIR_UNIFORM_CONSTANT`.

## Open next questions

1. On the equality-case layout `p = 1`, `ell = 2`, `r_max = 2`,
   `G = 256`, what does `3 r_max 2^{-G}` times the printed `E` envelope
   become? The scalar comparison is settled, and `p/6400` is not the
   prefactor when `L > p`. First step: multiply `6 · 2^{-256}` by
   `2^{4 ell} (p+2)^{16}` and compare with
   `2^{-60 ell} (p+2)^{-48}`. Blocker: that product is not formed here.

## Credit

Hiroki KUMAZAKI, PR #4174, for the constructor and its guard formula.
PR #4646 for the factored window term and the constant `1/6400`.
PR #4921 for the constant 3 on the single layout `p = 2`. Cinna Davis,
PR #4100, for the CRT parameters.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
