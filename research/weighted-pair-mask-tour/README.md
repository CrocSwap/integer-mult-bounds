# Exact weighted borrowed-source pair tours

Scoped proof with finite corroboration. For n >= 2 toggle sources and
positive prices sorted c1 >= ... >= cn, the minimum closed anchor tour
through every pair mask is

    2c1 + 2 sum_(i=2)^n (i-1)ci.

The optimum permits arbitrary intermediate masks and repeated visits. A
simple pair ordering attains it. Each dirty target is written once from the
borrowed source at its designated parity; all source rows are restored.
The [proof](PROOF.md) states the exact operation alphabet and lower bound.
This contribution is produced by Nick Petalas.

For four toggle sources, unit prices and two targets per pair, the complete
map takes **26 row ADDs versus 36 direct ADDs**. This includes 14 anchor
toggles and 12 target writes. At row width L, it costs 26L rather than 36L
bit XORs. Unequal prices (7,3,2,1) give an exact transition cost of 34.
The optimization is within one-anchor schedules, with no other source
mixing and one write per target. It is not a global CNOT optimum.

## Relation to prior work

Cinna Davis's merged [PR #2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271)
introduced the borrowed-source mask-tour boundary, shared transitions,
exact restoration and a four-edge square example. Its Open next question 2
asks for shortest tours through larger specified mask families. This result
answers that question for all two-element masks, with positive unequal
prices and an all-n minimum. The predecessor's example and verifier are
not replayed or claimed as new work. Its README is pinned as provenance
in [SOURCES.json](SOURCES.json). No predecessor code is imported.

The `bit-helper-contract` assignment changes scope from R439 H2/K to this
explicit local row-register interface. This is a side result for shared
parity delivery. It does not discharge an R439 replacement lemma. Selected
κ=0.00302015 and all frontier files are unchanged. Native realization,
frames, actual caller occurrence, hosting, tape movement and recursive
charges remain unknown. No supplier or κ improvement is claimed.

## Reproduce

From the repository root with CPython 3.12 and standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/weighted-pair-mask-tour
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/weighted-pair-mask-tour/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/weighted-pair-mask-tour/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/weighted-pair-mask-tour --check-source-history
```

Expected direct status is `PASS_WEIGHTED_PAIR_MASK_TOUR`. The independent
permutation oracle and the literal hypercube-state oracle optimize different
state spaces. The latter permits off-layer masks and repeated visits.
Exact basis columns, complete one-bit dirty states and 73-bit row fixtures
check the output map and restoration. Controls reject bad prices, incomplete
tours, wrong visits, malformed row references and altered circuits; a legal
expensive order distinguishes price priority from feasibility. Every runtime
check remains active under Python optimization.

The optional `--receipt NEW_PATH` creates a generated receipt after success,
bound to SHA256 hashes of the package files. It refuses an occupied path.
Normal verification writes no file and requires no Git, network or external
package. The mathematical theorem permits all n and positive real prices;
the constructor is bounded to n<=64 and rational prices, the full circuit to
at most eight targets per pair. Finite oracle domains are explicit in code.

## Open next questions

- Find one actual aligned caller requiring all pair parities at the same
  cut. Begin with its exact source/target demand and frames, then price
  references, restoration, physical storage and tape movement. Without a
  caller there is no claimed supplier consequence.
- If a caller needs only a subset of pairs, determine its weighted optimum.
  Start with that actual demand graph. The complete-pair forest bounds used
  here need not be sharp after pairs are deleted.

## Scope and credit

The base is canonical main `624de9dc66858af0945e5f8a0942488d62280d43`,
priority revision 7. The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134289)
records the exact question. Open PR bodies, recent account contributions,
current handoffs, main README terms and merged PR searches were consulted.
The cached scan covered 412 open PRs and 3,928 Discussion records at about
23:07 UTC on October 22, 2026. Sparse local-note coverage was incomplete;
main Git searches supplied separate object/formula checks. These searches
exclude unpublished work and do not prove novelty.

Cinna Davis retains credit for PR2271 and its predecessor lineage. General
weighted Hamming metrics, shortcutting, forest edge bounds and dynamic
programming are standard tools. The new theorem, constructor, written proof
and independent finite oracles are produced by Nick Petalas. Independent
human and formal proof-kernel review are unclaimed. Apache-2.0.

The Python code uses bounded source/gate domains, finite oracle state spaces,
explicit exceptions and direct calls without recursion. Python and its exact
arithmetic libraries allocate dynamically; the bounded verifier is not a
fixed-allocation implementation. Large-number bit complexity is not bounded
by the row-count limits. Warning-strict normal and optimized replay provide
the available interpreter diagnostics; no whole-repository linter or formal
kernel check is claimed.
