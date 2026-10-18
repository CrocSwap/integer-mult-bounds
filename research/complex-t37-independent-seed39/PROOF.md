# T37 whole-owner packing with a paid complex prefix allowance

This construction combines Chafik Boukhalfa's PR890 T21 owners with the
PR870 version of Hao Yan's T16 owners. It retains the U8 local word and
DreamingOfClouds' PR589 bit supplier. The new mechanism is a literal
whole-role exchange across the two owner schedules, with a larger complex
prefix allowance charged in full. The claimed conditional saving is
`1661960547713947/10^18 = 0.001661960547713947`; admission requires every
stage of `verify.py`, not this note or a proposed profile alone.

## Source and search scope

Implementation base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
PR890 source: `61b71bcf5a34db70220da81fa978d5b0c7bbb008`.
PR870 source: `b734850dc348800942f0ffd1f0723fdec7539b2b`.
The original sprint assignment used OS-generated seed 39, complex supplier
track, at base `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.

This changes a hypothesis of PR890's fixed-family bound: its complex
payload512 implies T<=22, whereas the present construction pays payload1024.
It does not contradict that bound. The local word, helper widths, capacity
types, dimension73 and nine-stage data recipe remain the inherited ones.
The deterministic search scanned shifts in [-1000,1000] in ascending order.
It completed 473 shifts through -528, the first to pass the fixed-bin window
screen, then checked all 5626 frozen width4 roles in full capacity48 bins.
Of these, 211 were viable replacements; the first in source order was used.
The remaining shifts [-527,1000] were not searched. See `data/SEARCH-TRACE.json`. No optimality claim is made for this search.

## Explicit owners and order

Relabel T16 replicas by adding21. Merge source call number i of T21 with
key16i and source call number j of T16 with key21j-528, breaking ties in
favor of T21. Both original call orders are subsequences. The actual
per-replica source-event projection remains the complete sequence of30
events, including bridges; merely preserving a stage label is insufficient.

The disjoint union initially leaves remainders
`{48:11085,44:1,3:1,2:1,1:5}`. Ten literal changed owner records, including
six relocations and four offset changes, are listed in `data/EDITS.json`.
The exchange changes `(44,3,2)` to `(48,1)`:

- Remove the sole width4 helper from bin(29,8,0), leaving its full rank48.
- Put it in the width4 slice of full bin(20,8,39), displacing a later width4.
- Repack capacity32 bin(20,14,111) as width8 plus six width4 helpers.
- Repack capacity32 bin(27,15,0) as three width9 plus one width4 helper.

The displaced later width4 enters the latter bin. Its three former width4
helpers go to the former capacity32 bin, whose width9 helper goes back.
This yields idle profile `{48:11086,1:6}`. Every helper remains whole, and
the actual windows, capacity prefixes, per-call family uniqueness, active
data exclusion and orthogonal73-axis charts are independently rechecked.
Restoration and phase obligations remain covered by the full controller
replay and unchanged local supplier checks.

There are333 invocations and167832 hosted helper roles. Their common local
profile is `{1:2548,2:338,3:446,4:162,5:72,8:8}`. The final paid profile is
`{1:848490,2:112554,3:148518,4:53946,5:23976,8:2664,48:11086}`.
Its mass is 2408256 = 73*33152-11840. Physical stock is 33152+514=33666.
The inherited native moment obligation is
`M37(b) = (1/33152) sum_r H37(r)*(r/73)^(1-b) < 1`.
The separately checked conservative version adds
`32*73^(1+b)*sum_r H37(r)/(10^16*33152)`. All entries of H37 are
recounted from complete invocations and the literal residual complements.
The finite nonrecursive work is charged by the emitted invoice below; its
constants do not enter as an unpaid change to this moment inequality.

## Independent comparison with T21

Write H37 and H21 for the two paid rank histograms. Multiplying by21 and37
respectively cancels all6993 local calls. The difference is exactly
`21 H37 -37 H21 =2[48]+15[1]-37[3]`. The37-coordinate vector
`(48,48,1,...,1,0,...,0)` with fifteen1s and twenty0s strictly majorizes
the vector of thirty-seven3s. Every proper prefix sum is larger and both
total111. Strict concavity of x^(1-b), for0<b<1, therefore gives a strictly
lower normalized native moment for T37. The child count also falls by20
in this common-denominator comparison, so the inherited positive per-child
conservative surcharge improves as well. `price.py` checks the exact
integer comparison and independently evaluates both moment engines.

The certified complex lower endpoint is
`416181814685169713943/250000000000000000000000`.
The unchanged bit lower endpoint is
`1733427039589844234749/10^24`. Both exact moment engines and all47 outer
inequalities are mandatory. The gain over PR890's constructed candidate is
`2773066918/10^18`, approximately0.000167% of that exponent saving.
This is a small increase, not a substantial advance toward kappa>0.01.

## Complete finite charge

The auxiliary bank envelope has groups(8,8,8,8,5), with22680 dedicated bank
families and33152 data families: live55832, physical56346. Every original
route, residual lane and exact complement is checked. All dedicated banks
and their padding children (including auxiliary rank53) disappear from the final hosted controller;
the envelope supplies a conservative invoice, not extra selected children.

Global prefix cost is113+2*333=779, strictly below the explicitly charged
complex payload1024. The stock has2643 bits, and the retained row formula is
`2*2643+9909+252+2*1024=17495<20161`. The old retained invoice truthfully
records512; it is pinned to512 and checked to be at most the new allowance.
The entire freshly computed per-vertex invoice is added to its overcharge.
No old invoice is relabeled as a1024-bit calculation.

The bit coefficient allowance and its bootstrap expression4+512 remain
unchanged: these refer to the bit invoice, not the complex global prefix.
Local allowance192, compiler multiplier16, factors144 per wrapper, and all
finite router, literal, logical and precision caps stay unchanged. Literal
source adaptations and multiplicities are exposed in `data/ADAPTER-EDITS.json`.
The fresh emitted invoice, with every invocation, wrapper, bridge, frame
change, restoration and source-access operation, must pass the retained
strict checks. Direct controls reject stale payload and row charges.

## Scope

This is a finite conditional construction, not a formal proof of the full
multiplication theorem. Inherited all-size compilation, common-label and
mutable-source realization, whole-call hosting, precision/tape, analytic
transfer and bit H1-H5 assumptions remain. No selected-frontier file or
`upstream/` source is changed. See `NOTICE.md` for attribution and AI disclosure.
