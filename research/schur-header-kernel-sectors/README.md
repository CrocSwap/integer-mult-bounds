# Sharp Schur kernel sectors from the original header

For a common identity-pivot deletion of size d with maximal residual
commutator rank 2d, the four joint kernel-sector dimensions are

```
(r00, r10-d, r01-d, r11-d).
```

Here the r values are the **original** commuting pair's joint-sector
dimensions. The [proof](PROOF.md) gives explicit original-space bases:
project V00 by I-i*pi, and intersect each other original sector with ker pi.
It works over every field and for arbitrary compressed product H, including
an eigenvalue-one component and singular or empty 00 factors.

The opposite-sector count is r10+r01-2d. This answers the original-header
question of [PR #5287](https://github.com/CrocSwap/integer-mult-bounds/pull/5287)
and supplies its complete central classifier without a full residual kernel
calculation. `header.py` provides both the constructive kernel bases and
`central_from_header(h, sizes, q)`. The retained scalar classifier supports
F2,F3,F5,F7; the written sector theorem is over every field.

Python 3.12 and the standard library are sufficient:

```sh
python3.12 -B scripts/research_package.py --package research/schur-header-kernel-sectors
```

Both registered normal and optimized commands end with
`PASS_SCHUR_HEADER_KERNEL_SECTORS`. `verify.py --write-result` regenerates
RESULT.json. Normal verification writes no package files. The checks build
full projectors and headers, verify sharpness independently, and compare all
four explicit bases with full residual kernels and complete central invariants.

The sharp rank assumption is required. This is a central-state interface,
not a full ordered-pair classification, header probability, later-guard law
or physical supplier. The original profile must be supplied or computed;
its cost is not free. The complete kappa and selected frontier are unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0.
Nick Petalas supplies the sharp-sector criterion, ssafwann the block and
nilpotent Schur extensions, and #5287 the unchanged central classifier.
`NOTICE.md` and the retained source documents preserve the full lineage.
`SOURCES.json` pins all copied bytes to an ancestor of this contribution.

## Open next questions

Pin a named consumer and state whether it needs the central class or the full
ordered-pair extension data. Then specify the header law and complete paid
selection/emission boundary. The present formula alone does not determine
unconditional multiplicities, later-guard survival or native physical cost.
