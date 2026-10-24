# Exact ternary disjointness-repair rank in even dimensions

For every even **h >= 4** and every field F of characteristic three, let
A_h be disjointness on the nonempty proper subsets of [h]. Then

$$
\operatorname{rank}_F(I-A_h)
=3\cdot2^{h-2}-1-(-1)^{h/2}2^{h/2-1}.
$$

This also counts the minimum unrestricted additive scalar rank-one terms
repairing A_h to the identity. At h=2 the rank is 1.
The [written proof](PROOF.md) resolves the explicitly open even-dimensional
question in Nick Petalas's [#5173](https://github.com/CrocSwap/integer-mult-bounds/pull/5173).
That predecessor proves odd h and supplies the h=2 control. The new step
proves that deleting both endpoints reduces the singular full tensor's
kernel dimension by exactly one, for every even h>=4.

| h | Interior dimension | Exact rank | Kernel dimension |
|---:|---:|---:|---:|
| 2 | 2 | 1 | 1 |
| 4 | 14 | 9 | 5 |
| 6 | 62 | 51 | 11 |
| 8 | 254 | 183 | 71 |
| 10 | 1022 | 783 | 239 |

This is a **scoped algebraic proof with finite exact corroboration**.
Independent human review and formal proof-kernel acceptance are unclaimed.
No native ternary supplier, physical COPY tariff, complete recursive bill,
new kappa or selected-frontier change is claimed.

## Reproduce and evidence

Python 3.12, standard library only. From the repository root:

```sh
python3.12 -I -W error -B research/even-ternary-disjointness-rank/verify.py
python3.12 -I -O -W error -B research/even-ternary-disjointness-rank/verify.py
python3.12 -B scripts/research_package.py --package research/even-ternary-disjointness-rank
```

Expected marker: `PASS_EVEN_TERNARY_DISJOINTNESS_RANK`. Each direct check
took under one second on CPython 3.12.12/macOS. The verifier is read-only,
Git/network-free and uses explicit exceptions, comparing its complete finite
result with [RESULTS.json](RESULTS.json). To regenerate evidence without
overwriting it, pass `--emit-results` and redirect stdout to a new file.

Checks cover exact bit-packed F3 ranks at h=2,4,6,8,10 and separately written
dense ranks through h=8; all 729 ternary 2-by-3 matrices compare the engines.
At h=2,4,6,8, all 340 basis columns check T^4=I, MP=0, P^2=P and
MG=GM=I-P, the endpoint blocks and projector ranks, where
P=I+T+T^2+T^3 and G=T^2-T. At h=2,4 the tensor action also agrees with the
literal disjointness predicate on every column.

A separate complete kernel count uses two half-input syndrome tables,
without elimination. At h=4 it covers all 3^14=4,782,969 inputs, enumerating
4,374 half inputs, and finds 243 kernel vectors. The h=2 control finds three.
The integer binomial multiplicity formula is checked at 100 even dimensions
from 2 to 200. Thirteen domain, h=2, endpoint-deletion, group-inverse and
projector rejection controls pass. These checks corroborate the written
proof; they do not supply its universal quantifier.

[independent.py](independent.py) was written by a separately tasked Luna
worker given the matrix definition and finite dimensions, without the
candidate formula or predecessor verifier code. The primary agent inspected
and reran it. This is separate implementation within AI-assisted work,
not independent human review. Its standalone output also records full-matrix
and single-endpoint-deletion ranks at h=2,4,6.

## Scope, sources and overlap

Scientific base: fresh canonical main
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority revision 7.
[Claim #5194](https://github.com/CrocSwap/integer-mult-bounds/discussions/5194)
takes the released [#5173 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145071).
This changes the generic `formal-interface-lemma` card to that concrete
algebraic question. It closes an infinite family left open by the predecessor;
the odd-h theorem and binary rank are cited rather than replayed as new work.

Initial overlap covered 6,996 local notes, 312 open PRs and 4,384 Discussion
records with complete pagination at 12:12–12:13 UTC on 2026-10-23, followed
by targeted live checks before claiming. No competing even-dimensional claim
was found. Arbitrary diffs and unpublished work remain coverage limits.
The donor's excluded topics and parallel R437/projection work are outside scope.

[SOURCES.json](SOURCES.json) pins the exact base, blobs and SHA256 of the
catalogue, selected record and predecessor documents as historical provenance.
No predecessor code or artifact is imported or modified. The checker constructs
its own matrices, so those documents are not live scientific inputs. The
registered runner checks Git provenance; the standalone checker needs no Git.

Physical implementation, coefficient preparation, reads/copies, arbitrary
dirty restoration, frames/hosting, precision, tape, stock, compiler and
recursive/outer costs are outside scope and not treated as zero. The binary
ledger from #4962 does not transfer to F3. Nonadditive repairs are not excluded.
No predecessor scientific suite, selected cold replay, Lean or Docker run is
needed or claimed.

## Open next questions

Can a nonadditive ternary repair avoid this additive rank obstruction?
This matters to whether the endpoint can support a useful physical supplier.
First specify an exact all-input ternary operation and a complete favorable
paid bill, including preparation and restoration. Those contracts and costs
are missing; another parameter sweep of the solved additive rank family is
not a useful next step. No implementation expansion or follow-up is reserved.

## Credit

- **Nick Petalas, #5173**, head `50ee4f7069d7aabdcdfc44ebadf0456d8cf82e0c`:
  odd-dimensional ternary theorem, h=2 boundary and explicit even-h question.
- **Ali Romman, #4962**: binary repair theorem and tensor/endpoint-deletion
  approach, with substantial OpenAI Codex assistance.
- **mikey1201, #172**, head `427b23bc79489e7b2b7548bfd434dd9670fd5c47`:
  disjointness endpoint and retained **icekylinx/#144** compiler/bookkeeping
  lineage, with source-specific Cline assistance. No physical cost is assumed free.
- **Krzysztof Wojt**, with substantial **OpenAI Codex assistance**: all-even
  theorem, singular endpoint argument, checker and package; the bounded Luna
  fixture task is disclosed above.

New work is Apache-2.0. Frozen sources and the selected result remain unchanged.
