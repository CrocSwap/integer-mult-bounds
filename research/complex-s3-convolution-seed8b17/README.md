# A rank-nine nonabelian convolution block: exact formula, conditional ceiling screen

**Local bilinear construction and optimistic profile screen. No provider mapping, supplier, or new κ is claimed.**

This package constructs an exact rational bilinear formula for multiplication in the six-dimensional group algebra `Q[S3]`. The mechanism is different from the nearby cyclic C3 convolution construction: `Q[S3]` is noncommutative and decomposes as

`Q[S3] ≅ Q × Q × M2(Q)`.

The first two factors cost one scalar product each. The matrix factor is multiplied by Strassen's seven-product 2×2 formula. Thus the 36 pair products in the regular convolution are represented by nine bilinear products. This package makes no claim that nine is the minimum rank, and it does not place the block in the selected gauge44 word.

## Exact map and reversible outputs

Index S3 by the six permutations in `RESULT.json`. For two coefficient vectors `x=(x_g)` and `y=(y_h)`, the regular product is

`c_k = sum_{g h = k} x_g y_h`.

Use the trivial, sign, and two-dimensional standard representations. The standard representation acts on the sum-zero subspace of `Q^3`, in basis `e0-e1, e1-e2`. Its rational Fourier coordinates are

`α(x)=sum_g x_g`, `β(x)=sum_g sign(g)x_g`, and `M(x)=sum_g x_g ρ(g)`.

Compute `α(x)α(y)`, `β(x)β(y)`, and the seven Strassen products for `M(x)M(y)`. Recover each output coordinate by

`c_g = (α(x)α(y) + sign(g)β(x)β(y) + 2 Tr(ρ(g^{-1}) M(x)M(y)))/6`.

`RESULT.json` gives all nine left forms, right forms, and six-coordinate output vectors. Their exact coefficients expose the rational denominator-six operation. For arbitrary dirty outputs `z`, the map is additive, `z -> z+c`; its inverse subtracts the same `c`, so the dirty state is restored. The verifier proves the bilinear identity on all 36 group-basis pairs, checks 256 deterministic integer and dirty-output fixtures, and rejects an omitted Strassen product.

## Conditional selected-profile budget

The pinned local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. If a compatible six-by-six S3 block exists, replacing its 36 rank-one products by one rank-nine child lowers the block's recursive rank mass by 27. The ceiling relaxation returns that mass to the idle pool and puts it at the favorable rank-51 cap. All unknown implementation charges are waived for this first screen.

| Hypothetical blocks | Candidate local profile | Ceiling for `a` | 5% screen |
|---:|---|---:|---|
| 7 | `{1:2160,2:418,3:432,4:142,5:82,8:8,9:7}` | `[0.001764054343894, 0.001764054343895]` | fails |
| 8 | `{1:2124,2:418,3:432,4:142,5:82,8:8,9:8}` | `[0.001775158769926, 0.001775158769927]` | passes conditionally |

The baseline upper endpoint is `0.001690054109089`; the required target is `0.00177455681454345`. The 8-block ceiling is about 5.036% above the baseline endpoint. At that target, eight blocks tolerate at most **one extra rank-one-equivalent child total**; two fail. This is a tight upper-bound budget, not an implementation allowance for each block.

The selected trace has 2,412 rank-one children per orientation, so its count-only capacity is 67 blocks. The package verifies this count from the source archive. It establishes **zero actual S3 support occurrences**: no mapping from the provider's child recipes to the six left, six right, and six output group coordinates has been found.

## Linear, copy, and implementation invoice

The algebraic transforms are explicit, so their size is visible:

- Each of the left and right form matrices has 39 nonzero entries across nine forms, with row supports `6,6,3,4,4,4,4,4,4`.
- Each input transform and the output transform has exact rational rank 6. At the abstract tensor boundary this adds no independent source or target dimensions beyond the six coordinates on each side; it does not supply the concrete frame and copy schedule in the selected provider.
- A literal no-sharing construction needs 30 signed additions/subtractions per input side and one doubling per side.
- The output map has 39 nonzero coefficients, with denominators at most 6. Multiplying each output equation by 6 gives an integer numerator schedule with 39 scatter terms, 33 additions after zero initialization, and six exact divisions by 6.
- Source/target access, frame changes, copies, scratch hosting, output fanout, precision, exact-division cost, interface transitions, and dirty-helper restoration are not charged by the ceiling screen. They are open parts of the provider invoice. Given the one-call total overhead headroom, a nontrivial implementation cost could erase the conditional gain.

No selected frontier or source certificate is changed. The selected record remains `certificates/selected-result.json`, resolved through its review, source manifest, and assembly certificate. The package pins those inputs, the selected replay archive, and the exact ceiling engine in `SOURCES.json`.

## Reproduce

From the repository root, using Python 3.12 and the standard library:

```sh
python3 -I -B research/complex-s3-convolution-seed8b17/verify.py
python3 scripts/research_package.py --package research/complex-s3-convolution-seed8b17 --check-only
```

Expected direct result:

```text
PASS_S3_GROUP_ALGEBRA_RANK9 basis_pairs=36 integer_dirty_fixtures=256 controls=1 rank1_capacity=2412 max_blocks=67 zero_overhead_threshold=8 local_only
```

To recreate the exact formula/cost certificate from the verifier, `RESULT.json` may be generated once with `python3 -I -B research/complex-s3-convolution-seed8b17/verify.py --write`; it refuses to overwrite an existing file.

## Open next questions

The entry overlap refresh covered 451 open PRs and 906 discussions. The exact terms `S3 group algebra`, `symmetric group convolution`, `nonabelian complex decoder`, and `six-dimensional group algebra` returned no matching PR or discussion. Nearby work includes the four-product rational C3 convolution claim (#2057), the Karatsuba block claim (#1987), rank-shape schedule work (#2003/#2052), and the fixed late-block results (#1429/#1517). The S3 algebra is nonabelian and its rank-nine construction factors through a matrix component; it is not a change of cyclic group size.

The claim and scope are recorded at [Discussion #1167, comment 18936773](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18936773). The next constructive step is to map eight actual source/target support blocks into both selected orientations and price their complete transforms and restoration. Until then this is an exact local mechanism with a conditional cost screen only.

Prepared by Cinna Davis (1337isnot1337) with substantial OpenAI Codex assistance. New package content is Apache-2.0; selected archives and prior certificates are unchanged.
