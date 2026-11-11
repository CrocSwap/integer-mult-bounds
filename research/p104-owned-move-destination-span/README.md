# Live destination span bound for paid P104 owned MOVEs

**NO VERIFIED GAIN. Exact conditional κ change 0%.** On the exact
[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) P104
word, at each paid owned MOVE's literal clock, form the bank of other
nonzero rows already live at that MOVE's original destination chart.
The moving row is outside the bank's exact rational span for all 47
MOVEs. The exhaustive census contains 424 donor incidences and has zero
unresolved cases. The compatible paid saving upper bound is exactly zero.

## Price and evidence

The full signed invoice is rebuilt on the exact native word and
17-copy #7113 caller. The replay saves the directed price before
checking donor support. Granting each eligible MOVE deletion once
and all replacement work free gives an initial upper of about
1,778.20218 raw units for 44 sites with two or more donors. All 2,767
exact pairs fail. The 39 remaining sites with three or more donors
give a second optimistic upper of about 1,676.28799 raw units before
the complete-bank test. Exact rational price intervals and the pinned
raw crossing upper are in the [pair price](receipts/pairs/PRICE.json)
and [bank price](receipts/fullbank/PRICE.json).

The [full-bank receipt](receipts/fullbank/SUPPORT.json) gives one
sparse rational separating dual per literal MOVE. Its dot product
vanishes on every available donor row and is nonzero on the target.
The replay verifies those products on the original rows. A separate
denominator-cleared rank implementation independently gives a rank
increase after adjoining the target for every one of the 39 larger
banks. The other eight cuts are independently covered by exact
pair checks and the one-donor or zero-input controls. The
[pair](receipts/independent/PAIRS.json) and
[rank](receipts/independent/BANK.json) receipts record that coverage.
Controls include a combination requiring three donors, dependent
rows, an empty bank, a sign mutation and an outside coordinate.
Both support engines use the pinned exact normalized word interpreter.

The result fixes the literal clock, original destination-chart ID,
original word and live bank. Changed clocks, other charts, cached retired
rows, new paid deliveries, altered ownership and simultaneous word
changes are outside this bound. No physical candidate was built. The
strongest independently reproduced comparable witness remains #7277
at conditional κ = 0.003645669928698.

## Replay

From a clean checkout, use CPython 3.12 with assertions enabled and
the standard library.

~~~sh
python3.12 -B scripts/research_package.py --package research/p104-owned-move-destination-span
python3.12 -B scripts/check_research_commit.py --package research/p104-owned-move-destination-span --check-modes --check-source-history
~~~

For a Git-free export run
`python3.12 -I -B research/p104-owned-move-destination-span/replay.py`.
[PROVENANCE.json](PROVENANCE.json) records exact public commits, paths,
Git blobs and SHA-256 for the word, crossing receipt and caller.
[LOCAL-PINS.json](LOCAL-PINS.json) authenticates the bundled scripts,
dependencies and exact receipts by package-relative paths. No external
checkout, prior temporary state or network fetch is required.

## Predecessors

[#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277) at
`ed090b57ed88f8859e5ff4643645099e6ba856ea` supplies the literal word
and comparator. [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller.
[#6069](https://github.com/CrocSwap/integer-mult-bounds/pull/6069)
supplies the older complex endpoint span precedent.
[#7293](https://github.com/CrocSwap/integer-mult-bounds/pull/7293)
supplies the same-clock destination-bank method on BIT.
[#7165](https://github.com/CrocSwap/integer-mult-bounds/pull/7165)
supplies the earlier complex owned-MOVE donor-route comparison.
[#7307](https://github.com/CrocSwap/integer-mult-bounds/pull/7307)
supplies the direct-deletion baseline on the same 47 moves.
OpenAI Codex and subagents materially assisted.

## Open next questions

Can a changed schedule or a newly paid donor provide a row before the
required read? Pin that changed bank and bound its total compatible
saving across the full signed invoice. A surviving proposal needs
exact physical signed action, ownership and restoration, and all
routing, precision and tape costs charged.
