# R439 packet updates with one restored dirty bank

The exact 313-event R439 window can use **one borrowed dirty payload bank**
instead of PR2481's two, under the explicit route and synchronized-scan
contracts in [PROOF.md](PROOF.md). Route calls remain **1232**; exchanges
fall **1232 to 626**, and outer packet XOR passes fall **4009 to 2191**.
This is a conditional payload construction and finite exact certificate.
It is not a full supplier, a minimum-bank theorem, or a new kappa.

For an ordinary update, exchange the source into the bank, route it through
the common frame into the target layout, XOR directly into the target's
owned packet, reverse the routes and exchange back. Snapshot taps retain
the predecessor's target-bank protocol so the snapshot stays immutable.
The direct target scan is charged. Original sources may be temporarily
exchanged; continuously immutable-source callers are outside the contract.

The [exact receipt](RESULT.json) covers all 431568 family records in each
direction, 313 event boundaries per direction, arbitrary dirty payloads and
eight semantic faults. A separate mathematical specialist supplies
[an independent audit](REVIEW.md) and small noncommuting-permutation checks.
The route compiler and chronological constructor are reused with credit;
the full finite replay is not an independent implementation of those sources.

## Reproduce

Python 3.12, standard library only, from a complete repository checkout:

```sh
python3.12 -I -B scripts/research_package.py --package research/r439-one-buffer-packet --check-only
python3.12 -I -B scripts/research_package.py --package research/r439-one-buffer-packet
python3.12 -I -O -B research/r439-one-buffer-packet/verify.py
```

The registered replay authenticates retained and live sources, recomputes
forward/inverse receipts and fault controls, then runs the separately written
small oracle. It also rejects corruption of all 15 retained and three live
source files and a changed cost receipt, then checks an optimized read-only,
Git-free export without changing its bytes. Verification does not rewrite
evidence. `--write-result` is an
explicit authoring command that refuses to overwrite an existing receipt.

## Scope and comparison

The all-finite-packet argument permits arbitrary correlated bit payloads and
invertible packet permutations. The concrete replay is GL2(Z/9), with
nonidentity carry-sensitive charts and all unowned records checked. The new
adapter saves one payload bank, 606 exchanges and 1818 outer XOR passes.
Its route multiset is unchanged; equal route work additionally needs a
context-independent role/direction tariff. Head movement is separately
derived in PROOF.md. Header/control work, selector implementation, routing
private scratch and physical supplier admission are not included in those
outer payload counts. The predecessor fresh-copy adapter still uses fewer
route calls (929).

[TASK.json](TASK.json) records the scope change from the drawn bit-mechanism
cards and the live overlap coverage. [SOURCES.json](SOURCES.json) pins live
inputs; [PREDECESSORS.json](PREDECESSORS.json) authenticates consumed retained
PR2481 and PR2448 material before import. No selected record or frozen input
is changed.

## Open next questions

1. Bind one actual selected GL64 route and inverse to all four ordinary-event
   cuts, including arbitrary dirt parked in the source. The blocker is the
   uniform backend and its private scratch/ownership contract.
2. Price a complete caller with the direct owned-target scan, header/control
   restoration, actual route tariffs and borrowed capacity. This determines
   whether the local storage/exchange savings survive physical admission.

## Credit

Ross Richardson, with substantial OpenAI Codex assistance and a separate
AI specialist audit. PR2481 (ywz65, also AI-assisted) supplies the two-bank
construction and immediate source contract; PR2448/2407/2437 (Ross Richardson),
PR2195 (Jose Manuel), PR1627/540 (alephnan) and the original supplier/exporter
lineage are retained in [NOTICE.md](NOTICE.md). The three-XOR exchange and
conjugation identities are standard. The contribution is this changed outer
schedule, its explicit contract/invoice and exact chronological binding.
Apache-2.0; no independent human review or formal-kernel proof is claimed.
