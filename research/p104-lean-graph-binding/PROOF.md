# Exact source binding for the packed banked recipe

This audit binds the packed recipe and native chart data in
[PR #7783](https://github.com/CrocSwap/integer-mult-bounds/pull/7783)
to the exact graph from
[PR #7761](https://github.com/CrocSwap/integer-mult-bounds/pull/7761).
It checks an external data correspondence that the formal package leaves
outside Lean. No new kappa, kernel build or complete application admission
is claimed. The selected frontier is unchanged.

## Exact objects

The formal source is commit
`47ef383d7de8b77bd198b104c84efb06191a89c2`. The graph source is commit
`d5219594c9b0e80c002a75e79b85766256496b07`.
The graph's canonical SHA-256 is
`c6387f5a887f3ef2e79782cf2d7d167aeae5e6cd1e92d577e4c6e610ed360f84`.
The source application names that same graph. SOURCE-PINS.json binds
51 retained files by SHA-256 and Git blob hash.

The retained graph builder reads the source BASE-GRAPH, BASE-INTERFACE
and EDITS files. It runs in a normal Python subprocess in both audit
modes. Its output must match the published graph hash. The audit does
not execute the original packing generators. It decodes the deposited
Lean literals directly.

## Bank and field correspondence

Filter the published schedule to its 5,746 paid banks. Map its kth bank
identifier to the formal index k. Keep each of the 1,262 field indices
unchanged. RESULT.json lists the complete bank map; its canonical digest
is `0af2dfee6385a5288996272158a4d02b5eec7b8b8d35dcf0436c35a50ad06995`.

The formal
[recipe definition](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/Bridge7761R4.lean)
uses three term domains:

| Family | Terms | Decoded tuple |
| --- | ---: | --- |
| F | 134,078 | input field, rational coefficient, receiving bank |
| R | 11,241 | earlier bank, rational coefficient, receiving bank |
| O | 43,106 | bank, rational coefficient, output field |

The checker reads each chunk list from the actual recipe definition.
It decodes all 381 packed recipe integers in that order. Each chunk
contains at most 1,500 terms. Field indices have eleven-bit slots;
bank indices have thirteen-bit slots. Coefficients have thirty-two-bit
slots. The coefficient decoder is exactly

```text
((slot mod 65536) - 32768) / floor(slot / 65536).
```

Every deposited denominator is positive. Each decoded coefficient and
index equals the corresponding source term, in order. No declaration
or term is omitted. The unused high bits of the final chunks are zero.
Every reference is to a strictly earlier bank. All field and bank
indices are within their declared bounds, so the formal `Fin` modulo
conversions leave them unchanged. There are no duplicate donors in a
row, and all source coefficients are nonzero.

As a second check, the decoder reconstructs all 7,008 source rows from
these tuples and the bank-index map. The complete graph has the exact
published hash above. Its rows have causal same-chart reads. Its paid
routes have strictly nested chart spans.

## Charts and owner endpoints

The nine other packed integers contain chart bases and pivots, owner
and bank endpoints, the output partner map and two output coefficients
per field. Together with the recipe, they contain 602,859 slots.

For each of the 1,099 charts, the checker decodes all nine basis and
pivot slots. It checks zero padding and the pivot equations. The decoded
basis generates exactly the same set of vectors as the source frame.
The comparison enumerates 68,745 chart-vector memberships, including
zero and repeated vectors in different charts. It also checks that the
decoded lists equal the literal `chBasis` and `chPiv` lists.

This is the formal chart interpretation: `chartOf` takes the span of
the listed bitmask vectors in the nine-dimensional space over F2.
[Chart definition](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/Bridge7761G2.lean)
and
[basis interpretation](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/Bridge7761Chart.lean)
give those meanings. Equal spans preserve the chart subspace even when
the displayed basis differs from the source basis.

Both endpoints of every public field and both endpoints of every bank
match the source chart identifiers. The partner map is an involution.
Thus this check binds the full native recipe, not only its dimensions
or a sample of bank coefficients.

## Linear-map implication and full output check

The formal
[bank recurrence](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/47ef383d7de8b77bd198b104c84efb06191a89c2/research/p104-banked-banner/lean/Nov15/BankTieD.lean)
adds the stated input-field forms and the stated earlier-bank forms.
Because each decoded reference is earlier, its non-earlier fallback is
never used. Induction on k proves that each formal bank form equals the
source bank form under the index map. The same term equality proves
the output-form equality.

The checker also expands the decoded graph independently over all
1,262 rational input directions. It compares every resulting output
coefficient with the diagonal and partner entries decoded from ODK,
OPK and PIK. This covers 1,592,644 matrix positions and performs
10,950,501 scalar coefficient products. These are verification counts,
not implementation costs. The canonical output-map digest is
`0734dc9676f2854d62cf934017d945c1b051d0f97894c75f342af6cd3cbf628c`.

The claim concerns the mathematical interpretation of the inspected
definitions and the exact deposited data. The checker is not a Lean
parser, elaborator or proof kernel.

## Controls and replay

Eleven controls change field or output coefficients, a receiving bank,
a referenced bank, an output field, a trailing chunk slot, chunk order,
a chart basis, a field endpoint, the output diagonal or the partner
index. Each is rejected by the data-correspondence check. The controls
operate after source authentication, so a source hash mismatch cannot
be their sole rejection reason. RESULT.json records each reason.

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-lean-graph-binding
```

Both modes print this prefix and elapsed seconds:

```text
PASS_P104_LEAN_GRAPH_BINDING 188425 terms 1099 charts 11 controls
```

## Limits and open next questions

The source graph builder is retained code from the formal package. The
rational coefficient expander is retained from
[PR #7777](https://github.com/CrocSwap/integer-mult-bounds/pull/7777). The packed
decoder and correspondence checks are new and source-aware. This is
computational corroboration, not independent human or kernel acceptance.

No Lean build, axiom audit, complete proof-closure check, physical word
replay, caller replay, interval price or compiler run is performed.
The auxiliary packed proof witnesses and chain certificates are not
independently reconstructed. The complete formal theorem and its
application still need their own review. In particular, the caller-list
origin, `Valid` and physical realizability remain outside this result.
All five inherited application assumptions remain.

The next separate question is whether the formal caller lists equal
the complete source SPEC invoice. Compare the literal lists with the
source caller and state the remaining hypotheses. A native graph match
does not establish that invoice correspondence.
