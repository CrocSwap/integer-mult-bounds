# Attribution and license

This new package is Apache-2.0, following the repository license.
Prepared for @woklerx with substantial OpenAI Codex assistance in the
algorithm, proof, implementation, review and writing. Agent cross-review
is not independent human review.

themilkman216's PR968 (`research/complex-frame-pair-decoders`) supplies the
original exact frame-pair search, E8 data and every inherited D/E/H check.
The new mask enumerator is an explicitly credited representation-level
rewrite of that search. Its ordered outputs are compared to the pinned
reference. Source files remain unchanged; no source license is replaced.

JosieElliston's parallel PR1071 adds independent geometry and delivery
bounds for frame-pair centers. PR1077 extends the coefficient-field proof.
Neither is a dependency of this performance result, and no such mathematical
finding is claimed here. PR1075, PR778 and PR824 concern different exact
replay kernels. PR1044's dependency-DAG work is a separate optimization.
