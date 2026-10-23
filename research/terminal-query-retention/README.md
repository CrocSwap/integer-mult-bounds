# Terminal-query retention for the complex supplier

This research-only patch gives a conditional composition of PR233's complex
flow with the PR209/234 five-stage architecture retained in PR244. The key
interface change makes each of 22 terminal center queries one existing dirty
coordinate, using eight additions, then delays its already-paid final climb.
It adds no dirty slots or recursive calls. Arbitrary dirty values are restored
by the new inverse cleanup.

The complete complex moment supports `a=754736418878859/10^18`, versus
`747454944651775/10^18`: approximately **0.97417% greater saving**.
There is **no assembled κ improvement**; the contemporary bit supplier binds.

Read `CONSTRUCTION.md`, `LEMMA.md`, `SAME_FRAME_EXTENSION.md`, and
`INDEPENDENT_REVIEW.md`. This is a constructive mathematical argument with
compositional exact checks, not an upstream-parser-admitted supplier, a fresh
Lean theorem, or a monolithic global all-column replay. The inherited
five-stage geometry, phases, compiler, routing, precision and analytic
interfaces remain explicit dependencies. The old `profile.json` status records
the initial prospective-pricing stage; the subsequent construction and review
are in the documents, not inferred from that numerical receipt.

## Portable checks

Run from this directory with Python3, without `-O`:

```sh
python3 -B verify.py
python3 -B verify_query_retention.py
python3 -B two_port_screen.py
```

The first command checks the 22 selected exact fresh-query identities, all198
local dirty columns, literal pivot gates, inverse identities and strict
rational moment bounds. To bind selected inputs to the full independently
regenerated upstream flow as well:

```sh
python3 -B verify.py --flow /path/to/flow.witness.json
```

`CONSTRUCTION.md` records full-round workspace reproduction commands. That
larger checkpoint, including the unchanged upstream regeneration, allocator,
source-K splice and finite-bill scripts, is retained separately; this small
patch does not pretend that its portable local check reproduces those stages.

## Provenance and scope

Pinned main: `3b6b66891c0ac888521cf591fe306c6286601d4f`.
PR233: `109a857a329d18ed5552d5573f17ddfa886ae57f`.
PR244: `a568d94f941929232ab393c7d33dc5a30e017892`.
Detailed source hashes are in `SOURCE.json` and the preserved receipts.

The paired-cube helpers and moment machinery are upstream work, including
icekylinx, eumemic, Avi Eisenberg, Chafik Boukhalfa, Jacob Sussman and the prior
contributors credited by PR233/234/244. `moment.py` is copied unchanged from
PR244's `research/five-stage-source527-banks/moment.py`; Apache-2.0.
The new terminal-retention construction, coordination and independent tests
were developed for SovereignSteak with substantial OpenAI Codex assistance.
The elementary linear-algebra lemmas are not claimed as novel mathematics.
Publication-level novelty of this particular application remains unresolved.
