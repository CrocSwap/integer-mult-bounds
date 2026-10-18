# QQ16 recovery from sixteen retained selected arrays

**Sharp linear-information result for a changed immediate-cut interface.**
At the actual consecutive F0/B1 cut, retain only the 16 selected X arrays from
complete F0. Grant the current 96 ordinary X arrays, 96 ordinary Y arrays and
16 selected pair sums after complete B1. These observations recover all 224
original pair-0 arrays, with the actual routed operators. Any retained linear
record for this fixed current-observation interface needs rank at least 16N,
where N is the owner/payload array dimension. The displayed 16 arrays attain it.

Relative to PR2480's sharp 24-array L2 record, this exchanges eight fewer early
retained arrays for eight more current observation outputs and a paid local
preparation. It **replaces** eight current selected Y outputs with sixteen
selected pair sums; the read sets are not nested. The changed decoder needs neither the 88
ordinary F0 reads, unread minor inverse, future-A logger nor B2 C query in
PR2443. Existing L2 and forward inverse identities retain their attribution;
the new result is the complete changed observation contract, its ordered
reconstruction, matching rank floor and local physical sum-read handoff.

**The restriction matters.** The 208 current observation outputs use 224 current
physical fields, since each sum reads two selected fields. Individual selected
values and macro intermediate values are not exposed by this interface. If
current selected X values are also returned, the full post-B1 state is available
and zero early retention suffices. This is not an unrestricted memory minimum,
not a final-only decoder, and not a completed supplier or new kappa.

[PROOF.md](PROOF.md) gives the exact contract and both operator inverse orders.
The current fields are traced from the actual source F0/B1 equations before the
next bridge. Their selected sums have unequal physical input types. An explicit
local read normalizes each selected Y by C_q, adds X+Y into an owned output,
then restores Y with C_q^-1. Its complete finite invoice is 80 events: 32
rank-one children, 64 monomial wrappers, 32 ADDs, 16 CLEARs and 16 additional
owned outputs. No cover maps are needed. The scalar primitive allowance is288;
child/wrapper/storage costs and the rest of the decoder remain unpriced.

## Exact comparison with concurrent work

| Contract | Early retained arrays | Current outputs | Current physical fields |
| --- | ---: | ---: | ---: |
| PR2470 L2 sufficient record | 32 | 200 | 200 |
| PR2480 sharp L2 record | 24 | 200 | 200 |
| This selected-sum contract | 16 | 208 | 224 |

The first two grant `X2_U,Y2_U,Y2_A`; this contract grants
`X2_U,Y2_U,(X2+Y2)_V`. Thus the eight extra observation outputs require 24
additional physical fields, not eight cheap extra scalar reads. The local
sum macro also needs sixteen owned output arrays; its storage may outweigh
the eight-array early-retention reduction. No net storage, native-work or
supplier improvement is established, and this is not a stronger bound for
PR2480's fixed interface.

PR2492 already realizes the shared `x1_U` reconstruction with 400 H1 + 96 H8,
208 cover maps, 992 native wrappers and 6,624 scalar primitives, using 96 owned
outputs and one local scratch and restoring all 200 sources. It also supplies
the same normalization/sum/restoration method on ordinary ports. That method
retains credit; our selected-port use is not a newly invented native primitive.
The new boundary is the complete compressed selected observation contract and
its matching full routed recovery/kernel, with its additional read obligation
made executable. PR2492 supplies neither that contract nor the remaining full
decoder. Both exact predecessor README snapshots are pinned in SOURCES.json.

This contract could help a caller for which keeping early Y through B1 is
expensive and selected current fields can be consumed locally. A downstream
result must schedule the sixteen sum outputs with PR2492's old-frame outputs,
complete the remaining reconstruction and cleanup, then compare total storage
and cost. Their partial invoices cannot be added into a full supplier claim.

## Evidence and reproduction

From repository root, Python3.12 standard library:

```sh
python3.12 scripts/research_package.py --package research/qq16-sixteen-record-cut
```

Direct read-only commands:

```sh
python3.12 -I -O -B research/qq16-sixteen-record-cut/verify.py
python3.12 -I -O -B research/qq16-sixteen-record-cut/independent.py
```

The routed audit reuses PR2456's unchanged source parser and operator algebra,
with credit; it is not a second independent implementation of that machinery.
The new composition checks both inverse orders on224 independent formal arrays,
parametrizes the full16-array live kernel, and exhibits an invisible nonzero
input for each omitted early coordinate. Five changed decoders fail, including
a physical/logical route substitution invisible on payload-constant data.
The local sum word checks16,384 exact signed Gaussian kernel columns and five
semantic faults, including missing normalization, source restoration and output
clear. [RESULT.json](RESULT.json) retains all proof-relevant receipts.

The separate checker imports neither the routed checker nor predecessor code.
On the constant-owner/payload subspace it proves exact ranks208/224/223 using
two prime moduli and row-count upper bounds. It accepts alternative early Y
records and the extra-current-X escape, and rejects redundant early sum records.
This finite corroboration is explicitly separate from the universal operator
isomorphism and rank proof.

Default verification compares the complete receipt without writing it.
`verify.py --write-result` creates a new receipt and refuses overwrite. Sources
are authenticated before execution. [SOURCES.json](SOURCES.json) pins main-tree
inputs and unchanged predecessor snapshots. Export the package with its declared
main-tree inputs to replay without Git; no network is required by either checker.

## Open next questions

1. Can this changed observation interface be realized at a favorable complete
   cost before the next bridge? First compose PR2492's old-frame `x1_U` outputs
   with these current-frame selected sums, specifying output lifetimes and
   early-X capture/retirement. Then price the remaining reconstruction, chart
   conversions and cleanup. The local sum macro alone does not answer that budget.
2. Is retaining early data preferable to granting individual current selected
   reads and inverting B1 directly? First compare the complete two callers with
   matching restoration and output contracts. The rank16 lower bound does not
   apply to that expanded read interface.

## Credit

PR2470/thakrarsagar supplies the retention census and L2 lead; PR2443/starship-s
supplies the two-cut decoder and F0 inverse; PR2456/ywz65 supplies the retained
operator audit; PR2468/ywz65 supplies signed native-read conventions;
PR2480/Ross Richardson supplies the sharp 24-array fixed-L2 result;
PR2492/ywz65 supplies the paid ordinary L2 reconstruction and sum-read method. Ali Romman
and the retained QQ16/selected-supplier lineage supply the local equations,
physical frames and routed source packet. See [NOTICE.md](NOTICE.md).
New work is by ywz65 with substantial OpenAI Codex assistance, Apache-2.0.
No independent human review or proof-assistant verification is claimed.
