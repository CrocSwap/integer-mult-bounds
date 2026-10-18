# P112 cross forms: a Schur rank tradeoff and formal COPY-floor interface

Two independent P112 root-code decoders still require **COPY cost 128**
under a broader class of arbitrary cross-call binary forms. If their global
ranks are r01,r10 and their minimum support-restricted ranks are c01,c10,
the sufficient condition is

    c01 + c10 >= min(8, r01, r10).

This follows by charging a term touching both calls at least
`16-min(8,r01,r10)`, then using the exact coefficient identity to count
terms. The [written proof](PROOF.md) and [Lean count theorem](CountFloor.lean)
state the different evidence boundaries explicitly. This is a COPY-rank-sum
floor, not a physical supplier, rank-power moment bound or new kappa.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Scope and result

The model is PR2294 section 4: arbitrary directed cross forms on two copies
of a nine-dimensional binary space, unchanged within-call P112 pairings,
any finite number of complex root-code factors, and separate-total union
rank prices. The union pairing need not fit a single nine-dimensional table.

The rank-only sufficient test
`max(0,r01-2)+max(0,r10-2) >= min(8,r01,r10)` covers **93 of the 100 ordered
global rank pairs** in `0..9`. It covers every pair with maximum at least
four and every pair with a zero rank. Seven low-rank pairs remain undecided
by that test; they are listed in the proof and RESULT.json. They are not
claimed to admit savings.

PR2294's form-specific sufficient condition requires `c01+c10>=8`; its
rank-sum-at-least-12 corollary covers 28 global rank pairs. This package
strengthens those tests. Its explicit rank-(4,4) example has support minima
(3,3), so the old test fails while the new test proves the exact minimum
128. Sixteen within-call coordinate terms attain 128 for every cross form.

## Evidence and reproduction

From the repository root, Python 3.12, standard library only:

```sh
python3 -I -B scripts/research_package.py --package research/p112-cross-form-rank-tradeoff --check-only
python3 -I -B scripts/research_package.py --package research/p112-cross-form-rank-tradeoff
python3 -I -B research/p112-cross-form-rank-tradeoff/test_integrity.py
```

The registered replay independently constructs the Hamming-shell root set,
checks 12,544 label pairings, both 511-functional support censuses, all 64
within-call support ranks, 9,216 small block matrices and 505 exact decoder
cost fixtures. Eight mathematical controls reject weakened hypotheses.
A deliberately degenerate rank-(1,1) example makes the criterion abstain;
finite decoders tested there do not decide its unrestricted minimum.

Expected marker:

```text
PASS_P112_CROSS_FORM_RANK_TRADEOFF ranks=93/100 blocks=9216 decoders=505 controls=8 abstentions=1
```

The five coefficient identities are checked in dimension 16, which is
equivalent to all 224-by-224 scalar demand entries because the source-bound
root matrix has an explicit left inverse. Binary term costs are computed
on actual support spans, preserving matrix rank. No predecessor verifier is
imported. Replay compares every structured RESULT.json field and preserves
explicit checks under `python -O`. Typical local replay is a few seconds.

Separately, use **Lean 4.21.0** with its bundled core libraries;
Mathlib and Lake are unnecessary:

```sh
lean +leanprover/lean4:v4.21.0 -j1 research/p112-cross-form-rank-tradeoff/CountFloor.lean
python3 -I -B research/p112-cross-form-rank-tradeoff/check_lean.py --lean /path/to/lean
```

The second command requires the selected executable to report 4.21.0. It
builds three theorems, checks four concrete counterexamples and rejects four
false proof files. Their axiom audits list only `propext` and `Quot.sound`.
The registered Python replay does **not** build Lean; its pass is finite
certificate evidence only. The complete matrix/rank proof is written,
not kernel formalized. Local checks are author checks, not independent review.

`--write-result` on verify.py regenerates RESULT.json for intentional updates;
ordinary replay is read-only. Source and predecessor pins are in SOURCES.json.

## Task, overlap and attribution

Task `formal-interface-lemma`, refined to the rank-price/count interface;
the full card is in [TASK.json](TASK.json). The claim is in
[Discussion #2372](https://github.com/CrocSwap/integer-mult-bounds/discussions/2372). Base:
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.

* Sagar Thakrar (@thakrarsagar), [PR2294](https://github.com/CrocSwap/integer-mult-bounds/pull/2294),
  head `18d6ac4f864af2b71aa8cf5f4541fcfc4350e2f0`, supplies the arbitrary
  cross-form model, support premises, original count argument, weaker
  sufficient conditions and the open question. Its proof is retained verbatim
  under sources/ with its credit and Apache-2.0 notice.
* Alephnan's PR1714 supplies the root-code batch model; Mihir Srivastava's
  PR845 and Adam Gall's PR1098 supply the support-lemma lineage. The fixed
  main-branch P112 single-lift geometry is an immutable input.
* DreamingOfClouds' [PR2338](https://github.com/CrocSwap/integer-mult-bounds/pull/2338),
  head `82700676e1d42acf98dc1921cb6ef82551620008`, proves related batch floors
  with a single rank-nine label table. Its text is pinned for scope comparison;
  none of its SAT results is a premise of this proof.

The new contribution is the minimum-of-cross-ranks Schur price, its coupling
to the prior complex count argument, the expanded sufficient region and the
kernel-checked conditional count interface. It does not re-claim the original
128 isometric-chart floor. All new work is Apache-2.0. Substantial OpenAI
Codex assistance was used for derivation, implementation, checking and writing.

## Open next questions

1. Decide the remaining rank pairs (1,1), (1,2), (2,1), (2,2), (2,3),
   (3,2), (3,3) when the actual support minima fail the new criterion.
   A small first step is to classify which of the eight hyperplanes kill
   each rank-one form. This matters because this proof leaves exactly that
   low-rank source of possible sub-128 behavior; coefficient identities
   and per-term support restrictions still have to be enforced jointly.
2. Formalize the matrix-to-count premises. Start with the 16-by-16 block
   Schur bound over F2 and C and then the support classification. This would
   reduce the current written-proof boundary; the Python census and the
   natural-number theorems alone do not formalize those implications.

No physical implementation or additional construction search is justified
by this sufficient-condition result alone.
