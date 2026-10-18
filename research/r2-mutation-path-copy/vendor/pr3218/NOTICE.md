# Attribution and retained sources

New comparator, integration, controls, benchmark and documentation: Tekalign
(@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.

`vendor/pr3202/` retains twelve files verbatim from 24kHandsome1201's
PR3202, commit `259043321323717b7e816d6be38ad5e1f0b69b4c`. Its original README,
code attribution, native receipts and source manifest are unchanged. These
files are necessary to replay the current R2 caller and its exact artifacts;
they are not newly generated native evidence. See `SOURCES.json` for every
source path, blob and SHA256 digest. The upstream repository's Apache-2.0
license applies.

Sagar Thakrar (@thakrarsagar), PR1781, supplies the separate packed exact
Clifford kernel and its gate conventions. The default packed oracle remains
unchanged. The comparator criterion (signed Pauli tableau plus one exact
column) is established Clifford algebra, also used by the retained native
producer; its discovery is not claimed here. Credit icekylinx, Jeremy Kothe,
Mason Hale and the original Clifford/native implementation lineage.

ywz65, PR2638, supplies the existing opt-in cached-table packed comparator used
as a stronger benchmark baseline. Charles Bethin (@cbethin), PR662, supplies
its table recurrences. The new engine's bounded immutable table implementation
uses the same known binary recurrences, independently coded for this engine.
Ali Romman/#1029 and Tekalign/#2768 are predecessors for sparse exact state
evaluation and current native replay tooling, respectively.

The R2 construction and its audits retain Nick Petalas/#3044, Jeremy Kothe,
Marius-Paul Dumitrean/#2979, Hiroki Kumazaki/#3146, Cinna Davis and the full
geometry, extraction, ownership and native lineage listed in the retained
README. This package does not assume independent approval of those sources.

Substantial AI assistance was used for algebra, implementation, testing and
writing. No independent human or proof-assistant review is claimed.
