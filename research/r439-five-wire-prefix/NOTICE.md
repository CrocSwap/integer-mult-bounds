# Attribution and source notice

This contribution is by Ross Richardson (@RossRichardson), prepared with
substantial OpenAI Codex assistance. A second AI agent independently implemented
the finite Boolean/positive-transfer certificate checks. No independent human
review is claimed. New work is Apache-2.0; see LICENSE.

The local resynthesis and interval-packing method follows Jeffrey Cox
(@namredips), PR754 (`47ebba87e064cc69d9b4834081fc74080762a74f`), and Gareth
Davidson (@bitplane), PR904 (`883a0bdf7792693e57c16be660824b57aacfbe05`).
The PR904 candidate is the unchanged starting word, preserved with its exact
certificate, README, notice and license under `vendor/pr904/`. PR904's
`build.py` and `common.py` are preserved unchanged for the repeated-pass control.
Our common.py is adapted from PR904's I/O helpers, and native.py from PR904's
harness (itself adapted from Sagar Thakrar's R420 decoder-sharing harness).
The native changes identify the new baseline/candidate costs and attribution.

The selected PR589 R439 word/tuner is DreamingOfClouds' work on eumemic's PR555
punctured R439 and PR543 R420 skeleton, with PR545/493/510/425/370 ancestry.
Retain the existing notices in `research/e8-bit-p111-tuned` and
`research/e8-bit-carrier-skeleton`; all used files are pinned in SOURCES.json.
The unchanged native exporter/checkers credit Dylan Crow, DaysSky, Zhihao Chen,
and their retained source notices. Substantial AI assistance in predecessor
sources is disclosed by their authors in those notices.

Related PR886's frame-only negative result and concurrent PR925, PR915/926 are
acknowledged, not imported. No savings from those candidates are composed here.
No repository selected-frontier or predecessor package is modified.
