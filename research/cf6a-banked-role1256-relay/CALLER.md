# Signed caller, directed price and outer qualification

The role-1256 relay yields a conditional lower point of **κ ≥ 0.0037300417**.
Its signed raw crossing is in **(0.0037300417703, 0.0037300417704)**.
The reported lower exceeds the #7700 supplied-word upper 0.00372934317807
by exactly 0.00000069852193 and the #7697 qualified bank upper
0.0037266288770 by exactly 0.0000034128230. The price checker recomputes
both upper signs from the complete pinned bills. The comparison to #7700
uses the supplied raw signed invoice. Its original source describes a
finite word check, including its own raw-program rational conditions.
The new claim uses the bank, compiler and precision qualification here
with the five assumptions named below.
[Supplied #7700 archive](https://github.com/CrocSwap/integer-mult-bounds/pull/7700) ·
[Qualified #7697 archive](https://github.com/CrocSwap/integer-mult-bounds/pull/7697)

## Actual application

The supplied word is from head
`7d84799a447867d36137d12ef7ca5646154d763c`. The checked word digest is
`ae62d5d8bef6f7146454b4b3643e487a58380c606a16c5baef7bf0dcf9df1472`.
The folded parent and relay child digests are
`72705b094d83d2ba24006661bbb031786a691b776bedb94515b1321e1535105f` and
`8e7b755bd2d2d387bc3d3adfe48100985adf74775ca5acbb143170a3d16b5ccf`.
The 4,192-event caller has literal digest
`62d94fb992acab0a71c3d12f22be4ce63f4f65e5cbe3f420b93aa1393ffa8dcf`.
Both gzip transport and decoded data are authenticated.

The actual sixteen joint events use 96 type-A and eight type-B ports.
Each joint event injectively binds all 400 main positions, including the
96 second planes, to root owners. Two exact Gaussian group-ring replays
apply the signed coefficients in event order and recover every declared
diagonal return on all 68 logical root rows. The elementary steps
include the two A shears, the B butterfly, and the signed QUERY,
LAMBDA and IDLE terms. There are 153,295 exact pre-product divisions.
Replicated on the designated ports, those diagonals are 3,536 distinct
same-owner root returns.

The phase replay matches the actual port geometry of the supplied word
and the retained phase-basis table. All 12,800 absolute forward and
return translations exchange the relevant eight stage directions,
fix their head direction, and preserve the remaining spectators in
the 137-axis view. The 3,536 negative root head translations are
checked separately. A missing contact translation and an aliased joint
owner each fail their respective check. The direct relay's internal
frame phase and full operator are checked in the native and operator
proofs. [Caller checker](caller.py) · [Exact caller receipt](evidence/CALLER.json)

Both banks replay all 1,501 normalized native output rows on independent
basis inputs. The declared main rows are the signed normalized A and B
interfaces, and each helper returns on its own normalized row. Thus
the physical helper with input `x` at chart `E` returns
`T_G T_E⁻¹ x` at chart `G`, with independent input and same-owner
return in each stage. This includes the retained rank-four roles 325
and 1087 and the retained rank-nine public role 1256. There are 1,101
independent helper owners per call and 17,616 across the actual caller.

## Complete signed invoice

| Quantity | Folded #7700 | Role-1256 relay |
| --- | ---: | ---: |
| Positive paid native slots per call | 6,144 | 6,143 |
| Fixed QUERY and IDLE paid placements | 3,552 | 3,552 |
| Total paid placements | 101,856 | 101,840 |
| Native productive helper returns | 17,616 | 17,616 |
| Productive root returns | 3,536 | 3,536 |
| Total productive placements | 21,152 | 21,152 |
| Productive minus paid rank mass | 1,328 | 1,328 |

The exact raw MOVE labels 95828 and 104442 are consecutive transfers
on public role 1256 through charts 476, 878 and 127. The folded row at
104442 reads the former as its sole donor with coefficient one. The
direct chart-476-to-127 MOVE uses its old sender row. In the frozen
child schedule its stable label stays 104442 and its zero-based
execution ordinal moves from 4,114 to 3,310. All 7,643 other rows
preserve their relative order.

There are 32 fewer rank-three paid placements and 16 more rank-six
paid placements across all sixteen calls. Productive targets are
identical by owner and rank. The exact price improvement over the
supplied invoice at saving `s` is
`16(2·3^(1−s) − 6^(1−s))`. One additional paid rank-one placement
in the whole caller would reverse the directed gain at the #7700 raw
upper, so the full ordinary accounting and direct native phase check
are part of the qualification.
[Supplied invoice](data/SOURCE-INVOICE.json) ·
[Extracted #7697 signed invoice](data/PR7697-INVOICE.json) ·
[Directed price receipt](evidence/PRICE.json)

## Directed compiler and finite ordinary lift

Two directed arithmetic engines enclose each compared signed moment.
Their intervals intersect, and the monotonicity bounds cover the
interval through the retained BIT floor 0.00376669 from the
ambient-corrected selected 134-axis template. The recursive compiler
uses carrier power 1,920, paid cutoff 11, target floor 12, tail power
offset 1/7 and conservative ambient cap 153. At the test point
0.00373004170007 the price ratio is below 1 − 10⁻²⁷ and both tail
ratios are below 31/32. The input-lift bounds pass. The compiler
writes log power 2,289 and H = 14,571,800,000,000,000,000. All
54 strict and four functional outer predicates pass with exact minimum
margin 10⁻¹⁵. [Selected outer root and BIT proof](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

Both banks use native path grid 2,025·2²⁰ and signed caller scale
2,025 with binary height 9. The complete physical budgets use 9,151
and 9,150 numerical homes per native invocation, inside the inherited
15,290-home bound, with separately charged dummy, guide and four
full-width guarded streams. Each branch charges 55,104 exact odd
conversions. The child charges 280,512 ordinary map positions,
122,001,408 scalar services, 1,477,054 reset services per native call
and 402,978 typed transfer legs per native call. Full addressed
selector, overwrite, copy, exact scalar, guide, stage and complete
return work contributes to ordinary work `G`. The independent
physical receipt gives context bound `c = 1156` and checks that
`bit_length(c·1920·153^1920·(H+1)^2) = 14083 < H` with the
fresh directed compiler's `H`.
[Physical budget and width proof](PHYSICAL.md) ·
[Exact physical receipt](evidence/PHYSICAL.json)

At retained width `W = p+h+2D+3`, aggregate the simultaneous typed
owner tuples, parked contexts, children, and compiler and BIT backing
into stock `O`. For compiled productive width `W_p`, paid rank-one
mass `P`, and `N = 2^H`, the fixed finite-template substitution is
`Z = W_p+O`, `E_0 = 64(Z+N+P+G+1)^3`, `B_0 = P+E_0` and
`C_0 = 32NB_0²`. The positive outer inequalities admit these finite
template constants after increasing the eventual input cutoff. The
conditional interfaces are `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`.

## Replay and provenance

The caller replay reads its layout from the exact #7700 WORD. The
compact phase-basis table is retained byte-for-byte from #7697 head
`f55fc1434436ffa1c6d064a29fc56812044b3157`, SHA-256
`325a1eb4aa7fe5f918b1d8344b88ad132ef4606268bccec20f223ace5feda18b`.
The #7697 comparator invoice comes from `invoices.candidate` in that
head's caller receipt. The pinned engines preserve the #7682 caller
qualification, including the #7113 and #7669 caller lineage, the #7674
network, independent signed replay and fixed-grid interval arithmetic,
and the upstream phase checker. The selected numerical inputs are from
canonical head `e54523517d0f03e58352e647c403a5af3e525a57`.
[Retained #7697 source](https://github.com/Clear1nsight/integer-mult-bounds/tree/f55fc1434436ffa1c6d064a29fc56812044b3157/research/p104-banked-chart595-split)

From this package, run the following with Python 3.12 and fresh
output paths.

```sh
python3 -I -B caller.py --out /tmp/cf6a-CALLER.json
python3 -I -B physical.py --compiler-H 14571800000000000000 --out /tmp/cf6a-PHYSICAL.json
python3 -I -B price.py --caller-proof /tmp/cf6a-CALLER.json \
    --physical /tmp/cf6a-PHYSICAL.json --out /tmp/cf6a-PRICE.json
```
