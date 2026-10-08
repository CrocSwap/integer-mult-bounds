# All-rank profile-cost reclamation

This finite conditional witness gives

κ = 10206752116843 / 200000000000000000 = 0.000051033760584215,
with bit saving a = 51036365162009 / 10^18 and the inherited h = 10^-12.

It exceeds the PR #65 mixed-order bound 0.000051028985071975 by
0.000000004775512240. This is a bound comparison, not a claim about formal
proof coverage or practical multiplication speed.

## Change and paid quantities

The PR #62 pair graph, region order, carrier matching and local linear
synthesis remain those used by PR #63. During reclamation, the compiler now
examines every eligible dependent retired role, including lower-ranked roles,
and selects a witnessed clearing operation using actual fixed-basis profile
costs. PR #60/#63 instead stop at the first dependent role in descending rank.

The candidate uses an integer score: each transition's inherited fixed-basis
pivot/CRT profile is evaluated with t times a fixed integer midpoint of the
exact rational ln(t) enclosure at scale 10^30. The score estimates the entropy
change of growth plus final cleanup. Later uses can alter that prediction, so
it is solely a deterministic discovery heuristic. The reported bound comes
from complete physical replay and the full paid exact moment, not the score.
No floating-point arithmetic affects candidate selection.

| Axis | Roles | Reclamations | Clearing XORs | All elementary XORs |
|---|---:|---:|---:|---:|
| 23 | 27918 | 801 | 1415 | 148975 |
| 25 | 36586 | 1090 | 1950 | 205773 |

The complete paid width, rank mass and deficit remain 137151806,
78860441550 and 1846900. All endpoint copy, exterior and data-growth costs
are retained. Neither fewer XORs nor unchanged width alone proves improvement.
The bounded search compared rank ties, signal sparsity, containment scarcity,
rank-entropy and physical-profile scores. No global optimality is claimed.

## Why selecting a later dependency is valid

At an acquire call, the linear basis contains current anchors and earlier
eligible independent retired roles. Each retired role enters the basis only
after its frame is checked to be contained in the requested frame. A dependent
candidate returns a literal XOR expression containing itself and basis roles.

Enumerating later candidates mutates only this temporary basis and stored
witnesses. It does not change any physical value, frame, operation or event.
Thus a stored dependency remains valid when another candidate is considered.
For the selected witness, the unchanged xor function checks containment and
charges the frame raises of both operands on every emitted XOR. It clears the
selected role, removes that role from the retired set, and reuses it through
the unchanged compiler. The other XOR operands keep their values. Allowing
candidates from additional ranks does not waive any eligibility check.

This establishes that the selection rule chooses among valid literal clearing
witnesses. Independently, the serialized circuit is replayed on every input
and dirty basis vector in both orientations; every physical transition is
reconstructed from the actual word and every fixed-basis profile is rebuilt.
The unchanged inherited constructor verifies the complete paid rank identity.

## Reproduction and controls

From the repository root, with Python assertions enabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research/slot-cost-rank-pair/verify.py
PYTHONDONTWRITEBYTECODE=1 python3 research/slot-cost-rank-pair/verify.py --rebuild
PYTHONDONTWRITEBYTECODE=1 python3 research/slot-cost-rank-pair/test_negative.py
PYTHONDONTWRITEBYTECODE=1 python3 research/slot-cost-rank-pair/arithmetic/refine.py
PYTHONDONTWRITEBYTECODE=1 python3 research/slot-cost-rank-pair/arithmetic/audit.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s research/slot-cost-rank-pair/arithmetic -p test_arithmetic.py -v
```

The physical verifier checks source and artifact digests, complete dirty-basis
replay, exact transition reconstruction and every physical profile. --rebuild
also regenerates both words with the committed portable compiler and requires
byte equality with the decompressed committed witnesses. CXX can specify a
working C++ compiler/sysroot. All disposable outputs go into
build/slot-cost-rank-pair, or the explicit --work-dir directory.

Seven physical controls reject an omitted XOR, understated role count,
omitted paid transition, altered word/profile digests and optimized Python
for both the compiler and verifier. Arithmetic verification has its own
independent rational bounds, adjacent-grid failures and adversarial controls.

## Scope and attribution

The original-envelope interpretation, analytic, semantic, routing, recovery,
fixed-tape and all-size transfer hypotheses remain inherited. This is a finite
conditional certificate, not formal verification of those hypotheses.

Retain Avi Eisenberg's PR #62 graph attribution, Chafik Boukhalfa's PR #60
rank-first compiler contribution, eumemic's PR #57 joint frame compiler, and
Dominik Scholz's PR #63 composition with OpenAI GPT-6 Astra assistance. The
PR #62 graph was prepared with Claude assistance; the PR #57/#60 compiler used
OpenAI Codex assistance. The inherited sources retain their full earlier
credits, including OpenAI, Harvey–van der Hoeven, icekylinx and collaborators.
This profile-cost selection experiment and packaging are by Rohan Arun with
OpenAI Codex assistance. Apache-2.0 applies with the inherited notices retained.
