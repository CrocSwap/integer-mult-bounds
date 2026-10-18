# Optimal subdivision of canonical fixed-reader typed windows

**A scoped optimizer and sharp asymptotic floor; no native-child saving or
supplier admission.** For the exact canonical macro family audited in
[PR2626](https://github.com/CrocSwap/integer-mult-bounds/pull/2626), this package
minimizes scalar primitive count over every consecutive subdivision of a given
child word. Mandatory caller boundaries cannot be crossed. Its finite potential
certificate also proves, for every word of length `n` and every such subdivision,

`primitive_count >= (448/3) n`.

The period `012201120` repeated `k` times has a legal single-window invoice
`1344 k + 8`, so the coefficient is asymptotically sharp. In this family even
unrestricted choice of octet sequence and subdivision can save asymptotically
at most `1/57` of the all-singleton bill `152 n`. This closes a scalar scheduling
question; it does not change any COPY/ERASE recursive-child invoice.

## Contract and changed question

PR2626, head `a42fdf29a3d5c3e5140f4985a0c8e495d4eb544c`, supplies the exact
fixed-reader tariff. We retain its three source octets, arbitrary dirty work
octets, eight output registers, canonical order-four phase words, and literal
body reversal. Sources are read-only. Each macro is
`COPY; body; ERASE; inverse(body)`; the endpoint restores all work registers
and adds the chosen source octets to the output. COPY may choose its initial
permutation for each used octet and ERASE accepts the resulting phase.

**The changed search space permits additional internal window boundaries.**
Each segment is itself a complete legal source macro. Concatenating them has
the same full linear endpoint, including arbitrary initial output and dirty
work, and restores work at every segment boundary. Original call boundaries
are mandatory cuts: output is delivered and work restored there. No result
is deferred across an original call boundary. This contract is not the literal
fixed-entry-phase variant or the phase-indexed reader variant of PR2626.

For a nonempty word `w`, the source tariff is

`L(w) = 136 |w| + 16 |used(w)| + 2 sum c((p-q) mod 4)`,

where the sum runs over successive occurrences `p<q` of each octet and
`c=(0,20,16,20)`. The body contributes 68 primitives per child, doubled by
its inverse; each used octet contributes eight COPY and eight ERASE ADDs.
The source proves that these gap corrections are optimal **within its
canonical macro alphabet**, using phase-tariff subadditivity. We reproduce its
unchanged full verifier before relying on that lemma. We do not claim a lower
bound over arbitrary ADD/NEG programs, changed readers, general coupled
corrections, or native recursive calls.

## Exact optimizer

After each processed child, a state stores three entries. An unseen octet
has entry `-1`; a seen one has `(current_position-last_read_position) mod 4`.
The initial state is `(-1,-1,-1)`. To append letter `x`, increment every seen
age modulo four. If `x` was unseen, add overhead16; otherwise add
`2*c(-age[x] mod4)`. Then set its age to zero. A cut transition first resets
all entries to unseen. Each transition additionally costs136.

The increment is precisely the next gap in the tariff. Every subdivision
gives one automaton path, and every path gives a subdivision; duplicate first
cut/no-cut paths have the same price. Mandatory boundaries force the cut
transition. Dynamic programming therefore returns the exact minimum and,
optionally, a backpointer witness. There are62 reachable states and372
labelled transitions including cut/no-cut alternatives. This is also checked
by explicit closure in the verifier.

Price-only optimization uses at most62 integer cells per layer and `O(62 n)`
transitions; optional backpointers use `O(62 n)` cells. Prices have `O(log n)`
bits. These are abstract algorithmic bounds, not a physical tape or bit-time
claim. The independent interval recurrence in the verifier deliberately uses
direct whole-window costs; its simple implementation is not advertised as the
fast algorithm.

## Proof of the uniform floor

[POTENTIAL.json](POTENTIAL.json) assigns an integer `H(s)>=0` to every state,
with `H(initial)=0`. For all372 edges of overhead `w`, the verifier checks

`H(target) <= H(source) + 3w - 40`.

Telescoping along any length-n path gives
`3 sum w >= 40n + H(final) >= 40n`. Adding `3*136n` proves
`3*primitive_count >=448n`. Mandatory cuts restrict the path set and preserve
the inequality. The theorem uses only the complete finite edge inequalities
and their telescoping proof. Shortest-path relaxation generates the certificate;
its implementation is not assumed correct to accept the certificate.

For sharpness, in `012201120` the zero positions are `0,4,8`, the one positions
`1,5,6`, and the two positions `2,3,7`. Internal correction costs sum40.
Between consecutive periods the three gaps have residues1,0,0, hence total
correction20. Thus the whole-word correction sum is `40k+20(k-1)=60k-20`.
All three octets are used, so
`L =136*9k +48 +2*(60k-20)=1344k+8`.
Together with the universal floor this proves asymptotic sharpness. It does
not assert that this single window is the finite optimum for every k or n.

## Why pairwise greedy improvement is insufficient

The six-child word `012201` has one-window cost904; six singleton windows
cost912. Every adjacent singleton pair has zero or negative fusion saving,
so a strategy that accepts only strictly positive pairwise merges makes no
first move. The optimal partition can still save8. This does not refute
algorithms that permit neutral moves, backtracking or larger merges.

## Evidence and reproduction

```sh
python3 -B research/typed-window-partition-floor/verify.py
python3 -B research/typed-window-partition-floor/test_integrity.py
python3 scripts/research_package.py --package research/typed-window-partition-floor
```

The ordinary verifier is read-only. `--write` creates absent receipts and
refuses to overwrite either existing receipt. Source bytes are authenticated
before import. [SNAPSHOTS.json](SNAPSHOTS.json) binds every unchanged PR2626
file by SHA256 and Git blob; [SOURCES.json](SOURCES.json) binds its two retained
scientific inputs. Git-free execution is supported; historical provenance is
distinct from live scientific inputs.

The stored evidence includes3279 words through length7 compared with a
separate interval recurrence;4665 word/mandatory-cut instances through length5
checked against exhaustive partitions; all62 states and372 edges; nine
scientific failure controls; and six compiled optimal schedules. An independent
row-matrix interpreter checks all56 columns at every segment endpoint and the
full inverse, proving the tested dirty-state behavior without zero-input
assumptions. Full source regression includes3279 source words and14400 source
ordered pairs. Compiled fixtures fit the predecessor's64-child emitter limit;
the symbolic theorem and our optimizer cover arbitrary finite lengths.

The receipts also include reads, writes, travel, dispatches, descriptor bits
and storage under the predecessor's explicit invoice convention. We minimize
**only scalar primitive count**. More windows add headers; no multiobjective,
wall-clock, whole-cover or native-hosting optimum is asserted.

## Open next questions

This is a **local scheduling/audit milestone**, selected under revision4 and
continued after reading revision5 on main
`b4560d9e7216f72b73c5aa940ac099c05e33ccf9`. The changed guidance leaves the
scientific source inputs unchanged. [TASK.json](TASK.json) records the boundary,
cost statuses and stop decision. Primitive cost and arbitrary-dirty endpoint
are proved; finite compiler/invoice costs are constructive. Native embedding,
caller retention, coefficient precision, physical hosting and a supplier-level
consumer budget are unknown and are not set to zero.

**Stop this scalar subdivision route here.** The uniform floor bounds its
possible gain, while a scalar primitive reduction does not discharge the
selected centre's recursive COPY/ERASE charge (the distinction emphasized in
PR2500 and the predecessor lineage). Further implementation is justified only
by a named consumer contract and allowance that survives native lowering and
cleanup. A different phase-indexed-reader contract is a separate alternative
already compared by PR2595/2626; this package does not reopen that calculation.
The next meaningful question is whether a consumer actually needs this
fixed-reader macro and can use internal restoration boundaries without
repaying the small saving. No such consumer is claimed here.

## Credit

PR2626 is Nick Petalas's audit of Aaron Wang's PR2595 construction and its
PR2464 context. Retain Cinna Davis's PR1391/1410 canonical phase construction,
Ross Richardson's PR1287/2500 interface boundaries and Sagar Thakrar's PR1227
lineage, along with every unchanged notice in the vendored package. Finite-state
dynamic programming and potential telescoping are standard methods. The new
result is their exact instantiation for this tariff, the subdivision witness
and the sharp uniform coefficient, not a claim to invent those methods.
Prepared by ywz65 with substantial OpenAI Codex assistance and separate AI
review; no independent human review is claimed. New material is Apache-2.0.
