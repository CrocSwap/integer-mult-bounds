Endpoint constructions and accounting replay
=============================================
The positive construction is a compensation subword, not a full supplier
or kappa improvement. It realizes orthogonal clique adjacency with dirty
helpers, and fuses a compatible matching layer over characteristic two.
Early cleanup permits proper helper endings at widths 4, 8 and 16.
Native endpoint wrappers, spectator banks and assembly admission remain
separate obligations. HANDOFF.txt gives the construction and its scope.

From the checkout root, run:
  python3 -I -O research/niemeier-lattices/workbench/continuation/endpoint-costs/verify_portable.py --workspace /path/outside-checkout/endpoint-replay
  python3 -I research/niemeier-lattices/workbench/continuation/endpoint-costs/verify_portable.py --normal --workspace /path/outside-checkout/endpoint-normal

The workspace is optional and defaults to a fresh temporary directory.
Only the standard library is required. Generated receipts and logs go to
that external workspace. The verifier compares all parsed JSON fields,
including the original full-ending clique control and the later proper-
ending fused receipt. It checks all pinned upstream bytes before use.
The five local replay entry points use exception-based checks under -O.
The omitted-cleanup negative control remains active in the fused replay.

clique_word.py checks the ordinary full-ending construction over integers.
fused_clique_word.py checks the characteristic-two word, full spinor/clique
alignment, the proper-ending version and its full-ending control.
hybrid_bound.py proves the stated all-stage obstruction using active
pressure alone. native_tensor_price.py uses PR600's pinned local receipt
and the stated tensor lift; it does not replay PR600's native pipeline.
tensor_price.py is an earlier conditional equal-factor invoice, retained
for comparison; it is not the later complete tensor construction.

The numerical comparison remains the historical PR600 declaration
0.001612722852614221 at head dfb7b827990d7b586b3cd778e3d750c050dd4778.
It is not silently updated to subsequent PRs. The enclosing continuation
records PR604 separately; none of these saved invoices uses its value or
claims to replay its cold-end construction.

Prepared for DominikScholz with OpenAI GPT-6 Astra assistance in T3 Code.
The upstream hyperplane-end mechanism, code, receipts and their inherited
lineage credit Jeremy Kothe / jeremykothe2 and the disclosed Claude Opus 5.5
assistance. sources/NOTICE.md is preserved byte-for-byte from PR600, as are
its source files. sources/SOURCES.json records exact source URLs and hashes.
The general Clifford-frame note is also preserved and pinned.

Archival upstream Python files under sources/ are quoted implementation
context and are NOT executed by this portable verifier. Their original
assertions and upstream no-O requirements are unchanged. This is the
explicit exception to the local replay's optimized-mode support; no
fresh upstream supplier replay is claimed. Original upstream paths in
sources/README.md are likewise retained as part of that pinned document.
