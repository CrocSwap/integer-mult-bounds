# Selected adjacent-call centre-owner census

This package checks the 143 adjacent ordered call pairs in the pinned selected
144-call schedule from PR1094. It asks whether the existing two-panel
centre-fanout interface from PR1708 and centre-return interface from PR1748
can share all eight centre inputs directly, with no added owner or chart
transport.

## Result

There are 81 adjacent pairs with the same orientation and 62 with mixed
orientations. All 81 same-orientation pairs have disjoint full 112-row target
panels. None shares even one physical owner ID among its eight centre source
rows. Nine pairs have equal chart tuples in all eight slots, but all eight
physical owner IDs differ in each such pair. Thus no adjacent pair instantiates
the predecessor interface with an identical eight-row source boundary and
zero owner transport.

This closes only that direct-owner witness question for the fixed schedule.
It does not rule out aliases, copied values, a nontrivial linear map between
owners, nonadjacent calls, or a changed global schedule. The result gives no
new supplier, paid-moment saving, conditional bound, or kappa.

## Reproduction

From the repository root, run:

    python3 -I -O -B research/selected-centre-adjacent-pair-seed01fcb1/verify.py

Expected status: **PASS_SELECTED_ADJACENT_OWNER_CENSUS**.

The verifier uses only the standard library. It pins the selected-result
record, selected replay archive, and four exact archive-member byte strings.
It reconstructs all eight source and target roles independently from the
gauge44 local programs, binds the forward and backward programs to
LOCAL-CHECKS, verifies the backward target rows against CANONICAL-WORD.cut,
maps all roles through each scheduled call's owner/chart records, and checks
the full 112-row target panels. Six synthetic controls check the admission
predicate, including equal charts with different physical owners.

## Pins and attribution

- Base commit: 0b1cccf86e2f5132ed286a26ef0a681a495740ea
- Selected-result record SHA-256:
  10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32
- Selected replay archive SHA-256:
  f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6
- Predecessor PR1708 head:
  4d163c04c0980c5b0e9092fbd5864c7cfadc125d
- Predecessor PR1748 head:
  ea14f191752c9901bf6684763534d2d248fb2ad2
- Predecessor PR1791 head:
  00d05a64898571cf57a14310fbcd3507ca99c5ec
- Related coordination: Discussion #1516, comments 18918111 and 18921301.

The local two-panel algebra is attributed to the authors of PR1708 and PR1748;
the selected-schedule budget is attributed to PR1791. This contribution adds
the bounded selected-schedule owner/chart census. It was prepared with
substantial OpenAI Codex assistance.

At the pinned base, the selected record resolves to review
docs/research/community-batch1099-review.md, source manifest
research/community-frontier1094-audit/SELECTED-SOURCE.json, assembly
certificate research/community-frontier1094-audit/ASSEMBLY.json, and the
selected replay command make frontier1094-verify. The record, review, manifest,
certificate, and integration receipt have exact provenance pins in
SOURCES.json. This package verifies its narrower adjacent-pair census and
does not rerun the complete selected-frontier replay. The selected conditional
finite value remains 836330098538459/500000000000000000; this result makes no
change to it.

## Cost and remaining obligations

The ideal local rewrite saves 32 paid-mass units per call by sharing the
rank-eight centre paths. PR1791's actual-profile screen leaves about 30.5 to
30.8 additional units per call for the full bit-limited gain, and strictly
less than 32 for any gain. This census finds no direct common owner/chart
source boundary, so any attempt to realize the interface would need owner
transport or another mechanism. This package does not price such a mechanism;
it therefore makes no claim that it fits the remaining budget. Precision,
frame changes, restoration, hosting, and interface charges remain payable.

The search domain is exactly the 143 consecutive pairs in this archive's
144-call schedule. It stops after that complete census and does not inspect
nonadjacent pairs or altered schedules.

## Open next questions

A possible follow-up is whether a nonadjacent same-orientation pair shares the
direct eight-row owner/chart boundary with disjoint full target panels. The
structured question in TASK.json gives its motivation, first step, and blocker.
