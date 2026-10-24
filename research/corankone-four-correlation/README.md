# Four binary full-guard events are strictly below independent marginals

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: **scoped counting proof with an exact finite component**.
For four pairwise orthogonal rank-one idempotents U_t on F_2^m, put
P_t=I-U_t. Under one uniform complete GL_m(F_2) header, let E_t mean that
all leading-minor guards through rank m-1 pass. For every m>=4,

```text
Pr(E_1 intersect E_2 intersect E_3 intersect E_4)
    < [3^(m-1)/((2^m-1)2^(m-1))]^4.
```

If rho_m is the joint fraction divided by that product, then

```text
1-rho_m = 12(7/9)^(m-1) + O((19/27)^(m-1)).
```

This answers k=4 of Open next question 2 in
[#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275).
That predecessor proves k<=3 and supplies the character law and k=4
spectrum. The new result proves the four-event product inequality and its
leading deficit. It is original successor work, with the predecessor laws
cited as steps. No new kappa or selected-frontier change is claimed.

[PROOF.md](PROOF.md) combines a uniform spectral tail bound for m>=85 with
81 exact rational comparisons covering 4<=m<=84. The first positive joint
fraction is 1/208320 at m=5; its marginal is 81/496.

## Reproduction and evidence

From the repository root, replace this local path with another CPython
3.12 interpreter if needed:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corankone-four-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/corankone-four-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-four-correlation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-four-correlation --check-source-history
```

The scientific marker is `PASS_CORANKONE_FOUR_CORRELATION`. The generated
stdout JSON enumerates all 81 finite comparisons and both character
multiplicities, and binds all six package files by SHA256. No receipt is
handwritten or stored. The verifier writes no files and uses only Python's
standard library. There are no live external inputs or imported predecessor
code. Historical provenance is pinned in SOURCES.json.

The executable finite component checks:

- All 4096 characters, with all 81 ternary assignments per character, agree
  with the Hadamard transform of independently generated factor weights.
- A direct integer convolution agrees with the spectral count at every
  n=0..12, without using diagonalization.
- All 81 finite product inequalities and the exact constants for the
  uniform proof pass. The asymptotic coefficient 12 follows analytically.
- Five controls detect independence, a missing finite-GL correction, a
  wrong zero-factor eigenvalue, its changed positive count, and a missing
  leading negative mode.

The loops have fixed finite bounds. The largest state vector has 4096
integers and walk depth is at most twelve. No function exceeds sixty lines
and no recursion or dynamic code execution is used. CPython allocates
integers and containers dynamically; fixed character, dimension and walk
bounds constrain this managed-runtime deviation from fixed allocation.
Warnings are errors in both registered modes. Independent human and formal
proof-kernel review are unclaimed.

Local CPython 3.12.15 on macOS arm64 passes both registered commands.
Direct normal and optimized checks each took 0.12 seconds, below their
120-second registered limits; these are check durations. Ruff 0.14.0
E/F/B/UP and the AST syntax/function-size inspection also pass.

## Limitations

Only four fixed orthogonal kernel lines over F_2 and uniform complete
headers are covered. This is a four-event product inequality, without an
assertion of general negative association. k>=5 and odd fields remain
open. Binary arithmetic is outside the retained odd-prime normalizer's
executable domain. No producer, header selection/emission, dispatch, dirty
return, stock, precision or fully charged physical caller is supplied.
Unknown costs are not zero. Selected cold replay, Lean, Docker and a full
multiplication theorem were not run or claimed.

The card's baseline binding check reached the selected source validation,
which passes at kappa 23/10000, but its old arithmetic summary raises
`KeyError: 'bit_lower'` on the selected productive-helper certificate.
This unrelated orientation incompatibility is not changed here. The
registered scientific checks are self-contained.

## Related work and credit

- Nick Petalas's [#4275](https://github.com/CrocSwap/integer-mult-bounds/pull/4275)
  supplies the all-k character law, its k=4 signed spectrum and the k<=3
  product inequalities. The new theorem settles k=4 for every dimension.
- Nick Petalas's [#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227)
  supplies the single corank-one marginal used in the comparison.
- The concurrent minimal-dimension rectangle question from #4275 is
  separate from this dependence question. No classification is claimed.
- Cinna Davis supplies the #4100 BIT request context. Source527,
  commdata2338 and Jose Manuel retain normalizer and recursive-closure
  credit. No predecessor credit or frozen package is changed.

Live PRs, recent handoff claims, local reservations, main README searches
and merged-title/body searches were consulted. They are partial overlap
coverage, without a novelty guarantee. TASK.json records the explicit
scope change from the audit card to original counting work.

## Open next questions

1. Does the product inequality hold for every k>=5? The next useful step
   is a structural bound on the nontrivial character eigenvalues and
   their signed multiplicities. A larger table alone is not a uniform
   proof. This package only settles k=4.
2. Can an actual producer use a fully charged shared-header caller?
   Start by pinning its kernel lines and header domain, then price
   selection, emission, dispatch, dirty restoration and stock. No such
   producer or complete invoice is supplied here.
