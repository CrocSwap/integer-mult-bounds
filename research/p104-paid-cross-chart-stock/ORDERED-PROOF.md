# Ordered-chart transport cut

We sharpen the [predecessor bound](PROOF.md) on #7161 scientific head
`e3f8d39c43b07063dfc5b800f71c5d21015259e6` and #7113 caller
`07a76c5e2738882c0cb322278e56f6cae3c9885d`. The comparable complete witness
is κ = 0.003644890067940 at live #7161 head
`7a607733a114689a60179898ab5ec9e30561daac`. The target is
`10018846261809/2500000000000000`. No new κ is certified.

## Rank proof

Fix an allowed positive column multiplicity and write V for one complete
payload space. Each of m selected transport lanes starts and ends in distinct
canonical spans of the same rank. Its independent arbitrary V-valued
payload must be returned to the designated destination. Restricted to these
payloads, the transfer is the identity I. Set the outgoing value at each of
the D descending paid MOVEs to zero, obtaining a transfer M₀. The difference
I−M₀ factors through at most D copies of V. Feed the D discrepancies at the
cut events into the downstream chronological network. All other gate laws
are the same and the error propagation is linear. Side information and
arbitrary coframed coding are allowed.

Choose a total order of canonical spans within each rank. Keep the lanes
whose source precedes their destination. Reversing each rank's order keeps
the complementary lanes. One choice therefore keeps at least m/2 lanes,
including repeated endpoint pairs and distinct owners. Restrict the input
and output to that same selection. With the descents zeroed, rank never
decreases along a path, so M₀ is block triangular in rank order. Within a
rank, a path stays in its canonical span. Order the equal-rank lanes by
source chart. A nonzero block from lane j to lane i requires the source
chart of j to equal the destination chart of i. This is later than the
source chart of i, so the equal-rank block of M₀ is strictly upper
triangular. Thus the restricted I−M₀ has full rank, at least (m/2) dim V.
Consequently m ≤ 2D. The old native word has D = 24 and m ≤ 48.

The factor two is attained in the abstract cut model. Ascend two equal-rank
charts' payloads x and y to a common upper chart, form x+y, descend once to a
common lower chart, and use two ascents to return the sum to both source
charts. Each subtracts its own side information to obtain the other payload.
This attainer concerns the abstract cut.

## Directed whole-construction price

Use the unchanged census of 6,279 MOVEs and the 128 exact coefficient
checks on 24 descending edges and 104 direct chart classes. All 73 pending
classes retain their ideal coframed capacity. The audit independently
derives 3,916 chronological distinct-span equal-rank endpoint pairs and
reconstructs all 110,519 paid positions and 22,427 productive targets of the
17-stage caller.

For each rank-nine price layer, count the union of owners available in any
pending direct chart, then add at most 48 of the remaining transportable
owners. This grants incompatible simultaneous choices and counts each owner
at most once in a layer. The four layer maxima are 154, 93, 52, and 48.
Give all 483 smaller owners their best allowed ideal split once. The
directed saving upper is
`592730639798561378905288647/5000000000000000000000000`. The exact directed
net upper is `-54927837478005033828434093/2500000000000000000000000`.
The ordered cut lowers the predecessor net upper from about −1.90184
to −21.97113.

The audit verifies the triangular pattern on all 64 loopless simple
three-chart digraphs in all six orders, plus parallel lanes and a
same-chart loop rejection. The written argument supplies the general
claim. Changed scalar chronology, cross-stage traffic, new recursive calls,
larger MOVE payloads, same-chart detours and rank redistribution are outside
this cut. #7208 bounds the fixed-line permutation preprocessing contract
with no preloaded copies and fixed public frames.
