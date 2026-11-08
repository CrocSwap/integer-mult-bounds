# Owned ascent (assumption A6): declaration, cost proof, precedent

## The change (one line)
`local.py:126` / `native.py:55`, rule "Nested chronological transport": for an owned MOVE the requirement `frames[b] < frames[a]` (descend) becomes
`frames[b] < frames[a] or frames[a] < frames[b]` (nested either way). Public MOVEs still ascend strictly. Nothing else changes: `verify_strict.py` is the
predecessor rule, `verify_relaxed.py` the changed rule; `check.py` runs both and shows that the strict verifier rejects this word at exactly the 23 owned-ascent events (rank mass 56).

## A6, stated as an assumption
An owned nested rise costs one paid H_r plus rank-0 adapters, with no credit, on arbitrary contents, factorwise at every tensor width, and CLEAR at any frame stays under the
owned_erasure assumption. It is load-bearing: no ascent, no word. The reported kappa is conditional on A6.

## Direction-free cost
Each MOVE a to b between nested frames applies C_b C_a^{-1}, of rank |dim b - dim a|; the inverse of a rank-r chart change is a rank-r chart change
((C_b C_a^{-1})^{-1} = C_a C_b^{-1}), so a rise and a fall between the same frames are paid the same r. The word's histogram charges every MOVE |delta dim|, owned rises included
(the owned rises are 10, 4, 1, 6, 1, 1 events of ranks 1..6, mass 56), and `check.py` takes helpers (credit) only from public endpoints: dim(final) - dim(initial) with an exact identity row. An owned register is never an input,
earns no target, and is cleared (owned_erasure) before return, so a rise creates no credit and cannot fake an independent field. The stream replay in `physical.py` executes all 23 rises through the compiled chart changes.
The compiled rank equals |delta dim| for every distinct chart pair of this word under the predecessor native compiler (2964 pairs, run separately, not part of the replay budget here).

## Precedent (read at the base commit)
* `research/kappa-rebuild/complex/native_extensions.py:126`: `N.need(spaces[old] < spaces[new] or spaces[new] < spaces[old], 'Nested center transport')`, while public climbs on line 123 must ascend (`'Ascending borrowed climb'`).
* `research/pooled-native-hosting-admission/NATIVE-ADMISSION.md:249`: "An owned centre copy, its complete descending/ascending child path and its clear therefore realize exactly the emitted common-label centre macro."
* The vendored main native (`research/direct-mixed-flow/vendor/THREE-base-FULL-IDENTITY-NATIVE.json.gz`) has 16 owned centre transports per call in each orientation (8 of rank 3, 8 of rank 5); forward they descend 8 to 3 to 0, and the backward orientation traverses them the other way.
* `notes/copied-centers-lemma.tex:58-62` and `:71`: in the reverse complementary orientation the copy is transformed up by rank r, "These are the same charged ranks, implemented by the retained forward/inverse residual interface." That text covers a copy started by COPY; this word accumulates by ADD into a fresh owned register before it rises, so A6 goes further than that text.
* #2479 (merged 2026-10-15): "Equal native rank mass does not admit these changed lifetimes to the original pure-copy storage/owner bill." Changed owned lifetimes were merged as exact finite work with the owner contract flagged; this package states the same.
The compiler text (#4268) is not available here and was not checked.

## Direction-based lower bounds are scoped, not global
These results assume that owned registers only descend and are not valid against a word that uses A6: the owned-paid-56 floor of #6315 (Lemma S: "public ascents shrink C^perp for free, owned descents grow it at their price"),
the eight-unit relay floor of #6229, the reader-497 cache floor of #6257 (descending owned caches; ascending carriers outside its scope), and the surplus accounting of #6831 ("public registers only climb and private registers only descend", surplus -(16p + O)).
#6881 states that ascend-only public paths are verifier behaviour; its bound S <= sum(L_p - 1) - sum c_j takes c >= 56 (H6), which is the owned-descent floor and is scoped the same way.
