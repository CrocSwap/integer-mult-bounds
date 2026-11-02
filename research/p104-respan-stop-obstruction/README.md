# One-step helper respanning cannot unlock a single P104 stop deletion

This package proves a new scoped obstruction for the exact word of
[PR6345](https://github.com/CrocSwap/integer-mult-bounds/pull/6345).
Even if all 42 one-step helpers may change both endpoint subspaces at once,
none of its 2,660 intermediate stops can be deleted while all other epochs
outside those helpers retain their frames and the scalar schedule is fixed.
The count includes 2,654 public stops and six owned stops.

Every stop has an explicit ADD/COPY contact with another register whose epoch
stays fixed. That contact forces the original intermediate frame to be visited.
[PROOF.md](PROOF.md) states the exact model and proves the implication.
This is a scoped proof with a finite structural certificate. No new kappa is
claimed, and the selected frontier is unchanged.

This extends PR6345's second Open next question. The predecessor establishes
price-null helper freedom; the new step is an obstruction to using that freedom
alone to remove one stop elsewhere. Existing word legality, native operators,
invoice and supplier assumptions are premises, not review deliverables here.

Ali Romman's [PR5590](https://github.com/CrocSwap/integer-mult-bounds/pull/5590)
already proves a price floor for the older PR5580 word when every scalar contact
frame is fixed. Here contacts involving freely re-spanned helpers may change
charts. The new certificate finds a contact with a fixed partner at every
candidate stop of the different PR6345 word. The common-chart equality itself
is an inherited rule, not a new general theorem.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-respan-stop-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/p104-respan-stop-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-respan-stop-obstruction
```

Expected: `PASS_P104_RESPAN_STOP_OBSTRUCTION`, 2,660 stops, 42 free helpers,
ten semantic rejections, two positive toy controls, and
`PASS_REGISTERED_RESEARCH_PACKAGE` from the registered runner.

Pass `--receipt /absolute/path/outside/checkout/receipt.json` to the direct
verifier to save every contact witness with source and package file hashes.
The verifier generates this receipt; no retained receipt is required.
In a sparse checkout, materialize
`research/p104-frontier-symmetric-ladders` first.

## Scope

The helper MOVE positions, scalar operands/order and all non-selected epochs
outside the one-step helpers stay fixed. The merged transport replacing the
selected stop may be placed at any intervening cut. The proof allows arbitrary
new helper endpoint subspaces, including ones absent from the native catalogue.
It rules out this local move before pricing or native synthesis matters.

Coordinated changes to multiple epochs outside the one-step helper set,
changed scalar schedules, additional transports and other words remain open.
The package does not
classify optimal frame assignments or prove a global price ceiling. The five
inherited framework assumptions remain. Full native, caller, compiler, rounded
execution and all-size replays are outside this obstruction's claim and were
not run. [VALIDATION.md](VALIDATION.md) records checks and implementation bounds.

## Open next questions

- Can changing a blocking partner epoch together with the selected stop admit
  a legal two-register deletion? Start with one generated contact witness and
  trace the partner's other contacts. Full frame legality, productive target
  changes and the complete signed bill are unresolved.
- Can moving one helper's unique MOVE across scalar contacts evade the fixed
  schedule obstruction without adding paid work? Start with an explicit
  reordered scalar program and preserve every arbitrary public input.
  Chronology, restoration and full pricing are blockers.

The structured versions are in [TASK.json](TASK.json).

## Credit and coordination

The new obstruction, proof and verifier were produced by Nick Petalas.
The input word, price-null freedom and open question are DreamingOfClouds's
PR6345. Its predecessor is Ali Romman's PR6167 retained-operand construction
over DreamingOfClouds's PR6144/PR6143 and the retained P104/native/caller lineage.
Their source files and credit remain unchanged. No predecessor implementation
is imported or copied into the verifier. All new work is Apache-2.0.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19358834).
