# Exact two-sided prefix substitution and complete cost

All endpoint matrices in this section act over F2. Integer positive prefix
bounds are checked separately; equality of the forward integer operators is
not claimed. Fix the input hashes in SOURCES.json and the 111 target rows and
439 helper columns of the selected PR589 compensation matrix K. Physical
targets are registers 111 through 221; helpers are 222 through 660.

## Restored arbitrary-input boundary

Let E be the product of PR915's 306 target transvections in their actual
execution order. If T1 is executed first, E = T306 ... T1. Let H be the
product of helper transvections `helper[a] ^= helper[b]` for the 192 disjoint
pairs in CERTIFICATE.json. Each transvection is its own inverse over F2.
Disjointness implies that the helper transvections commute and H inverse = H.
The target transvections need not commute; E inverse is executed by reversing
their order.

The emitted D acts on arbitrary `(x, y, s)` as follows:

1. Helpers become Hs.
2. Targets become Ey.
3. Targets become Ey + (E K H inverse)(Hs) = Ey + EKs.
4. Applying E inverse to targets gives y + Ks.
5. Applying H inverse to helpers restores s.

Sources x are never read or written in D. All D operands start and remain at
frame zero. Every helper is restored before A, and targets have the same
value and frame as after the original D. All non-D fields are identical, so
the entire unchanged suffix receives the original boundary state. This is
the exact semantic substitution needed under the inherited realization
assumptions.

The original H2 only permits helper-to-target additions. It is false for
both PR915 and this word. The original literal K extractor is also false.
We retain both predicates unchanged and require them to be reported false.
The replacement contract is the complete legal D boundary above. H1, H3,
H4 and H5, and all other source-checker conclusions, remain true. Acceptance
of the replacement contract is a maintainer review obligation.

## Column orientation, mixed term and savings

For a helper transvection a <- b, H has entry (a,b) in addition to I. Right
multiplication changes **column b by column a**. Thus its paid gain on the
current transformed matrix R = EK is

```text
weight(R[:,b]) - weight(R[:,b] XOR R[:,a]) - 2.
```

The two charged ADDs prepare and restore the actual helper. Because accepted
pairs use disjoint helper indices, the columns of a later admissible pair
have not changed. Their initial pair score is therefore still exact. The
builder sorts all positive scores by `(-gain, tie, a, b)` and walks the list
once. A trial is admitted only after the complete combined word satisfies
both positive-bound ceilings. The independent verifier uses sets for pair
scores and explicit literal instructions for the full positive replay.

Write A = E-I and B = H-I. Then

```text
E K H = K + A K + K B + A K B.
```

For each row i and column j, the independent check computes these four
terms directly using E's row supports and the original K. Since helper
pairs are disjoint, column j of B has at most one nonzero entry. This checks
all 111 * 439 = 48,729 coefficients without using the builder's packed-column
updates. The mixed term AKB has 7,031 nonzero coefficients. Removing exactly
that term from the emitted middle produces a different full D operator.

The exact middle weight decreases from 6,376 to 4,764, saving 1,612 helper
reads. Preparing and restoring 192 helpers costs 384 ADDs, leaving a net
gain of 1,228. The fixed target preparation and restoration cost 612. Hence

```text
D = 192 + 306 + 4,764 + 306 + 192 = 5,760 ADDs.
complete word = 5,760 + 6,220 = 11,980 ADDs.
```

The same helper pairs used alone on K would have middle weight 13,772 and D
cost 14,156, saving 3,929 against the original D. Adding that standalone
saving to PR915's 11,097 would suggest 15,026, which is incorrect for this
composition. Its actual saving against PR589 is 12,325. This is why the
combined matrix and full bill are rebuilt.

## Full-word positive bounds and resources

Replace each signed scalar ADD by addition of nonnegative input bounds.
Copies inherit their source bound and erasures reset the copy slot. Record
the greatest coordinate at every prefix, separately for the forward word
and its reverse, interchanging copy and erasure roles. This triangle-
inequality calculation bounds signed execution; it does not use F2
cancellation. Each instruction is counted and each temporary copy is paid.

The builder computes whole-macro bounds, whose coordinate maxima occur at
their final positive addition because donors are distinct from destinations
and unchanged during a macro. The verifier lowers all individual additions,
copies and erasures. The unchanged C++ native checker gives a third replay.
All agree on F = 71,907 and B = 10,562,318 for the candidate. Both exceed
their parent values and are charged rather than inherited.

Every accepted partial word obeys `64 F^3 B^2 < 2^104` and
`2^18 F^5 B^4 < 2^192`. These caps were declared before nomination. The local
bound is 102 bits, and the nine-stage bound is 192 bits. The latter is
strictly below 2^192 by
`4716451243325510895298044774700760932455158103238770688`.
Only about 0.075% of that numerical ceiling remains. verify.py binds the
nine-stage formula to the source's `2^nb F^(K+1) B^K`, at K = 4 and
nb = 6(K-1) = 18, and reproduces its baseline 177-bit receipt.

There are 439 existing helpers and nine retained rank-seven totals. Every
register's MOVE path, the COPY/ERASE subsequence and the paid histogram
`{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` remain unchanged; the rank
mass is 5,129. No source access, scratch register, frame change, recursive
child or copied total is added. At 5/9/11 stages the new ADD savings beyond
PR915 are 6,140 / 11,052 / 13,508. Against PR589 they are
61,625 / 110,925 / 135,575. Existing bridge costs are 666 / 1,998 / 2,664,
and fresh-copy counts are 45 / 81 / 99.

## Coverage and remaining work

The finite search completes all 192,282 ordered pairs and the single sorted
greedy pass. There are 2,298 positive pairs, 192 accepted pairs, 2,106 overlap
skips and no bound rejects. No neutral detours, matching optimum, target
reselection or general circuit optimality is asserted.

Exact boundary tests cover every source, target and helper column in both
directions for the original, parent and candidate words. In particular,
omitting target preparation can pass helper-only columns but changes dirty
targets; omitting helper preparation can pass clean-helper inputs but changes
dirty inputs. Controls explicitly demonstrate both failures. Disjoint helper
undo order is immaterial, so the order-failure control concerns the
overlapping target basis.

The finite native checks do not emit the whole hosted supplier or recompute
its complete invoice. Integration must accept the semantic D contract,
rebuild and audit that hosted supplier, recompute all finite costs and
precision allocations, and rerun the outer assembly. These are the remaining
obligations for using this candidate in a conditional bound. The inherited
common-label realization and analytic assumptions remain in force.
