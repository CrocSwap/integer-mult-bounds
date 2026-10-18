# R420 Lean source-expression audit

This independently checks the external correspondence between PR612's Lean data and PR543's historical R420 supplier. The existing maintainer audit already confirmed the seven data fields. This package additionally checks the **actual alias and derived expressions** used to assemble those fields, and makes the check portable.

The historical [`im-cold617-formal-binding.py`](../community-cold617-audit/im-cold617-formal-binding.py) extracts three B-gate lists and concatenates them itself. It does not read the Lean definition of `phaseB`. It similarly constructs `start` itself and assumes the recorded frame, final and inherited-data expressions. Thus its external comparison can pass after some of those Lean expressions change. This is a limitation of that standalone audit, not a defect found in the original circuit or a bypass of PR612's hash-pinned Lean build.

## Reproduce

From the repository root, using Python 3.11+ and its standard library:

```sh
python -I -B research/r420-lean-source-binding/verify.py
python -I -B research/r420-lean-source-binding/test_binding.py
```

Both commands also support Python's `-O` mode. They read the existing source files and create no repository outputs by default. No Lean installation, supplier execution or network is required.

Expected verifier output:

```text
PASS_R420_LEAN_SOURCE_EXPRESSIONS fields=13 frames=672 gates=837 operands=1077
```

The verifier compares its complete deterministic report against [EXPECTED.json](EXPECTED.json). The test command passes 13 tests, including 33 distinct negative cases. Six demonstrate changes accepted by the assertion-enabled historical script: `start` offset, B-band order, the `lines`/`frames`/`scatter` reversals, and the `final` prefix length. The revised semantic checks reject them independently of source-hash admission. Other controls cover malformed declarations, constructors, indices, order, multiplicity and JSON types; unchanged inputs, nested comments and recompression pass.

## What the comparison establishes

The checker has its own restricted tokenizer and literal parser; it imports neither the supplier nor the historical audit. It accepts only the recorded forms of the imported aliases and derived expressions. This deliberately small grammar is **not a general Lean interpreter**. A semantically equivalent source rewrite can require a reviewed parser update.

It reconstructs and compares all seven ordered fields: 120 line labels, the 672-frame table through its explicit permutation, both 660-entry endpoint arrays, nine retained helper identifiers, all 837 B gates including their 1,077 operand occurrences, and all 120 scatter rows with 568 index occurrences. Order and multiplicity are preserved even where a weaker scalar check could ignore them. The inherited PR590 frame/line/scatter data are read from the maintainer's retained source files; their historical 489-helper instance is not substituted for the R420 instance.

The six scalar/domain fields `h`, `v`, `R`, `format`, `form` and `coords` are also compared, giving 13 fields in total. The checker does not interpret the supplier's other fields or prove the meanings of those metadata labels.

Source pins identify the exact base and consumed files. The original gzip container remains pinned as an immutable input. An alternate compression of the identical decompressed payload can be checked without requiring the same gzip header or stream.

Use `--word /path/to/recompressed.json.gz` for that comparison, `--root /path/to/checkout` for a different source root, or `--json` to print the checked report. The default root is derived from the checker's location.

## Boundary and attribution

This is an independent external source audit, not a new Lean theorem or a fresh kernel build. The source equality and prior Lean results remain separate pieces of evidence. The full A/C cleanup, D compensation, current COPY/ERASE lifecycle, physical frame transport, hosting and all-size multiplication transfer remain outside this package. No new kappa, current-frontier applicability, runtime improvement or complete multiplication proof is claimed.

The base is `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. PR612 and its PR590 dependencies are James Chang's (`jamesyc`) formalization, with disclosed OpenAI assistance. PR543 is eumemic's R420 supplier, with disclosed Anthropic Claude assistance and its retained predecessor lineage. Douglas R. Colkitt's maintainer audit supplies the prior correspondence script and receipt. Their original files and notices are unchanged.

Prepared for **Chinmay Arvind (@chinmayarvind23)** with substantial **OpenAI Codex assistance** in implementation, controls, review and writing. Licensed under the repository's Apache-2.0 license. Automated agent review is not independent human peer review. See [CLAIM.md](CLAIM.md) for task selection and overlap, [SOURCES.json](SOURCES.json) for pins, and [VALIDATION.md](VALIDATION.md) for measured checks and limitations.
