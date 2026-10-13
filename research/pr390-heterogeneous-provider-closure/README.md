# PR390 heterogeneous physical-provider closure in exact RAM

This addendum completes the mathematical physical-provider and ordinary
scalar/index RAM argument for the **existing pinned PR390 construction**. It
adds no circuit rewrite, bank-packing gain, selected multiplication bound or
new cyclic exponent. The source-specific closure is the contribution.

The construction uses the h=9, v=120, R=783 literal word at
[PR390, 0e790f2](https://github.com/CrocSwap/integer-mult-bounds/tree/0e790f2dfb64e17bdee154aee151bb0c1dddb28e/research/e8-prefix-restoration),
including its existing dirty preconditioning, early sinks, exact endpoint
adapters and inverse bank owners. It constructs an explicitly heterogeneous
interface; it does not cast those sinks into the unchanged homogeneous
`BR.Inv` contract.

The [proof](PROOF.md) establishes:

| Statement | Exact scope |
| --- | --- |
| Physical B_K | Every fixed K>=1 and positive tensor multiplicity f; arbitrary correlated live data/helper arrays; private work cleared before use and zero on exit |
| Optimized B4 | m=73, W=58,899 live families per orthogonal owner, rank mass 4,289,643 and deficit 9,984; all recursive and nonchild costs charged |
| Gaussian/Walsh | One fixed exact scalar/index RAM program on every power-of-two length, work O(N(log(N+2))^(1023/1024)); specified scalar i for the Gaussian kernel |
| Cyclic corollary | The inherited Sussman exponent 1-7474546/10^10, all positive lengths, with a supplied canonical positive root at selected order 0<D(N)<8N^3 and one charged root primitive |

The RAM model charges indexed access, scalar/index preparation, fresh array
allocation, stack work and bounded recursion, with one fixed polynomial
word/arena cap. Complex scalar values have unrestricted exact heights. This
is a mathematical program-existence/work theorem. No new closed Lean term,
practical fast implementation, finite-alphabet precision or tape-layout
certificate, original Family130 manuscript equivalence, or global integer
multiplication theorem is claimed.

## Retained finite evidence

The independently reconstructed scalar leaf was already checked on every
1,031 column in both orientations: 1,023 live columns, including all 783
dirty helpers, plus eight initially dirty active center columns. The existing
exact audits also checked all 3,135 phased transition recipes, 240 data
adapters, two sink adapters, the global owner/phase/packing invoice and the
integer-only strict moment. Those completed results were reused during this
publication preparation; they were not rerun and no contributor program was
executed.

The supplied standard-library checker reconstructs the scalar word directly
from the three pinned public literal files and tests its complete operator:

```sh
python3 -B own_scalar_columns.py
```

It writes resumable results under `own-scalar-results/`. This is a finite
scalar replay, not a full phased physical compiler, an all-size execution,
a Lean build or a stand-in for the universal proofs. Its mathematical
functions are unchanged from the completed referee replay; only the literal
input directory was relocated for this package. The complete Clifford
lowering follows the constructive algebra in PROOF.md, not a hidden external
fast-provider premise.

[PROFILE.json](PROFILE.json) records exact arithmetic and completed-check
scope. [SOURCE.json](SOURCE.json) pins the public inputs and interfaces;
[NOTICE.md](NOTICE.md) credits the construction and transfer lineage. New
exposition and the independent scalar checker were prepared with substantial
OpenAI Codex and ChatGPT Pro assistance. The reported independent checks are AI referee work,
not independent human peer review or kernel certification.

The manifest binds this prepared package's bytes, subject to an external
reviewed revision/archive anchor. It does not authenticate itself, prove the
theorem or assert that a future execution took place. Original source and
review artifacts remain preserved separately.
