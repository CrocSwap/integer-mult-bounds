# Attribution

New experiment, independent Python columns, wrapper, controls and writing:
Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
No subagents or independent human review were used. Apache-2.0.

Compilation reuse is provided by ccache, by Andrew Tridgell, Joel Rosdahl and
its contributors (GPL-3.0-or-later). Ccache is an external executable and is not
vendored or reimplemented. Its manual documents the options used here:
https://ccache.dev/manual/4.12.3.html

The unchanged columns_k.cpp is DaysSky's PR #381 extension of Dylan Crow's
PR #370 / PR #346/#352 native cohort checker lineage. The authenticated
research/e8-bit-carrier-skeleton/NOTICE.md retains the complete predecessor
credit (eumemic, Anthropic Claude-assisted). The accompanying nlohmann/json
header retains Niels Lohmann and contributors' MIT license in its header.

The raw fixtures come from our PR #2373, head
b52f87f5355ad9f02ca4ac4395117655ac1b19c7, which replays the PR #1188 baseline
and Sagar Thakrar's PR #2115 deferred-target-undo construction. No construction,
undo optimization or native checker theorem is claimed as new here. The
independent Python bitset and prefix implementation adds a replay of this
fixed nine-stage boundary; it does not replace the native engine in the timed
experiment. The benchmark runs unchanged, pinned native bytes.
