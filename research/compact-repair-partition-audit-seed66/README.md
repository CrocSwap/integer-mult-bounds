# When exceptional repair can be split into independent batches

**Research note / adversarial mathematical audit. No new κ.** A small total
cleanup bill does not mean each batch can clean itself: an item may need to
move into another batch. This note gives the exact safety condition and tests
it on the unchanged compact-control code.

## Result

After the raw address permutation S, the required correction is P=T S^-1.
Independent batches work on arbitrary payloads **if and only if each batch
is a union of cycles of P**. This statement concerns batches that receive no
payload information from one another. It does not forbid paid cross-batch
routing. [PROOF.md](PROOF.md) gives the quantified proof.

For PR2250's earlier-source two-slot word, on the saturated dirty-digit
fibre, the active repair cycles have length
`2^(2K-rho-G-1)`. At `(G,K,rho)=(4,8,2)` the actual source sends post-raw
target address **0 to 65,408**, with raw preimage **65,412**. The complete
65,536-address fibre has **64 cycles of length 512** and **32,768 fixed
points**. Every proper dyadic contiguous target partition fails. Residue
cells modulo 128 are a positive control; unlike the raw map, the repair
preserves them.

For a disjoint exhaustive partition retaining whole R-bit records and a
common valid key/control bound A, the exact source tariffs add:

    sum_i [M_i R + M_i A^3 + B_i A(R+A)]
      = M R + M A^3 + B A(R+A).

A batch may therefore be entirely bad while the aggregate repair tariff
stays at most three times the original volume under PR2476's admission
conditions. Correctness still needs the cycle condition. Dispatch, gathering,
merging and parking costs remain separate. This supplies a conditional answer
to PR2476's aggregate-partition handoff, not a faster repair implementation.

## What is new and what is inherited

@martinxxx9's [PR1108](https://github.com/CrocSwap/integer-mult-bounds/pull/1108)
already proves the one-digit saturation law and raw-word order. John-Michael
Smith's PR763 checks repair on invariant source/back-field fibres. Jose
Manuel's [PR2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250)
supplies the actual stream interpreter, global repair and tariff.
@ywz65's [PR2476](https://github.com/CrocSwap/integer-mult-bounds/pull/2476)
proves the uniform recursive repair bound and distinguishes global density
from density in one bad-only slice.

We add the **independent-cell endpoint condition**, apply the credited law
to the actual correction `T S^-1`, and connect valid partitions to aggregate
accounting. No source bug, new one-digit defect, improved guard, new moment
or completed supplier is asserted. The numerical recursive bound is inherited,
conditionally; its moment engines are not rerun here.

## Reproduce

From the repository root, with CPython 3.12 and no external dependencies:

```sh
python3 -I -B scripts/research_package.py --package research/compact-repair-partition-audit-seed66
```

Expected: `PASS_COMPACT_REPAIR_PARTITION_AUDIT addresses=2396160
orbit_length=512 physical_records=4096 no_new_kappa`, six passing test groups,
then `PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
The direct replay is self-contained and also works in a Git-free export:
`python3 -I -O -B research/compact-repair-partition-audit-seed66/verify.py`.
Normal verification is read-only. `--write /new/file.json` generates a receipt
without overwriting an existing file.

## Evidence and exact scope

| Check | Completed domain |
| --- | --- |
| Original raw executor vs independent four-update arithmetic and inverse-table oracle | All target values, every dirty digit and both active source bits at G=1..4, K=G+4, rho=66 mod K: 2,396,160 cases; other spectator values are fixed by the declared fixture |
| Actual source inverse and ideal map | All 65,536 target values in the primary saturated fibre |
| General partition criterion vs independent keyed reinsertion | All 6,635 permutation/partition pairs on 1..5 records, 591 admitted |
| Additive tariff identity | All 14,946 partition/bad-set pairs on 1..6 records |
| Original sequential program, original radix sort and full payload comparison | Two complete 2,048-record rectangles, 11-bit injective record labels; both selected offsets at G=1,K=2 |

The small physical fixtures deliberately have an empty sufficient good set;
they test endpoints, not asymptotic admission. Injective record labels check
the complete permutation of those records. The proposed partition dispatcher
in the test harness is a Python grouping operation, not a fixed-tape compiler.
The mathematical proofs, not finite extrapolation, supply the all-size claims.

Negative controls reject independent half-range reinsertion, every proper
dyadic target partition in the primary fibre, a wrong repair sign, a modified
source before import, a false Git blob, and altered receipt data. Tariff
countermodels expose repeated bad-record visits and coefficient fragmentation.
A clean optimized Git-free replay verifies that normal execution changes no
files. [VALIDATION.md](VALIDATION.md) records executed commands and limits.

Starting main: `bd1b3bc7174cddbfa4e30ac073dc134f48aa6e77`, priority revision 5.
The exact executable dependency is PR2250 at
`d404b48a1e7b147556b309497d55089c837dddb2`; the audit target is PR2476 at
`32e88ddfd111b93fbcfb306514397cf406e4d5d4`.
[SOURCES.json](SOURCES.json) pins original paths, Git blobs and SHA256 bytes.
The selected result remains `0.001672660197076918` and is provenance only.
[CLAIM.json](CLAIM.json) records OS seed 66, three candidates, bounded overlap
coverage and the failed upstream claim-post attempt (403). No claim was posted.

## Open next questions

- Can useful invariant cells be gathered and returned at uniform linear total
  access cost? Start with the actual modulo-128 cells and price all selection,
  metadata and parking work. Their noncontiguity is the unresolved cost.
- Which partitions work for a specific multi-digit or later-source repair?
  First derive that exact residual map. Additional carries couple compact
  fields; the one-digit formula does not establish its answer.

These questions and blockers are structured in [TASK.json](TASK.json). Neither
is claimed completed, and no broad follow-up search is launched here.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI Codex assistance** in
mathematics, code, source review, verification and writing. The separate
implementations share the same AI author; no independent human or formal-kernel
review is claimed. [NOTICE.md](NOTICE.md) preserves predecessor credit and the
unchanged source notice. Apache-2.0. No selected frontier, supplier code or
`upstream/` file changes.
