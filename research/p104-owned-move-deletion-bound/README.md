# Direct deletion bound for paid P104 owned MOVEs

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On the exact
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) native word,
consider direct deletion of one paid owned MOVE with the rest of the word
fixed. The two tested cases are an identically zero MOVE input and a MOVE
whose first next same-lifetime contact is CLEAR. All 47 paid owned MOVE inputs
are nonzero as exact normalized rational rows. Each of the 47 MOVEs has an
intervening contact before CLEAR. The stock is empty under both predicates,
so the optimistic paid saving is exactly zero per native call and across the
complete caller. Zero cases remain unresolved in this scope.

## Exact scope and checks

The signed rational replay initializes all public inputs independently and
propagates exact sparse rows through 76,443 literal instructions. It checks
the chart and ownership guards, including the fresh-zero COPY token, and
removes exactly canceled terms. A nonzero input row has at least one nonzero
coefficient and therefore a nonzero response for some allowed input.
The census checks 70 owned lifetimes and 47 positive-rank owned MOVEs.
The paid rank histogram is `{1: 20, 2: 9, 3: 2, 4: 13, 5: 2, 6: 1}`.

A separate forward pass follows each active owned role and records the first
later contact of each MOVE. It counts ADD and COPY sources as reads and tracks
INIT/CLEAR lifetimes separately. The next contacts are 36 ADD source reads,
seven ADD destination contacts and four SCALEs. This independently checks the reverse
next-contact census used in discovery. The controls detect an exact rational
cancellation, reject a changed sign, detect a synthetic direct CLEAR, reject
an intervening ADD or COPY source read, and distinguish a reused owned slot.
[RESULT.json](RESULT.json) and [CONTACTS.json](CONTACTS.json) contain the
deterministic replay receipts.

The fixed-word stock bound covers these two direct deletion predicates.
Changed contacts or lifetimes, broader dead-value analysis after an
intervening write, and a replacement that transports a nonzero field require
separate tests. No physical candidate was built. The strongest independently
reproduced comparable witness remains #7277 at conditional κ =
0.003645669928698.

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled and the
standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-owned-move-deletion-bound
python3.12 -B scripts/check_research_commit.py --package research/p104-owned-move-deletion-bound --check-modes --check-source-history
~~~

A Git-free export can run
`python3.12 -I -B research/p104-owned-move-deletion-bound/replay.py`.
The bundled word is authenticated by SHA-256 and Git blob ID. Its exact
source commit, path and digests are in [PROVENANCE.json](PROVENANCE.json).
No earlier checkout or temporary pointer is required.

## Predecessors

[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) at
`ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the literal word
and complete comparator. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the
signed caller and paid accounting lineage. [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)
previously bundled the identical literal word in a distinct scalar
chronology audit. [#6865](https://github.com/CrocSwap/integer-mult-bounds/pull/6865)
supplies the related owned-exit and lifetime-shortening precedent.
[#5557](https://github.com/CrocSwap/integer-mult-bounds/pull/5557)
supplies the initialized-zero owned COPY and residual precedent.
[#7165](https://github.com/CrocSwap/integer-mult-bounds/pull/7165)
supplies the earlier paid owned-MOVE replacement comparison with donor
routes. OpenAI Codex and subagents materially assisted.

## Open next questions

Can a changed lifetime or consumer graph remove the earliest intervening
contact while preserving the complete signed operator? Start with one exact
owned contact chain and bound the total compatible savings under its changed
contract. A surviving route needs signed forward and adjoint action,
ownership and restoration, and a fully charged caller and tape price.
