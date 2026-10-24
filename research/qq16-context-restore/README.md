# QQ16 Context restoration in finite metadata handles

The literal `Machine.restore_context` now has an executable source-specific
metadata constructor. It allocates the actual five-object Ring/Unsigned/Context/
Count/Program graph, preserves its field order and shared references, and safely
reuses records after replacement. With one held prior pair, **15 dynamic records
suffice for arbitrarily many restorations**. The fixed source boundary is an
explicit input contract; this result does not construct the whole QQ16 frontend.

This answers a bounded part of [PR5330](https://github.com/CrocSwap/integer-mult-bounds/pull/5330)
Open next question 1 and the
[released Context lifecycle handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19151254).
[The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19152880)
records the narrower scope. PR5034 bounded completed-return graphs and supplied
a source shape control; PR5330 implemented adoption while leaving Context
construction open. This package adds the restoration constructor, its transient
lifetime proof and a complete charge for this metadata operation.

[PROOF.md](PROOF.md) gives the precise boundary and refinement argument,
record bound, padded-scan tariff and remaining obligations.
[constructor.py](constructor.py) takes fixed slot/configuration handles, not a
runtime object-id table or supplied adjacency graph. It retains the numeric-leaf
quotient and sequential-store model of the credited predecessors.

## Exact corroboration

[verify.py](verify.py) executes the unchanged selected source ASTs and actual
Count inheritance chain from the pinned nested archive. It independently
compares types, ordered attributes, every reference, identity sharing and the
literal `owned_tapes` output after gluing the same fixed boundary.

- 864 restorations: all 108 five-slot tuples twice in each of four sessions.
- Plain and cyclic/shared fixed boundaries; omitted codebook Tape preserved.
- Actual 16-bit and 4096-bit source word buffers give identical metadata receipts.
- A held old pair survives 108 later restorations; peak 15 dynamic records,
  10 retained after collection, with safe address reuse.
- Borrowed contents, heads, meters and live sets are unchanged; final owned
  metadata is erased.
- Ten rejecting controls cover lost Tape/raw/word aliases, mutation or premature
  retirement of old objects, excess retention, borrowed disposal, bad slots and
  uncollected history.

These slot tuples test a complete finite **structural** domain, including aliases;
they are not all numerically valid parent frames. The fixed vocabulary and
prebound source objects are fixtures, not a full production constructor run.
The check is author-checked with substantial AI assistance, not independent
human or proof-kernel acceptance.

## Reproduce

From the repository root, Python 3.12 and the standard library suffice:

```sh
python -B scripts/research_package.py --package research/qq16-context-restore --check-only
python -B scripts/research_package.py --package research/qq16-context-restore
```

The registered hook runs normal and optimized Python, each with a 30-second
limit. Expected markers: `PASS_PACKAGE_METADATA_AND_PINS`,
`PASS_QQ16_CONTEXT_RESTORE` twice, and `PASS_REGISTERED_RESEARCH_PACKAGE`.
[RESULT.json](RESULT.json) is the deterministic receipt, including nested hashes.
The direct command for a checked Git-free package export is
`python -B research/qq16-context-restore/verify.py` (also valid with `-O`).
It writes nothing unless explicitly called with `--write`.

## Limits

The current frontier remains governed by `certificates/selected-result.json`;
there is no supplier admission, new kappa or multiplication-theorem claim.
This is inventory metadata, not numerical `new_context`/`high_count`, header
decoding, physical parking, source compilation, or the full F(K)/D* versus B*
bill. Additional external aliases invalidate the one-held-pair capacity premise.
No complete native controller, selected cold replay, Lean or Docker run is used.

## Open next questions

1. **Lower the real `new_context` path.** This would cover numerical constructor
   temporaries and its highs Count closure. Begin with the actual
   `Context(ring,codes) -> save_count -> count` sequence and its source-defined
   scratch/liveness ledger; numerical source compilation remains the blocker.
2. **Close the actual caller's root contract.** This is needed before using 15
   records as a whole-program bound. Enumerate all live Context/Program aliases
   around `dispatch`, `call` and `complete_return`, including callbacks. A
   completed-return cap alone does not settle intermediate liveness.
3. **Compose this constructor with PR5330 adoption.** Start with a common fixed
   boundary and one restore/adopt/restore sequence; preserve each algorithm's
   paid initialization, collection and inventory charges. Initial boundary
   compilation and the other mutators still prevent a complete F(K).

The source pins and original card are in [SOURCES.json](SOURCES.json) and
[TASK.json](TASK.json). Base: canonical main
`7c472563474e60185e6ca101a17622133d047e56`, priority revision 7. Initial overlap
covered 305 open PR bodies, 4620 Discussion records and all 7267 tracked
top-level note/metadata records, with complete reported pagination. That is
public text coverage, not a guarantee of novelty or coverage of arbitrary diffs.

The final refresh at 2026-10-23 19:18 UTC covered 307 open PR bodies, 4638
Discussion records and all 7267 tracked notes. It found a
[complementary numerical `new_context` scratch/installation claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4744#discussioncomment-19152915),
which explicitly released the overlapping restoration implementation. That
producer investigation is separate; no result from it is assumed here.

## Credit

Prepared by Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex
assistance; Apache-2.0. JoyboyBrian's PR4986/5034/5330 supply the finite-handle
kernel, return-cut bound, adoption frontend and explicit open question.
Chris R/Clear1nsight's caller/adoption and inventory, Jose Manuel's physical
Machine and source constructors, Tekalign's finite-role lineage, Mihir
Srivastava's return obligations, ywz65 and the archived physical/control
predecessors retain credit. The nested archives are used unchanged with their
original notices. No independent human review is claimed.
