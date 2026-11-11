# Fixed destination-chart span ceiling for the retained BIT word

The exact 2,871-arrival census finds zero native paid MOVEs that can be
replaced by local XOR using only the already-live original rows in the
destination chart. An independent replay verifies a separating
GF(2) dual at every arrival. With the complete original 36-copy bill,
the savings upper is zero. Conditional κ is unchanged.

## Replay

From a clean repository checkout with CPython 3.12 and assertions enabled:

```sh
python3.12 -B scripts/research_package.py --package research/bit-destination-span-bound
```

From this directory, the standalone replay also works without Git, network
access or an earlier research checkout.

```sh
python3.12 -I -B replay.py --controls
```

The verifier authenticates two exact bundled inputs. It reconstructs all
2,871 original arrival spans and independently verifies the ordered duals,
literal endpoint and complete directed price. Mutated source, forged
membership and an incomplete cap exercise the failure paths. See
[Proof](PROOF.md), [census](RESULT.json), [independent audit](AUDIT.json),
and [exact provenance](PROVENANCE.tsv).

## Open next questions

Can changing the chronology of coframed operations produce a different
destination library? First bound a declared whole-word edit family against
one complete signed invoice. Charge the old and new transport, source
preparation, typed contacts, ownership and restoration. A price-clearing
case needs exact arbitrary-input action and full replay before a build.

The original native word and invoice are credited to #7001 and #6726.
The public source copy is pinned through #7289. OpenAI Codex and subagents
materially assisted. [Notices](NOTICE)
