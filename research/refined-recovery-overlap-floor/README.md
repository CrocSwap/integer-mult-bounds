# An overlap floor for refined recovery at depth t ≥ 27

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

**Scoped proof with exact finite corroboration; no κ.** This addresses open
question 1 of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)
(`research/refined-recovery-longer-chains`, head `b6de532e`). PR6660 proves that the
optimal worst-case fiber of refined chains over mode-preserving frames is exactly
F^t for t ≤ 26 and *strictly* larger for t ≥ 27. It suggests minimizing its
zero-fiber kernel formula over overlap patterns at t = 27. This package gives a
floor for **every** overlap pattern and every t ≥ 27:

    |fiber(0)| ≥ F^t · (1 + (2^d − 1) · μ_d^(t/(2^d−1))),   1 ≤ d ≤ 4t − 104,
    μ_d = ρ₂^(2^d − 2^(d−3)) (d ≥ 3),   ρ₂ = 50979600/51008161.

| depth t | floor / F^t | tag bits ≥ | ⌈t log₂F⌉ (direct sum) | identity frame ⌈log₂A_t⌉ |
|---:|---:|---:|---:|---:|
| 27 | 15.78976 | **696** | 692 | 796 |
| 28 | 252.51 | 725 | 717 | 825 |
| 30 | 252.26 | 777 | 769 | 885 |
| 40 | 251.03 | 1033 | 1025 | 1181 |

So the strict inequality of PR6660 is in fact a gap of about four bits at t = 27
and eight bits from t = 28 on. The optimum lies between this floor and the
identity-frame value A_t.

**Argument.**
1. PR6660's zero-fiber formula, grouped by cosets of C, becomes a sum over a
   binary dependency space D of dimension at least 4t − 104. The summand is a
   product of coset ratios ρ ∈ {1, ρ₁, ρ₂}.
2. Restrict to any d-dimensional subspace of D and apply AM–GM over its nonzero
   points.
3. The per-stage minimum μ_d is attained by rank-3 stage maps onto the
   even-coset plane E, not by injective ones, because ρ₂⁷ < ρ₁⁸ (ratio
   1 − 1.2·10⁻⁷).

At t = 27 an abstract pattern of 27 such maps reaches 1 + 12ρ₂^25 + 3ρ₂^26, which is
within 10⁻⁴ of the floor. The bound is therefore essentially sharp for
four-dimensional dependency spaces. Whether actual frames realize that pattern is
open. See [PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/refined-recovery-overlap-floor/verify.py
python3.12 -I -O -W error -B research/refined-recovery-overlap-floor/verify.py
python3.12 -B scripts/research_package.py --package research/refined-recovery-overlap-floor
```

Each run prints `PASS_REFINED_RECOVERY_OVERLAP_FLOOR` in under a second. It
derives C from the pinned matrix and checks every number stated above in exact
rational arithmetic, including all 67 subspaces of F2^8/C for μ_d (d ≤ 8). It
recomputes RESULT.json and runs two failure controls.

## Limitations

PR6660's zero-fiber formula and 104-dimensional cap are cited premises at its
pinned head, which is open and unmerged. This package does not replay them. The
result is a lower bound; the exact maximum fiber at t ≥ 27 remains open. It
supplies no codec, physical tag, caller or restoration cost. κ, the selected
frontier and its five assumptions are unchanged. No independent human or proof-kernel
review is claimed.

## Open next questions

1. **Realizable minimum and max fiber at t = 27.** Can frames in G realize a
   dependency space whose stage maps are rank-3 maps onto E? If the first 26
   stages form a direct sum, the 27th map is forced to be injective. Is the
   maximum fiber equal to the zero fiber there?
2. **Upper side.** Beat the identity-frame bound A_t with one four-dimensional
   overlap, by extending PR6660's stage-by-stage box lemma to one coupled pair
   of stages. The present window is about 100 bits.

## Credit

Nick Petalas's PR6660 supplies the depth law, the zero-fiber formula, the
dimension cap and the open question. CubeJerry's PR6327 supplies the chain model,
F and A_t. zxv's #5444 supplies M. AM–GM and the coset structure of the extended
Hamming code are classical.
