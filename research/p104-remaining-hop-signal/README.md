# Seven paid-hop bypasses need new main-signal acquisition

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with an exact finite certificate; no new kappa.** None of the
seven nonempty combinations of bypassing the three specified read-only owned
stops in DreamingOfClouds' [PR6621](https://github.com/CrocSwap/integer-mult-bounds/pull/6621)
can preserve its main map using only initial frame-3 preparation and terminal
frame-127 cleanup. Arbitrary linear work in those two phases cannot help.

The stops are register 772 at frame 520 and register 771 at frames 534 and
117. Each bypass deletes that stop's outgoing reads and directly joins its
neighboring owned transports. Every other scalar event and public endpoint
stays fixed. [PROOF.md](PROOF.md) defines this correction contract precisely.

For indicators A, B, C of the three bypasses, the exact main-map defect has
rank `A + bool(B or C)`. Its explicit decomposition uses two independent
52-coordinate input functionals. All seven defects are nonzero.

| Bypassed stops | Defect rank | Changed main outputs | Changed main coefficients |
| --- | ---: | ---: | ---: |
| 772/520 | 1 | 2 | 104 |
| 771/534 | 1 | 2 | 104 |
| 772/520, 771/534 | 2 | 4 | 208 |
| 771/117 | 1 | 3 | 156 |
| 772/520, 771/117 | 2 | 5 | 260 |
| 771/534, 771/117 | 1 | 5 | 260 |
| all three | 2 | 7 | 364 |

There is also a cost obstruction for repairs that add paid work. For
`H_r=r^(1-C)` and `0<C<=1/32`, even bypassing all three stops saves less
than `24C<=3/4` paid moment per native call. One additional paid job of any
positive integer rank costs at least one and consumes that entire saving.
This does not prove that every changed acquisition needs an extra paid job.

The next construction must alter the acquisition or delivery of main signal,
use other chronological charts, or change other target/paid work. Extending
the two specified preparation/cleanup phases cannot fix these bypasses.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/p104-remaining-hop-signal/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/p104-remaining-hop-signal/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-remaining-hop-signal
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-remaining-hop-signal --check-source-history
```

Other systems may substitute their CPython 3.12 interpreter. The direct
marker is `PASS_REMAINING_HOP_MAIN_SIGNAL`. Each run prints a fresh JSON
receipt bound to every package file hash and writes no files.

The primary engine evaluates all 104 input columns symbolically for the
source and each bypass. A second calculation uses backward source
functionals and forward destination impulses, checks all later deleted-read
couplings, and compares every coefficient of every defect. Exact rational
elimination checks the ranks. The verifier checks common charts, nested
transports, unchanged endpoints and paid deltas for each modified word.
Six controls cover the unchanged word, an altered source byte, three retained
reads at bypassed charts and a reversed response sign. All checks remain
active under optimized Python.

## Source and scope

The source is PR6621 head `c51a142bb94c6d46ebee9a48c3f71cde8022da91`.
The exact compressed word is retained in this package. [INPUT.json](INPUT.json)
records its archive/member origin, size, Git blob and SHA256. The original
archive's API identity and nested-word equality were checked locally.
Replay does not need the
pending PR's Git objects, its nested implementation, network access or an
optional solver. [PREDECESSOR-NOTICE](PREDECESSOR-NOTICE) is copied unchanged.

This answers a bounded construction branch of PR6621's second open question.
It does not audit that PR's result, price or caller. PR6163's receiver-window
obstruction concerns a different read substitution and repair window;
CubeJerry's [PR6248](https://github.com/CrocSwap/integer-mult-bounds/pull/6248)
and PR6257's cache floors concern preserved operands and charged cache paths.
Those models are neither replayed nor extended here. The new
question fixes direct bypasses and permits arbitrary preparation/cleanup in
two different phases, including simultaneous edits on both owned roots.

The selected baseline returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` as
orientation. No selected cold replay, native phase replay, caller admission,
compiler, analytic recovery or complete rounded multiplier is supplied.
The fourth intermediate owned stop, which has an incoming update, is not
covered. Neither are interior repairs, new source representations or arbitrary
changed words. Independent human and formal proof-kernel review are unclaimed.

The verifier is nonrecursive. Its fixed source bounds each word by 18,561
events, 799 roles, 104 symbolic columns and binary frames of dimension at most
nine. Every function is shorter than 60 lines. Python allocates dictionaries,
Fractions and integer temporaries during replay, a managed-runtime deviation
from allocation-free execution. No external input can enlarge the domain
without failing the pinned-byte gate. Warning-strict normal and optimized
replays are the interpreted-code diagnostics; external Python linters were
unavailable.

## Open next questions

1. Can an interior common chart supply one of the two missing main
   functionals without an additional paid job? Start from the explicit v and w
   responses in the verifier, identify an actual source/receiver pair and
   charge every changed transport and target. No such acquisition is supplied.
2. Can changing the source of register 773's incoming frame-1031 update
   merge its two paid hops? First derive that two-input boundary with arbitrary
   dirty state. It is outside the read-only bypass class proved here.

## Credit

DreamingOfClouds / PR6621 supplies the native word and the construction lead.
Credit Ali Romman's PR6551/6529, the PR6545 retirement construction,
Erwan L.'s PR6453, PR6398/6399 and all native, helper, compiler, interval and
analytic contributors retained in the predecessor notice. The linear-response
and rank-subadditivity arguments are classical. The seven-case obstruction,
its prefix/suffix proof, price bound and new verifier were produced by
Nick Petalas.
