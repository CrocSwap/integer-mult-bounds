# Pure44 alias and q518/506 kernel composition

This is a **superseded finite conditional construction**, with modern
κ = **0.00169659996105181924736999999999979966068000768963615052600000000004**.
It composes Dugongue's PR2309 pure alias619→530 and owner fill with Jeremy
Kothe's PR2302 q518/506 kernels and frame choices (the kernel shape is
mdumitrean's PR1625). The full source and generators are preserved unchanged
under [`supplier/`](supplier/README.md). Its manifest is
`e1bcf65a27e52767e2f7f4c28b284ff21b4e4f991ba2a1a803617abe49ef3a9a` (479 files).

The added result is their actual chronological composition: matching common
gates, transporting eight insertions and two deletions into the pure44 word,
preserving the alias-specific monomial map, transporting the other 43 warp
frames, and deriving the entire inverse-reverse cleanup. The portable producer
recovers both credited predecessor controls before auditing the new words.
Matching rank profiles alone would not establish this compatibility.

## Result and evidence

Both providers have local paid profile `{1:2341,2:505,3:420,4:124,5:42,8:8}`,
mass 5381, 436 public helpers and 76 private FULL cleanup buffers. All 666
hosted calls use the extra provider. The complete global profile is
`{1:1582416,2:336330,3:288393,4:82584,5:29451,7:148,8:5328,14:1,48:24479}`:
mass 4,816,512, 66,304 live fields, 66,826 physical fields and 290,376 hosted
roles. The row coefficient is 19,545 below the retained 20,161 guard.

Relative to the pinned PR2309 invoice the profile changes by
`+1332 C1 -2664 C2 +1332 C3`. Strict concavity gives `1+3^p < 2*2^p` for
`0<p<1`; positive-child count and rank mass are unchanged, so the conservative
per-child surcharge cancels. The modern κ improvement over that pinned claim
is about `8.48368e-8`. Exact proof, values and inherited assumptions are in
[`supplier/PROOF.md`](supplier/PROOF.md) and the frozen source.

[`evidence/RESULT.json`](evidence/RESULT.json) records complete finite admission
of this exact manifest. The accompanying release, supplier, native, assembly,
invoice, hosted-owner and bootstrap receipts record their own coverage.
The bounded hook freshly rebuilds both words and rejects eight targeted
kernel/alias/cleanup mutations. A full cold replay separately checks native
transport and phases, the literal owner invoice, strict supplier and modern
outer admission, hosted-owner binding and the ordinary bootstrap.

The frozen inner README predates the final runtime and deliberately treats its
numbers as expectations; the source is not edited retroactively. The external
receipts and this publication note supply the completed execution status.
Predecessor receipts remain historical and do not admit the new words.

## Latest-source comparison

The submission review refreshed upstream main and searched all open PR bodies,
including drafts, and paginated discussion bodies, comments and replies.
[`OVERLAP.json`](OVERLAP.json) records coverage, exact heads and limitations.
This is a bounded overlap review, not a novelty proof.

[PR2312](https://github.com/CrocSwap/integer-mult-bounds/pull/2312) and its
successors already claim stronger values using a different width exchange.
[PR2474](https://github.com/CrocSwap/integer-mult-bounds/pull/2474), pinned at
`5298f86c5193db65f869121eab3cac16d557196c`, claims approximately
`0.001703676387993676489034`. Its actual words already contain the identical
q518/506 gate edits; PR2322's coherent handoff has already removed helper619,
and lender530 serves helper651. Applying our target deletion again cannot
remove an additional helper. Our verified improvement must not be added to
that claim. No universal obstruction to future rescheduling is asserted.

The minimal pinned comparison inputs under `comparison/pr2474/` and
`verify.py` reproduce these structural facts in both orientations. This is
not complete verification or adoption of PR2474. The selected record is
unchanged. The contribution preserves a distinct composition, its portable
producer and reproducible evidence, without claiming a new leading bound.

## Packing cap

The paid-profile relaxation in
`research/complex-local-word-ceiling/ceiling.py`, at dimension73, 66,304 live
fields, 666 calls, centre mass64/call and idle rank≤51, gives
`a < 0.001728266380383`. The modern outer satisfies `κ<a`, so this also bounds
its κ and the composition realizes about **98.167735%** of that cap.
[`evidence/PACKING-CAP.json`](evidence/PACKING-CAP.json) supplies the exact
directed bracket and rational ratio. The tool's historical `a/(1+a)` conversion
belongs to an older balanced outer reduction; it is not used for this modern
outer. This cap fixes the local profile, coverage law and idle-rank guard.

## Reproduction

The bounded registered hook uses the Python3.12 standard library on Linux:

```sh
python3 scripts/research_package.py --package research/t74-pure44-kernel-composition --check-only
python3.12 scripts/research_package.py --package research/t74-pure44-kernel-composition
```

It checks frozen bytes, receipt/value bindings, the latest-source structural
comparison and exact cap, then freshly rebuilds and audits both composed words
with meaningful rejecting controls. It also checks the additive centre-to-target
cut guard from [PR2478](https://github.com/CrocSwap/integer-mult-bounds/pull/2478),
with two rejecting cut mutations per provider. The full native replay also
covers the interface that motivated that audit. The hook does not replace
complete cold admission.

Full replay from the repository root, with an external output path that does
not already exist:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -I -B \
  research/t74-pure44-kernel-composition/supplier/verify_package.py \
  --out /absolute/new/composition-cold
```

[`evidence/ENVIRONMENT.json`](evidence/ENVIRONMENT.json) records the tested
Linux interpreter, dependencies, command and cold/reuse status. Native replay
is fresh by default. Optional `--native-cache` reuse must pass the retained
source-bound binder; it is not needed for the documented cold run. No historical
selected-record suite was rerun because this PR changes no selected inputs.

The all-size compiler, fixed-tape realization, precision, recovery, analytic
transfer, bit-supplier and modern-outer interfaces remain inherited conditions.
Finite certificate success is not an unconditional multiplication theorem,
full Lean reflection, or independent human review.

## Open next questions

An independent review of the chronological transport and inherited physical
hosting/outer interfaces would strengthen assurance; begin with the two exact
rebuilt words, rejected mutations and source-bound native receipts. The blocker
is independent mathematical review, rather than another numerical κ search.
Any future attempt to improve the latest supplier must start from its actual
handoffs and frame schedule and price a fresh complete invoice; helper619 and
the q518/506 kernels cannot be counted twice. Structured details are in
[`TASK.json`](TASK.json).

## Credit

Prepared for Marius-Paul Dumitrean (`mdumitrean`) with substantial OpenAI Codex
assistance in construction, validation and writing. Dugongue/PR2309 supplies
the pure44 alias, exact fill and private-buffer accounting; Jeremy Kothe/PR2302
supplies the two kernels and frame refit, using mdumitrean/PR1625's kernel
shape; Cinna Davis (`1337isnot1337`)/PR2226 supplies anticipatory dirty borrowing.
The retained supplier, audit, outer and source-specific notices preserve the
full predecessor attribution. Comparison excerpts credit Jeremy Kothe/PR2474,
Vlado Vojdanovski/PR2322 and tekuuu/PR2436, with their retained NOTICE.
New work is Apache-2.0; all retained source licenses continue to apply.
