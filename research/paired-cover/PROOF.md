# Paired lockstep vertices in the first stage of a three-stage cover

## 1. Claim

Under every interface retained by PR #130 (its three-stage Cayley cover, general Clifford frames, weighted bit
interface, borrowed rows, the semantic/bulk assembly and the inherited analytic and fixed-tape hypotheses),

κ = 1708101/5000000000 = 3.416202 × 10^-4,

which is +8.59% over PR #130 (3.146011 × 10^-4) and +2.83% over PR #131 (3.32205398986 × 10^-4). The complex side
binds. The next κ grid point at denominator 10^10 is rejected.

| per pair of first-stage vertices | PR #130 | here |
|---|---:|---:|
| persistent streams | 2(2v + 3R) = 180,326 | 4v + 5R = 151,621 |
| complex saving | 3.147997e-4 | 3.418543e-4 |
| stopped bit saving | 3.731650e-4 | unchanged |
| κ | 3.146011e-4 | 3.416202e-4 |

The new ingredients are a pairing of first-stage vertices that share their auxiliary streams, and the lockstep
execution of each pair. No local word, frame, data stream, router, partition or bit construction changes.

## 2. Setting (PR #130)

E = A ⊥ B ⊥ C with dim A = h = 24, dim B = dim C = 23 and m = 70. Every vertex k of G = O(E) runs PR #117's local word
in every stage; its active space is kA (for stage one, kA = g(B + q_S) for the data positions it serves, by
R_{12,S}). The offsets are 0, kB and k(B + C) in stages one, two and three. Each stage has its own auxiliary bank of
R roles per vertex, and a role with entrance gauge σ pays an exterior of rank m − h + dim σ (PR #130's dirty-tail
lemma).

## 3. The pairing

Let κ be the coordinate involution of E that exchanges e_i and e_{24+i} for i < 24. It permutes coordinates, so it
is orthogonal, κ² = 1 and κA ⊂ B + C is orthogonal to A. For every k, kA and (kκ)A are orthogonal, and k ↦ kκ is a
perfect matching of the first-stage invocation set G without fixed points.

In stage one the offset is 0, so a core touches only its active space. Give the paired cores k and kκ one common
stream for each role u. Each core acts block-diagonally on its own coordinate directions and accepts every state on
the other directions as spectators, exactly as in PR #128's completed-core sharing; the data and target streams of
each core are its own and unchanged.

Stages two and three carry the offsets kB and k(B + C): a core there occupies kA + kB (47 dimensions) or all of E,
so no orthogonal partner fits, and those banks stay as in PR #130.

## 4. Lockstep and the merged children

The paired cores run the same first-stage word, so they can execute it together, gate by gate. At every time the
common stream's frame is U_1 ⊕ U_2 with U_1 ⊆ kA and U_2 ⊆ kκA the two cores' current frames. A joint step from
U_1 ⊕ U_2 to U_1′ ⊕ U_2′ is a transition between nested binary subspaces of E, so by PR #130's general Clifford
lemma ("for U ⊆ V, the exact transition T_V T_U^{-1} has rank dim V − dim U", with two rank-zero adapters around
one C^{⊗r} factor) it is a single child of width (dim U_1′ − dim U_1) + (dim U_2′ − dim U_2). The lemma holds for
degenerate subspaces as well. Run one after the other, the same operator would be two children.

At the end of the joint word, the dirty tail of the shared stream has rank m − 2h + 2 dim σ_u (PR #130's tail
formula applied to the direct sum of the two cores' frames and gauges, which lie in orthogonal coordinate
subspaces). So per pair of vertices, the first-stage bank contributes R − Σs_a exteriors of width m − 2h,
s_a exteriors of width m − 2h + 2a, and its internal children at twice their widths; stages two and three and all
data histograms contribute exactly PR #130's amounts for two vertices.

## 5. Finite profile and checks (`paired_cover.py`)

* Inputs pinned by SHA-256: PR #130's `certificates/three-stage-cover-complex-input.json` and
  `certificates/three-stage-cover-network.json`.
* The unpaired per-vertex profile rebuilt from the input equals PR #130's certified per-vertex children.
* κ is checked to be an orthogonal involution with κA ⊆ B + C.
* The paired profile telescopes: W·m − s = 2(2v − 3ℓ) per pair, the same deficit per vertex. Every child is below m;
  the largest is 68.
* The complex saving is the largest on the 10^-10 grid under PR #104's exact moment (next point rejected).
* The bit saving is PR #130's certified stopped saving, unchanged.
* The finite bridge is PR #130's construction with the paired stream count (group order, local and router charges,
  semantic induction, row stock 160000); the 47 strict constraints and 7 margins of the assembly hold at κ, and the
  next κ grid point is rejected.

Not machine-checked here: the lockstep schedule and the shared tail (§3–§4) are stated as proofs, not replayed.

## 6. Scope

All of PR #130's interfaces remain assumptions, including the opposite-bank factorization and the common
generic basis for the enlarged finite family of transitions (the merged first-stage transitions are among them).
The same lockstep principle applies wherever identical cores share streams on orthogonal subspaces: on PR #129's
completed-core groups (11 or 24 cores per stream) it raises κ from 1.29186e-4 to 2.05734e-4. No global optimality is
claimed.

## 7. Credits

* **icekylinx**: the three-stage Cayley cover, general Clifford frames and weighted bit interface (PR #130), and
  the stopped product-ring framework (PR #104).
* **an664**: completed-core sharing (PR #128); **eumemic**: PR #117's local DAG, PR #129 and PR #131.
* **Zhihao Chen (jacklightChen)**: PR #97's bit ledger; **Swapnil Jain**: the round-seven bit witness.
* Everyone credited in PR #130's NOTICE and SOURCES.json.

The pairing, the lockstep schedule and this certificate were prepared by Avi Eisenberg (ikeboy) with Anthropic
Claude assistance.
