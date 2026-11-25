# Coordinated source-purification donor experiment, PR233

## Main finding

Purifying a donor is not equivalent to obtaining a free zero carrier. In the
tested fixed word, it removes fresh rank at the consumer and thereby creates
an additional dirty storage requirement. Sharing one paid source parity frame
across up to eight purifications does not amortize that requirement.

This is a precise failure of this proposed modification, not an impossibility
theorem for source-assisted constructions. No improved supplier is claimed.

Pinned basis: PR233, commit 109a857a329d18ed5552d5573f17ddfa886ae57f.
The source archive was extracted into `source` by `setup.py`. The immutable
source-aligned cache was shared from the composition worker; input hashes are
in each receipt. We do not rerun its expensive baseline regeneration.

## Rank-throughput lemma (elementary, exact)

At an interface let n be the number of incoming dirty registers, d the rank of
their fresh components modulo available source controls, t the number of
required outgoing dirty registers, and r their fresh rank. Assume the required
fresh outputs are in the available span and the interface preserves all old
values by an invertible dirty-row transformation. Its minimum number of new
independent dirty registers is

    b = max(0, t + d - r - n).

Indeed n+b-t retired registers must retain the d-r fresh directions not
represented by the outputs, hence n+b-t >= d-r. Conversely, choose bases for
the outgoing fresh row space and a complementary fresh row space, and extend
the resulting independent dirty rows to an invertible basis using b fresh
dirty registers; the remaining output dependencies consume t-r dirty rows.
This is the interface model used by the existing flow checker, not a claim
about unrestricted algorithms or arbitrary nonlinear operations.

In particular, when d=n, b=t-r. Erasing one outgoing fresh direction while
leaving t fixed necessarily increases the local dirty birth count by one.
This holds even when the incoming fresh rank and input count both decrease
by one. Available source controls can set d=r=0 at the purification site,
but do not remove arbitrary old values or eliminate this downstream bound.

## Explicit representative

Replace physical donor 3708 (dimension 3) by unused donor 2559 (dimension 2)
for recipient 13377. The new donor lies in the original paid parity source
frame S=[580,328,204] with ports [425,426,428,431]. The chronology and exact
binary frame containments are screened before pricing.

The complete flow comparison `node-delta.json` records:

* At donor frame [580,388], (n,d,t,r) changes (2,2,2,2) to (2,2,3,2): one extra birth.
* At its source parity frame, one incoming fresh value is erased and one dirty register retires.
* At the recipient frame, (4,4,2,2) becomes (3,3,2,1): one extra birth by the lemma.
* The old donor's frame retires one extra register but cannot reduce its birth count.
* One eligible dirty-kernel reuse recovers one birth. Net R and W still increase by one.

The exact integer child-histogram difference produced by the flow accounting is
ΔH={1:+3,2:+3,4:-3,15:-3,19:+6}. Its weighted sum is 66=3h with h=22,
consistent with one additional full dirty role. The numerical local root falls
from 0.0007099074827603464 to 0.0007098787901245577.

## Bounded coordinated experiment

The initial exact geometry screen found 2,380,224 legal donor substitutions
among unused source-purifiable donors for the higher-rank used donors.
Three distinct rank4-to-rank2 replacements were fully flow-priced; each lost.
Then one common parity source frame was selected, and 1,2,4,8 distinct
rank3-to-rank2 substitutions were priced jointly with recomputed kernel matching.
This allows coordinated paid changes rather than fixing the old kernel list.

| Substitutions | Net additional R | Kernel reuses | Local root |
|---:|---:|---:|---:|
| 0 | 0 | 0 | .0007099074827603464 |
| 1 | 1 | 1 | .0007098787901245577 |
| 2 | 2 | 1 | .0007098548693364839 |
| 4 | 4 | 2 | .0007098022637057777 |
| 8 | 8 | 4 | .0007096941773183611 |

All prices include frame crossings, dirty births, cleanup, center controls,
source/target factors and legal kernel reuse. They are modular-rank discovery
screens at prime 1000003, not exact characteristic-zero lift certificates.
Losing candidates were not sent through the expensive exact lift/endpoint
contract. The rank-throughput lemma is proved independently of those screens;
the reported graph profiles remain computational observations in that model.
No full assembly improvement is possible from these observed worsening local
profiles; no changed final κ is claimed. Exhaustiveness is only for the stated
geometry screen, not optimization over coordinated subsets or new words.

## Reproduction and next condition

From the workspace root, after the shared aligned cache exists:

    python3 -B round27/joint-notes/setup.py
    python3 -B round27/joint-notes/screen_swaps.py
    python3 -B round27/joint-notes/bundle_screen.py
    python3 -B round27/joint-notes/price_swap.py
    python3 -B round27/joint-notes/price_swap.py --index 0
    python3 -B round27/joint-notes/price_swap.py --plan round27/joint-notes/bundle-1.json
    python3 -B round27/joint-notes/price_swap.py --plan round27/joint-notes/bundle-2.json
    python3 -B round27/joint-notes/price_swap.py --plan round27/joint-notes/bundle-4.json
    python3 -B round27/joint-notes/price_swap.py --plan round27/joint-notes/bundle-8.json
    python3 -B round27/joint-notes/compare.py
    python3 -B round27/joint-notes/node_delta.py

Each output tree retains its changed physical pair list, frozen frames, complete
flow witness, priced histogram and input hashes. The scalar schedule is unchanged.
Scripts use relative workspace paths, including the shared aligned cache path
explicitly recorded in `price_swap.py`; this cache must be retained for resumption.

A viable follow-up must avoid the loss of outgoing fresh rank at fixed output
width—e.g. simultaneously reduce the number of outgoing dirty rows, retain a
useful fresh carrier, or supply a legal already-retired dirty row at the recipient.
Merely making more donors source-purifiable does not satisfy that condition.
This is a targeted obstruction, not a recommendation for another broad search.
