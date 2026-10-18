# A sharp limit on common S4 permutation-cut certificates

**Scoped proof-method obstruction; no new kappa.** At adjacent prices
`(2,1,2)`, the strongest nonnegative combination of role-uniform coordinate
cut ranks on *any finite permutation S4-modules* gives exactly **20** for

    diag([2143], [3142], [4231], [2143], 1, ...).

The separate scalar shortest words cost **21**. Uniformly at prices
`(beta,alpha,beta)`, with `0 <= alpha <= beta`, these bills are
`8 beta + 4 alpha` and `9 beta + 3 alpha`: the sharp method gap is
`beta-alpha`. Thus no such common certificate is tight on all 24 targets
when the exterior price is strictly higher. The actual circuit optimum
with arbitrary restored dirty workspace remains open.

This answers Ross Richardson's explicit next question in
[Discussion2570](https://github.com/CrocSwap/integer-mult-bounds/discussions/2570#discussioncomment-18956828).
It preserves that predecessor's exact twenty-target theorem and Nick
Petalas's PR2583 two-register census. It adds no word search or new
supplier. [PROOF.md](PROOF.md) gives the five-point pentagonal upper
certificate and an existing cut combination attaining it; no large cut
enumeration is needed.

## Evidence and replay

Python 3.12+ and the standard library suffice, from repository root:

```sh
python3 -I -B scripts/research_package.py --package research/s4-two-premium-cut-envelope
```

The registered commands run the primary checker, a separately implemented
Floyd-Warshall oracle, and six behavioral test groups. They check the
exact symbolic invoices, all 32 binary five-point cuts, all 24 scalar
distance/word pairs, 1,093 undeduplicated scalar words, five exact price
controls, full group-algebra endpoints with six dirty roles and all twelve
call omissions. Four actual producer mutants, an independent orientation
mutant, corrupted evidence and changed source pins reject. Normal and
optimized verifiers run read-only in a Git-free export with the pinned
inputs. Default replay writes nothing; only `verify.py --write` regenerates
[RESULT.json](RESULT.json).

These are two implementations prepared in the same AI-assisted session,
not independent human review. A direct circuit and necessary lower-bound
profiles are checked; arbitrary-role circuit optimality is not. Arbitrary
subspace cuts and nonpermutation representations lie outside the theorem.
No native realization, hosting/precision/tape invoice, selected cold replay,
formal-kernel proof or hosted CI pass is claimed.

Local registered replay passed on Windows with CPython 3.12.10; direct
optimized replay also passed with CPython 3.14.6.

## Open next questions

Can a stronger invariant or a complete formal word decide whether this
mixed tuple costs 20 or 21 at `(2,1,2)` with arbitrary dirty workspace?
This matters because coordinate-cut enumeration is now known to stop at
20. First examine equality in the inherited unit-price ordered-pair bound:
a cost-20 word would have exactly twelve paid letters and eight exterior
letters, since the ordered-pair and natural cuts already force these
respective minima and their sum is 20. A finite
search would need a separately budgeted exact alphabet and memory plan;
no further construction campaign is undertaken here. See the precise
scope and blocker in [TASK.json](TASK.json).

## Sources and credit

Scientific base: current main `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`,
priority revision 5; task-picker nonce `428618959ce92654afec0b1fcbcac0de`.
The target-specific relaxation card is refined to a changed-price
proof-method audit. [SOURCES.json](SOURCES.json) pins exact main blobs
and the public predecessor archive SHA256. Its proof, README and Apache
license are retained verbatim under [predecessor/](predecessor/README.md).

Credit Adam Gall/PR1941 and Ross Richardson/PR1966/1989 for the cut method;
Nick Petalas/PR2583 for the weighted two-role census; Ross Richardson's
`s4-permutation-cut-cone` archive for the twenty-target result and the
successor question; David Arias/PR2738 and complementary PR2577. The
pentagonal cut inequality is standard. New here are the explicit S4
separation, its mixed tuple, and the sharp price-cone method invoice.
Jerry Chen's retained [abelian metric note](../abelian-cayley-metric-scope/README.md)
uses the same standard inequality on different charged metrics; this
package imports none of its implementation.

The submission refresh found main `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`
and priority revision 6. Its changed guidance was read; this bit card,
selected record and live mathematical inputs are unchanged. The completed
scoped result is retained, with no new construction expansion.

Prepared for Arham Tahir with substantial OpenAI Codex assistance.
No independent human review is claimed. New work is Apache-2.0.
