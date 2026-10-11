# Historical source527 checkpoint: publication of the completed audit

Douglas Colkitt, with OpenAI Codex assistance; 2026-10-10.

This publishes the previously completed conditional audit of **eumemic's
PR210**, pinned at `298f7c112889f799e8e2040099fbc325d0ccd0f6`:

**κ = 710046193349537 / 10¹⁸ = 0.000710046193349537.**

The result was announced after its audit but before its standalone package
was imported into main. The subsequent gen4 publication moved main directly
from 0.000661885549259598 to 0.000723571590007464. This import fills the
historical publication gap; it does not lower the current selected result.

## Construction and evidence

The [complete source package](../../research/five-stage-source527-banks/README.md)
and its original workflow are imported without changes from the pinned head.
All 121 package inputs and the manifest match the completed eight-stage
replay. The import receipt also checks git blob identity. Original whitespace
is retained where changing it would invalidate the audited source pins.

- [Full finite replay](../../research/community-round9-audit/pr210-verification.json):
  banks, bit, complex, finite, math, primes, raw and scalar stages all passed,
  including missing-stage and corruption controls.
- [Exact certificate](../../research/community-round9-audit/pr210-certificate.json):
  two moment engines, three finite ordinary-leaf levels, all 47 strict
  constraints and seven margins; the next headline grid point is rejected.
- [Additional complex scalar audit](../../research/community-round9-audit/pr210-complex-scalar.json):
  both signed directions, all 12,052 formal columns and 9,412 dirty roles,
  with independently propagated bounds and omitted-addition controls.
- [Full original round-nine report](../../research/community-round9-audit/REPORT.md)
  and [per-PR ledger](../../research/community-round9-audit/INDEX.md): historical
  review scope, individual findings and limitations, including verification
  contributions. These records do not imply that every reviewed PR is merged.
- [Publication checks](community-pr210-integration.json): exact import,
  preserved certificate and proof hashes, historical record validation and
  confirmation that the gen4 selection is unchanged.

The full numerical replay is reused from the completed audit because every
consumed source byte is unchanged. Import-time checks freshly validate the
manifest, source tree and certificate bindings. A fresh complete replay is
available through:

```sh
python3 -m pip install -r research/five-stage-source527-banks/requirements.txt
make source527-verify
```

For just the publication bindings, run `make source527-record-check`.

## Attribution

eumemic supplies the final source527 composition, internal cancellations,
target transformations and source reuse. The construction credits Henry Grant
/ hcg890 and Jacob Sussman's five-stage layout/complex baseline; Rohan Arun's
width-120 banking and helper refinements; Evan McKinney's completed-bank
method; Chafik Boukhalfa's physical helper/checkers; Avi Eisenberg's complex
helper; Dugongue's coordinated-frame lineage; and Romyxen / sennemmi's nineteen
operation-frame improvements. The complete upstream notices, licenses and
AI-assistance disclosures remain in the original package. Parallel work,
including Gabriele Nespoli's fixed-prime/finite-depth refinement, retains its
own entry in the published review ledger.

## Boundaries

This is a conditional finite construction. Uniform compilation,
common-ancestor/weighted charts, paid routing and restored rows,
prime supply, precision/recovery, complex symbolic correctness and the
all-size analytic reduction remain inherited dependencies. It is not a
complete formal proof of integer multiplication or a practical benchmark.

Later revisions of PR210 are not silently included. The copied round-nine
report states what had and had not been published when its review finished;
this document records the later publication. The report's PR236 Lean receipts
are published as review evidence, but the standalone PR236 source package
and the seven separately prepared tooling PRs are not integrated by this change.
