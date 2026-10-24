# Edge allowance against p/6400

**Scoped comparison. No new κ.** The selected conditional exponent stays
60403/20000000. This does not accept PR #4100.

## Result

On the edge layout `p = 2^{24} - 2 = 16777214`, `ell = 24`, and 65,536
widths of 23, the constructor gives `L = 1507328 ≤ p`, `G = 3072`, and
`r_max = 4`. Here `p + 2 = 2^{24}`, so the envelope ratio is exactly

```text
R = 3 r_max = 12.
```

The printed product line uses the coefficient `p/6400`, with `C_E` left
as a common factor:

```text
r (2/B + β) E ≤ (C_E p / 6400) 2^{−60 ell} (p+2)^{−48}.
```

The comparison asked by PR #4925 is `12 · 6400` against `p`:

```text
12 · 6400 = 76800 < 16777214 = p.
```

So `12 < p/6400`. Division gives

```text
p = 218 · 76800 + 34814,
```

and therefore

```text
218 < (p/6400) / 12 < 219.
```

The additive gap is

```text
p/6400 − 12 = 2609 + 2814/6400.
```

`C_E` is not evaluated. No larger ratio is sought, and the 104,864-plan
schedule is not replayed.

## Scope

Card `formal-interface-lemma`, scope **refined**. This is the open
question of the production envelope ratio. One layout and one division
are checked. No census and no multiplication theorem are claimed.

Canonical main fetched 2026-10-23T00:13:18Z at
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B research/crt-reservoir-edge-allowance/verify.py
python3.12 -B scripts/research_package.py --package research/crt-reservoir-edge-allowance
```

The direct command prints `PASS_CRT_RESERVOIR_EDGE_ALLOWANCE`.

## Open next questions

None of the same kind. PR #4925 asked whether 12 is at most `p/6400` on
this edge. The comparison holds, and the quotient above is the result.
`C_E` remains the unevaluated common factor already excluded from that
question. Searching for a larger ratio was excluded by the predecessor.

## Credit

Hiroki KUMAZAKI, PR #4174, for the constructor. PR #4646 for the printed
product line. PR #4925 for the edge layout and the ratio 12. Cinna
Davis, PR #4100, for the CRT parameters.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance.
Apache-2.0. No independent human review and no formal-kernel acceptance
are claimed.
