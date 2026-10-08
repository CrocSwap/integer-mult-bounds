# Fixed local bases at (47,45)

The conditional witness is **κ = 16631776/10^12 = 1.6631776e-5**, with
bit saving `1663233/10^11`, beta `1/20` and headroom `1e-12`.
Both local bases are fixed to **I+J**, using the original envelope labels
and original oriented carrier matchings. This changes the construction
from PR33's generic local bases. The data profile is conservatively
**48 singletons +43+1933**; its former 37-block is not assumed to survive.

The proof establishes both full data corners through bipartite trees and
retains the first 43-block for every nonzero coordinate specialization.
The local profile rebuild checks all physical transitions. Exact minor
bounds use one prime for rank-two corrections and three primes for both
rank-three source growth and rank-four core changes. Lucas–Lehmer checks
establish primality. These are exact zero certificates, not sampled ranks.
The complete histogram has the same physical rank and paid copy correction.

```sh
make fixed-basis-two-stage-check
make fixed-basis-two-stage-producer
make verify
```

The producer requires a C++17 compiler and reconstructs both actual scalar
DAGs, every original label dependency, carrier matching and local profile
in temporary storage. It compares the entire result to the checked-in
records. The arithmetic checker validates pinned predecessor sources,
minor bounds, actual incidence trees, physical rank, the rational moment,
47 strict assembly conditions, seven margins and negative controls.
The moment gap exceeds `3.14e-14`; the assembly gap exceeds `7.49e-13`.
Failure at the next moment grid point concerns the sufficient enclosure,
not global optimality. Eventual analytic and fixed-setup cutoffs remain.

[The proof](../../notes/fixed-basis-two-stage.tex) and generated
[certificate](certificate.json) state the conditional scope. The generated
patch replaces the pinned PR33 corner manuscript; apply it independently
of the other historical proof replacement patches. No PDF is generated.
Finite calculations do not formally verify the full multiplication theorem.

Credit icekylinx's PR32 fixed-basis projectors/profiler and exactness method
at `0ef3aeb61f55cc0b321ce6a0ef00acee25cefe52`; unchanged sources are in
`references/fixed32/`, with hashes and provenance. The adapted profiler
extends three-prime certification to source growth at the new dimensions.
Credit Zhihao Chen's PR29 topology and PR21/23 transfers, Paureel/Aurel Prosz
and Swapnil Jain's two-stage development, Rohan Arun's PR31 moment/assembly
modules and corner refinement, icekylinx's preceding producers, RaD/hipotures,
and all authors retained in NOTICE. Dominik Scholz, with substantial
OpenAI GPT-6 Astra/Codex assistance, contributes this composition and its
exact evidence; the inherited dimension work also used Claude Opus 5.5.
Original licenses and attribution remain.
