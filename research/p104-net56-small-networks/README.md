# P104 small networks and rational normalization

The 9/8 and 8/9 cases are dual by time reversal and orthogonal complement.
The 56-drop bound holds with at most one low gather in 9/8 and under the
dual one-high-deposit condition. Exact 8/8 and 9/8 witnesses attain 56.
A separate saturated equality witness has two dimension-seven gathers.
With eight depositors, the one-dimensional residual charts use distinct
normals from a pinned set of sixteen, with 8,766 qualifying independent
eight-subsets out of 12,870. See [small-network proofs](SMALL-NETWORKS.md).

Sequentially replacing charts by incoming spans and intersections with
outgoing constraints preserves the full rational transfer and all paths
at nonincreasing drop. A tight cover contraction preserves odd transfer,
while reachability can change. Paid routing preserves full transfer and
terminal reachability, with a sharp zero-drop specialization and a
positive-drop example where the invoice rises from 7 to 1,462.
See [saturation](normalization/SATURATION.md), [contraction](normalization/COVER-CONTRACTION.md)
and [routing and the slack bowtie boundary](normalization/ROUTING.md).

The proofs and exact Python checks were cross-reviewed by two independent
Codex agents. The remaining two-low case and legal-word realization are
open. Run the registered package from the repository root.

## Open next questions

Resolve the case of two dimension-seven gathers and eight distinct one-dimensional deposit charts.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
