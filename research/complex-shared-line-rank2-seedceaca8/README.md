# Shared-line rank-two block: exact favorable ceiling screen

**Scoped negative result. No source-realized block, supplier, or new κ.**

The selected #1094 complex local profile is
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` per call. I tested a new rank-shape
mechanism: if two rank-two child frames have target planes that share exactly
one line, replace the two rank-two children by one rank-three block child that
materializes the shared direction once. This changes `2+2` paid rank units to
`3`, frees one unit of coverage mass per pair, and would need a legal block
interface to copy the shared output to both targets.

## Exact upper-bound calculation

Keep the selected model fixed: child size `m=73`, 896 families over 9 stages,
centre charge 64, one unpaid coordinate, and idle cap `R=51`. Allow every one
of the 418 rank-two events to pair, so `g` ranges from 0 to 209. For each `g`,
the relaxed local profile is

```text
n2 = 418 - 2g
n3 = 432 + g
n1 = 2412, n4 = 142, n5 = 82, n8 = 8
```

All matching, source access, input/output adapters, copies, fanout, frame
transitions, hosting, precision, and dirty-state restoration are charged zero.
The freed rank mass is assigned to fractional rank-51 idle children by the
pinned ceiling model. This is a favorable completed budget for the proposed
profile substitution.

More fusions cannot worsen this relaxation. For a fusion, four units of rank-2
mass become three units of rank-3 mass plus one unit of idle mass. The idle
unit is carried at rank 51. For `a >= 0`, the per-mass cost factor `r^(-a)` is
non-increasing in `r`; the three rank-3 units and one rank-51 unit therefore
cost no more than four rank-2 units. So `g=209` gives the best ceiling in this
profile family.

| Profile | Rank mass | Idle mass | Certified `a` ceiling |
|---|---:|---:|---:|
| `g=0` (selected) | 5,586 | 1,646 | `[0.001690054109088, 0.001690054109089]` |
| `g=209` (every rank-2 event paired) | 5,377 | 1,855 | `[0.001768394682583, 0.001768394682584]` |

Using the baseline upper endpoint, a 5% target is
`0.00177455681454345`. Even the all-pairs upper endpoint is below it: the
endpoint ratio is exactly `43131577624/41220831929` (about `1.0463`), less than
`21/20`. The profile-only gain therefore tops out at about `4.6354%`, before charging
any physical interface. Per the task gate, I stopped before searching or
synthesizing selected-source pairs.

## Scope and limits

This rules out a 5% ceiling improvement from this profile substitution alone,
under the unchanged coverage law, centre charge, and outer rank cap. It does
not show that a shared-line block is impossible. Nor does it rule out a smaller
profile gain, combinations with a changed coverage law, or other rank-shape
mechanisms. The source event stream supplies frame IDs and ranks, but this
screen does not prove that any particular two transitions admit the proposed
joint interface. Physical compatibility and all adapter/copy/restoration
costs remain unproved.

## Open next questions

- **Can a selected-source pair of rank-two frame transitions with a shared
  target line be realized by one rank-three block with fully charged source
  access, fanout, adapters, and dirty restoration?** A source-realized block
  could still offer a sub-5% local gain or combine with a changed coverage law.
  The first step is to identify one exact pair in the pinned local program and
  compare its full Clifford transitions with a proposed joint rank-three block
  interface. This was not needed after the ideal 5% gate failed.

## Reproduce

```sh
python3 -I -B research/complex-shared-line-rank2-seedceaca8/verify.py
python3 scripts/research_package.py --package research/complex-shared-line-rank2-seedceaca8
```

The verifier checks the selected replay archive and member hashes, independently
recounts both directions of the local rank profile, recomputes both rational
ceiling brackets using the pinned `complex-local-word-ceiling/ceiling.py`, and
checks the maximal-fusion and 5% boundary controls.

## Provenance

Cycle X, seed `ceaca886bcd52d7e2a036a2b4d561117`, on exact base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; task `complex-rank-shape-decoder`,
catalogue priority revision 4. Claim: [Discussion #1163 comment 18933950](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18933950).
Focused review package: [PR #2151](https://github.com/CrocSwap/integer-mult-bounds/pull/2151).

The initial claim comment contains transcription errors in its archive and
canonical-word member SHA-256 strings. `SOURCES.json` and `verify.py` contain
the correct hashes; the Discussion comment still needs a correction reply.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in selecting
the profile-level mechanism, deriving the favorable bound, implementing exact
checks, and writing the package.
