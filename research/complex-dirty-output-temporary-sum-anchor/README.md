# Temporary-sum anchor for arbitrary dirty outputs

**Claim: this contribution does not improve the selected κ.** It proves an exact local construction and screens a hypothetical profile, but does not place the products in the selected supplier. This is a scoped result, not a claim that no future implementation can improve κ.

The selected value remains `κ = 0.001672660197076918`.

The prior two-output anchor uses two clean required output coordinates. The selected #1094 provider instead has arbitrary dirty target inputs: its exact forward endpoint preserves each target's own input column and adds its source column. This note removes the clean-target condition by temporarily forming the sum of both dirty anchors, compensating every other target once, and restoring the anchor before the products.

## Construction

Over any commutative ring, take independent rank-one products

```text
P = x0*y0,  Q = x1*y1,  Ri = xi*yi  (2 <= i < q)
```

and arbitrary initial target values `d0,...,d(q-1)`. The desired additive map is
`A0=d0+P`, `A1=d1+Q`, `Ai=di+P+Q+Ri`. The schedule is:

```text
A0 += A1                              # temporary dirty sum d0+d1
for i >= 2: Ai -= A0                 # cancel both dirty anchors in one shear
A0 -= A1                              # restore A0=d0
A0 += P; A1 += Q
A0 += A1                              # temporary sum d0+d1+P+Q
for i >= 2: Ai += A0                 # dirt cancels; each target gets P+Q
for i >= 2: Ai += Ri
A0 -= A1                              # restore A0=d0+P; A1=d1+Q
```

All source values stay unchanged. Each step is a reversible shear or a rank-one product shear, so reversing the schedule restores every arbitrary target and source. The output-slice matrix on `(P,Q,R2,...,R(q-1))` has rank `q`; the displayed `q` products therefore attain the tensor rank lower bound.

The schedule uses `q` recursive children and `2q` scalar additions. Independent accumulation uses `3q-4` rank-one children. At `q=112`, this replaces 332 children with 112, saving 220 child calls, while adding 224 scalar additions. The temporary dirty sum lets each other target pay one compensation shear rather than two. The schedule uses no clean target, scratch helper, copy or frame change. The extra additions are charged in the scalar compiler envelope separately; translating each one into a rank-one-equivalent fee would erase the recursive saving and is not the cost model used here.

## Exact reproduction and selected-source boundary check

From the repository root:

```sh
python3 -I -O -B research/complex-dirty-output-temporary-sum-anchor/verify.py
python3 scripts/research_package.py --package research/complex-dirty-output-temporary-sum-anchor --check-only
```

The verifier symbolically proves the forward map and inverse for all 110 widths `3<=q<=112`, checks output-slice rank, exhausts 37,376 assignments over `F2` for widths 3–5 and 551,124 assignments over `F3` for widths 3–4, and rejects five schedule mutations. It also replays the pinned selected scalar program and confirms that all 112 target coordinates retain independent arbitrary entry dirt. The exact source/interface replay is a prior result by ywz65 and Codex; this note uses its pinned interpreter and selected archive, with attribution retained.

Seven hypothetical blocks fit the selected local word's 2,412 rank-one children: `7*332=2324`, while `8*332=2656` does not. Replacing those seven groups gives the hypothetical profile
`{1:872, 2:418, 3:432, 4:142, 5:82, 8:8}`. The fixed-word exact ceiling is `a<=0.002374178346`, or conditional complex `κ<=0.002368554974`, versus selected `κ=0.001672660197076918`. This moves the ideal complex ceiling above the unchanged bit endpoint `0.001733427039589844234749`, so the bit supplier would become the limit if an admitted local construction produced a complex saving at that level. None of those seven source-compatible blocks has been identified yet.

The 1,568 additional unit-addition macros per call are separately screened against the selected scalar guard. Using the retained per-macro adapter growth and charging eight real primitives per complex unit addition, the conservative local bound is at most `10,688,681,187,742`, below the strict `2^48` guard `281,474,976,710,656`, with slack `270,786,295,522,914`. This is only the local scalar-envelope screen; it does not supply the product mapping or the complete supplier replay.

## What remains unproved

- **Bounded source-block attempt.** I inspected the pinned selected `FULL-WORD`, `CANONICAL-WORD`, `CLIFFORD-RECIPES` and `LOCAL-PROGRAMS` together. They expose 112 ports/root rows, 2,896 frame-transition recipes and the exact dirty scalar endpoint, but do not directly bind a common set of product operands to 112 destination rows at one chronological cut. The 112-by-8 root/scatter data is a different interface from the required dirty accumulator block. No `P,Q,P+Q+R_i` factorization or full invoice was extracted. This is a bounded representation mismatch, not evidence that no such factorization exists.
- A source-bound implementation must account for every child frame, source acquisition, scalar macro, full inverse, precision/tape effect, and outer caller/cleanup transfer.
- The seven-block profile is a relaxation of a changed local word, not the current selected profile. It does not prove the resulting complex moment or a whole-supplier kappa.

The prescribed stop point has been reached: do not search for seven copies until one source-bound block closes.

## Provenance and credit

Pinned to local checkout `d8e0f83f00191df62174b641e9fff055c357f641`. This extends the local two-output temporary-sum map in [complex-two-output-sum-anchor-seed65ce19](../complex-two-output-sum-anchor-seed65ce19/README.md), credited to Cinna / commdata2338, by changing its clean-output premise to arbitrary dirty additive targets and optimizing the compensation schedule. The selected dirty-target boundary is established in [centre-owner-observation-floor](../centre-owner-observation-floor/README.md), credited to ywz65 and prior source authors. The exact ceiling and scalar-guard tools retain their package credits. No external claim or PR was opened.

## Open next questions

1. Can one exact selected provider subword be expressed as the 112 forms `P,Q,P+Q+Ri` while retaining its source and frame chronology?
2. Does the full child/frame/caller/cleanup invoice for that one block fit with positive recursive-child savings?
3. If a block fits, can seven disjoint copies be assigned while preserving the selected supplier's arbitrary-dirt inverse and the complete bit/complex assembly?
