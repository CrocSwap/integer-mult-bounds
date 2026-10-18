# Twisted helper exits do not make feedback cheaper through four registers

For all **1,478** labeled boundaries `(h,y) -> (T h, y+K h)` with
`H >= 1`, `Y >= 1`, `H+Y <= 4`, and every `T in GL_H(F2)`, permitting
target-to-helper feedback does not lower the minimum number of unit XORs.
This is a finite exact negative result about a changed helper boundary, not a
new supplier or kappa. It answers the smallest instances of Sagar Thakrar's
[PR1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) question 3;
the requested three-helper/three-target case remains open here.

The earlier [PR1306](https://github.com/CrocSwap/integer-mult-bounds/pull/1306)
census requires `T=I`. Its restored-shear result and substitution lemma are
credited. This package does not rerun that larger census or claim another
H2/K admission. The new domain permits every invertible helper exit and
compares the shortest words for each fixed `(T,K)`.

## Exact boundary and invoice

All helpers and targets contain arbitrary independent dirt. Registers are
ordered helpers first, then targets. A gate `[d,s]` means `r[d] ^= r[s]`, with
distinct registers and cost one. The restricted alphabet excludes only a helper
destination with a target source; helper mixing and target mixing are permitted.
The unrestricted alphabet contains every directed XOR. Both require the complete
matrix `[[T,0],[K,I_Y]]`, including its zero target-to-helper block and identity
target-to-target block. No clean initial target or helper is assumed.

Every prefix XOR is paid, including any preparation and restoration within the
prefix. There are no extra registers, free permutations, frame moves, COPYs,
ERASEs, recursive calls, or other uncounted prefix operations. A length-L word
has L scalar ADDs and zero of these other event types. This is a local algebraic
price, not a hosted or precision invoice. An eventual inverse-T cleanup or
changed continuation must be charged separately. Even granting a favorable
zero additional absorption cost, feedback yields no advantage at any *fixed*
exit in this domain.

| Helpers | Targets | `(T,K)` maps | Maximum minimum XORs |
|---:|---:|---:|---:|
|1|1|2|1|
|1|2|4|2|
|2|1|24|4|
|1|3|8|3|
|2|2|96|5|
|3|1|1,344|7|

For example `h0 ^= h1; y0 ^= h0` has nonidentity helper exit
`(h0,h1)->(h0+h1,h1)` and target response `y0+h0+h1` at cost two.
It is accepted as twisted, while treating it as restored is rejected.
The census does not compare a twisted prefix to a restored prefix as though
their different outputs were interchangeable.

## Why the minima are complete

The primary checker performs ordinary breadth-first search from the identity in
each finite matrix group, with every declared gate as an edge. The full group
has `product_j (2^n-2^j)` elements; GL4 contains exactly 20,160. The restricted
group is the block triangular group, of size
`|GL_H(2)| |GL_Y(2)| 2^(H*Y)`. The generators produce the helper and target
diagonal groups and every helper-to-target elementary shear, so this is the
whole restricted group. Both cardinalities are checked after queue exhaustion.
Unit edge weights make the first-visit distances global minima. No bounded
search depth is substituted for exhaustion.

Every `T` and every binary K is enumerated without orbit reduction, and both
minimal witnesses are replayed on their complete binary matrix. Matrix equality
is equality over every F2 module, since every operation is an F2 coefficient
map. This algebraic statement does not prove physical address realization.

`independent.py` imports neither primary nor predecessor code. It represents
each transformation by a literal truth table on all `2^(H+Y)` dirty inputs and
builds both complete groups by output-table composition. All 1,478 distances,
the group distance layers, shape histograms, and maximum witnesses agree.
Both methods share the BFS principle; this is separate code/representation,
not independent human review or an independent mathematical proof method.

`RESULT.json` retains shape counts, complete group distance histograms, endpoint
cost histograms, a canonical digest of every labeled distance, and attaining
maximum witnesses. The replay recomputes all data. Six semantic controls reject
forbidden feedback, self XOR, Boolean register indices, target-dirt corruption,
unrestored feedback, and an incorrectly omitted twist. Two relocated positive
runs and ten subprocess controls test five actual receipt corruptions against
both engines, including a false minimum, missing gate, missing shape, wrong
helper exit, and incomplete group count. Checks remain active under `-O`.

## Reproduce and provenance

```sh
python3.12 -I -B scripts/research_package.py --package research/bit-twisted-feedback-four-registers
```

Expected lines include `PASS_TWISTED_FEEDBACK_FOUR_REGISTERS maps=1478
feedback_gain_maps=0 controls=6`, `PASS_TWISTED_FEEDBACK_TRUTH_TABLES`, and
`PASS_TWISTED_FEEDBACK_PACKAGE`. `verify.py --write` explicitly regenerates the
receipt. Standard library only. On restricted Windows hosts, set TEMP and TMP
to a writable workspace directory before running the subprocess controls.

Base and pre-submission canonical main are
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The picker nonce is `cb4ee3cfc909cd9f39b3f5949ed64666`, bit-mechanisms.
The prescribed PR1062 working example passed (661 columns, eight controls).
Its first attempt hit the sandbox temporary-directory permission error; the
unchanged replay passed after moving TEMP/TMP into the workspace.
`SOURCES.json` pins exact Git blobs and SHA-256 of the predecessor documents,
catalogue and selected record. No predecessor code is imported or changed.
The selected record remains PR1094; its complete cold replay is not run.

The overlap search included all fetched open PR bodies, local package metadata
and ledger. Full Discussion API coverage was unavailable due to rate limiting;
visible Start Here and Handoffs pages were read through Curiosity Bot. This
limitation is retained in `OVERLAP.json`, not treated as proof of novelty.
Nearby PR1937/2428 concern restoration absorption; PR2115 relaxes the target
basis. Neither is this fixed-target-identity feedback comparison.

## Open next questions

Can a fixed twisted exit show a strict feedback advantage with at least five
registers, together with a fully priced continuation that absorbs it? First
produce a concrete unrestricted word beating a certified restricted minimum;
then bind its exit to the continuation or pay an explicit inverse. No favorable
candidate or physical absorption is supplied here, so this result does not
justify extending the same census without a new lead. Structured question:
`TASK.json`.

Unrun obligations include actual R439 substitution, chronology across nonzero
frames, physical common-frame/climb semantics, native supplier replay, hosting,
precision/tape, all-size compilation, analytic transfer and formal proof.
There is no general no-feedback theorem, selected-frontier change, or new kappa.

## Credit

Sagar Thakrar / PR1868 supplies the twisted-helper contract and explicit feedback
handoff. @commdata2338 / PR1306 supplies the restored-shear model and census;
Hanson Sun / PR1557 extends it to three helpers/four targets. Credit woklerx /
PR1194 and Arham Tahir / PR1311 for semantic-D work, Zhihao Chen / PR425 for the
scalar interface, and the retained eumemic, DreamingOfClouds, Gareth Davidson,
theon199, Sagar Thakrar, Aaron Wang and Ross Richardson bit-word lineage.
Prepared for **ywz65**, with substantial OpenAI Codex assistance in research,
code, checking and writing. Apache-2.0; no independent human review.
