# Current personal matrix review edition

This is Alejandro Zarzuelo Urdiales's personal July generalization, separate from the contestant matrix submissions.

The final qualified scope is **11 sources and 45 distinct selected declarations**, using only standard kernel axioms. The frozen nine-source/35-declaration core remains byte-preserved; its README and source_manifest.json describe that earlier subset. [The final integer extension guide](README_FINAL_INTEGER_EXTENSION.md), [final source manifest](lean/final_source_manifest.json) and [final checker](lean/check_final_selected_axioms.py) are the current full reproduction entry points.

The general block and instruction-program theorems have separate ordinary component-validity hypotheses. The concrete order-16 theorem derives the actual matrix product and 2208 scheduled products from proved coefficient data and an explicit 46-product leaf. The integer extension proves a numerator equal to eight times the product over every commutative ring, and exact final integer division by eight; its arbitrary-size version uses a separately valid leaf and schedules 48 times that leaf's product count. It does not assert universal leaf existence, global optimality, tensor rank, numerical stability or journal acceptance.

From the lean directory, fetch the pinned dependencies and Mathlib cache, then run:

```
python3 check_final_selected_axioms.py
```

A fresh timestamped result is written to lean/reproduction. The manual GitHub workflow invokes this final checker. [The clean GitHub run](https://github.com/alejandrozu/openmath-2026-judging/actions/runs/37675264184) completed successfully at proof commit `9e13c89a51a62958ced9ebdf16da31f5e2fb3cdd`, checking all 11 sources and 45 selected declarations with only standard kernel axioms. The [downloaded actual reproduction and qualification](evidence/github_ci/37675264184/actual_download_qualification.json) bind the source hashes and actual audit output. Historical local evidence remains separately preserved.

The [flat circuit and independent polynomial replay](circuit/README.md) can be reviewed without Lean. The redundant temporary regenerated circuit is intentionally omitted; its actual replay digest and coefficient-by-coefficient equality record remain available. The original circuit is unchanged.

The [current clean nine-page manuscript](manuscript/Hybrid_Composition_revised.pdf) and its [current manifest](manuscript/current_manuscript_manifest.json) retain immutable proof links and author/tool attribution. [Current image QA and typesetting evidence](../author-return/2026-10-07/README.md) are distinct from the45 selected proof declarations. Earlier native-editor failures and earlier document snapshots remain historical, without implying current journal acceptance.
