# Bounded independent-neighbour pair handoff

Status: negative under the complete optimistic fixed-graph invoice. No
profitable physical candidate was found or claimed, and no kappa is claimed.
No remote mutation was made by this agent.

Public prospective claim:
https://github.com/CrocSwap/integer-mult-bounds/pull/4867#issuecomment-6353171449

* Exact geometry: 511 empty-chart hyperplanes, two distinct neighbours each.
  Opposite neighbours above one hyperplane have mutual distance one.
* Actual domain: 256 distinct original rank-zero internal pairs, both opposite
  assignments: 261632 cases; 1831424 actual incident rank calculations.
* Result: 44 histograms, all dominated in the nine exact min-rank tariffs by
  `3H1+H7-H8`. Cost is at least `3+7^theta-8^theta >= 2` for
  `0<=theta<=1`. Best developed-C value is approximately 2.0090712929448316.
* Independent replay: Python imports no predecessor rank engine, combines
  independently recomputed single-endpoint invoices and shared-edge correction,
  and exactly matches all C++ histogram counts. It also checks geometry,
  helper/paid inventory, changed-graph controls, and every rank-eight edge.
* Analytic completion: #4867's single/common-axis theorems plus the new
  opposite-neighbour screen close every independent one-neighbour assignment
  on every rank-zero internal edge. Different hyperplanes have shared rank two
  and cost at least `2-2^theta>0` for theta below one.
* Rank-eight gate: all eight remaining internal edges have degree-four
  endpoints, each with two external rank-zero edges and one external edge of
  rank at most two. External changes cost at least two jointly; shared rank
  stays at least six. Therefore cost is at least
  `2+6^theta-8^theta >= 2-2^theta>0`. The nominal 8355872 rank-eight pair
  choices were not scanned because this complete optimistic gate rejects them.

The conclusion retains all 640 arbitrary owners, the original scalar/native
word, endpoints, all 408 helper jobs and zero extra centre reward. It does not
close three or more independently changed contacts, changed scalar words,
changed demand, native intermediate reuse, or a different caller contract.

Science inputs are frozen at global-centre-cut commit
`159eb73dd70ccdb03af6f61435135c026cf9886a`; final metadata is
`673b1f38379ee88513dfbe2d828845afa7c2f9ec`. `SOURCES.json` hashes the exact
source/graph files. The worktree remains at base
`624de9dc66858af0945e5f8a0942488d62280d43`; all new files are under this
outputs directory, and no predecessor package was edited.

Reproduce from the project root:

```sh
python3 sol1337-global-centre-cut/research/sol1337-global-centre-cut/build_graph.py dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs
g++ -std=c++20 -O3 -Wall -Wextra -Werror -I sol1337-global-centre-cut/research/sol1337-global-centre-cut/vendor dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs/scan.cpp -o dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs/scan
dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs/scan dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs/center-contact-graph.txt dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs/SCREEN.json
python3 -O -W error dyadic-full-controller-20261023/outputs/opposite-neighbour-pairs/verify.py
```

`PROOF.md` contains the exact bill identities and analytic extensions.
`SCREEN.json` stores every histogram. `VERIFY.json` records the independent
replay. `RANK8-CENSUS.json` records all eight analytic-gate edge inventories.
