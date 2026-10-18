# One-factor stock at the ordinary recursive backend

PR2899's ordinary wrapper can consume PR3246's smaller NODE-guard stock,
**conditional on the retained completed-caller and physical-cost contracts**.
This package supplies an opt-in encoded selector, traces both padded calls
and returns, and keeps the full recurrence and ownership bill explicit.
It changes no predecessor, shared backend, selected certificate or exponent.

For fixed original width e and atom width w, put d=D(e), b=28416 NH and Q=9475.
The new selector uses `Q*b^d` at positive depth, instead of `(Q*b)^d`; at
depth zero it uses 1. The exact divisor saving `Q^(d-1)` is **Nick Petalas's
PR3246 result**. The contribution here is its source-bound connection to the
actual ordinary consumer, an executable encoded adapter, and the reduced
return evidence. It is not a measured runtime or total-memory reduction.

The old dual full-depth-format promise is stronger and still needs its old
reserve. This package explicitly narrows to the actual NODE guards. It does
not make that format conversion free or remove any private buffer.

## What is connected

- The selector retains PR2899's original-e width and depth choices, computes
  the least covering radix power, then recomputes the strict fit test and
  body/remainder split. Every old fitted width remains fitted.
- `Ordinary.fitted` pads each call to a multiple of the supplied stock and
  restricts it immediately afterwards. Its gap keeps the genuine high-field
  range. Both calls reuse the reserve and preserve every row ordinal.
- The source recurrence, all recursive children, scalar operations, source
  access, routing, frame changes, restoration, output disposal and setup
  remain charged. The inherited ordinary rate is unchanged.

The [proof](PROOF.md) states the all-domain implication and its assumptions.
The [adapter](selector.py) uses only inherited Count operations for
input-dependent arithmetic. In an already initialized PR2899 source namespace,
the opt-in call is:

```python
engine.execute_plan(payload, original, prefixes, gap, suffix,
                    lambda: select_guard_stock(original, engine.q))
```

This is for the selected W=28416, Q=9475 NODE-guard contract with unchanged
source/callee premises. Do not use it for an arbitrary binding or a consumer
requiring both old depth formats. No default engine is patched.

## Reproduction and exact scope

Base: `463113d 675af 7410ac 91d 53a 4fed 51ec 6494eb 9a`, priority revision 6.
Main dependencies: PR2899 `2f 0911ad 735643a 069b 9790302fbf 179e 49f 74f 8`,
PR2809 `e 7d 93dd 0de 0bb 81308bc 3356f 65eddeeb 22fd 712`,
PR2753 `7dba 5452a 4071a 856a 0b 11cebdcd 2d 3b 6bcd 7659`, and
PR2808 `b 00b 58e 0db 823643364f 705b 530faac 254e 7b 05b`.
The pending proof dependency is PR3246
`4b 9a 993d 90f 2b 49d 9217ab 46cb 6daaba 194b 53f 4`;
[PREDECESSOR.json](PREDECESSOR.json) authenticates its byte-exact proof export.
[SOURCES.json](SOURCES.json) pins all imported sources and their external inputs.

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/ordinary-one-factor-stock
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE` after setup, nested return,
wrapper return and rejection controls. Replay compares [RESULT.json](RESULT.json)
without regenerating it. Direct checks also work in a complete committed
source export:

```sh
python3.12 -I -B research/ordinary-one-factor-stock/verify.py --suite setup
python3.12 -I -B research/ordinary-one-factor-stock/verify.py --suite nested
python3.12 -I -B research/ordinary-one-factor-stock/verify.py --suite wrapper
python3.12 -I -O -B research/ordinary-one-factor-stock/test_verify.py
```

The bounded evidence separates three questions:

| Check | Coverage and limit |
| --- | --- |
| Encoded selection | Two reduced dimension/rank profiles, q=2/3, Q=1/2/5/9475, e=1/2/4/24/32/127; every output Count matches a separate integer specification. Not full selected GL64/large-prime encoded execution. |
| Actual recursive return | Q=2, b=6, depth 2, 72 fresh rows instead of 144; all 18432 bits of one row-sensitive payload, 12 actual child calls/returns, 156 residuals, borrowed input and final cleanup. Not an all-input or GL64 proof. |
| Actual outer return | Manual fitted q2/dimension 2 plan with stock 12, genuine 16 and padded 24 rows; all 4096 independent input columns through both 6144-bit padded returns and final ordinary permutation. No recursive child in this separate fixture, and no claim that full selected setup generated it. |

The exact finite census also checks 866320 guard decisions,7000 padding/depth
contracts and 169386 selected-rank depth inequalities. Its domain and stopping
rule are fixed in code; it is not a search for a better exponent. The seed 55
assigned the recursive-interface track; deterministic coverage is not sampled.

Controls distinguish a first-level guard from recursive admission, omitted
compatibility, stale fit/body decisions, the stronger old-format requirement,
source/proof corruption, invalid noncontracting profiles, typed receipt drift
and unsafe output overwrite. Reused PR2899 controls check archive corruption,
borrowed leases, forbidden allocation and wrong equal-valued affine origins.
No finite pass is represented as a formal proof of the full theorem.

## Open next questions

1. Independently review the extension of the completed C0 primitive and
   cost/reserve premises to this guard-admitted domain. Start at one concrete
   selected route/weighted leaf and retain all payload/spectator coordinates;
   the source-wide PR2809 scientific review remains open. This is required
   before changing a default backend, even though a source-level composition
   and small executable fixtures are available.
2. Bind a later bootstrap consumer's **actual** required format before reusing
   this selector there. Locate a P-based depth divisibility test or prove it
   absent; a dual-format consumer requires `Q^(d-1) | t` for rows `t*S_d`.
   Do not infer a numerical selected-stage coefficient from this local lemma.
3. Implement and price a complete selected large-prime consumer with this
   reserve. Start with the unchanged source recurrence and every physical
   cost term in PROOF.md; the present small payload replays cannot establish
   that implementation or a practical speedup.

## Credit and provenance

Tekalign (`tekuuu`), with substantial OpenAI Codex assistance in derivation,
implementation, checking and writing. Apache-2.0; no independent human review
or formal-kernel verification is claimed.

Nick Petalas supplied PR3246's one-factor theorem, PR2120's depth bound,
PR2808's outer wrapper, PR2989/3041's compiler-interface audits and the explicit
handoff. Jose Manuel (`jmbarrancoml`) supplied PR2899, PR2809 and the retained
stock/compiler lineage. David Arias supplied PR2753's logical recursive caller.
Ross Richardson supplied PR2420's live/physical format distinction. Adam Gall
supplied PR2084's conditional parent reserve. The concurrent PR3223 by
commdata 2338 separately audits NODE/peel/return under primitive premises; this
package does not claim that audit or repeat its full coordinate census.

The source fixtures, affine provenance and failure controls retain their
PR2899/2809 authorship. Credit the PR589/555/source527 geometry, hosting,
coefficient and compiler lineage, including DreamingOfClouds and eumemic;
selected assembly credit remains with Rohan Arun, Jeremy Kothe and their
predecessors. All original archives and notices remain unchanged.

Task selection, prior coverage and remaining obligations are in [TASK.json](TASK.json).
Of three candidates (this junction, QQ16 dirty restoration, weighted-leaf
refinement), this takes the new released handoff rather than extending a static
search. Entry metadata covered 301 open PRs,2630 closed PRs and 2076 Discussion
records; one initial open-PR refresh timed out and was replaced by the complete
301-PR fetch. Targeted #2319/#2612 reads and PR3246's body were also checked.
The final 19:49 UTC search covered 309 open PR titles/bodies and the nearest
claims, with unchanged main and PR3246 head. These searches omit arbitrary
diffs and unpublished work and are not a novelty certificate. [VALIDATION.md](VALIDATION.md) records final checks and limitations.
