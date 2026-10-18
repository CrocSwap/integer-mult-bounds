# R439 helper-star restoration cannot cross the fixed continuation

**Exact finite obstruction, with a written subset proof; no new κ.** None of
the nonempty restoration subsets in the three words below can move from the
end of D to the full-frame end of C while every other gate stays fixed.
Every dirty helper is an arbitrary input. Merely restoring helpers eventually
does not protect the targets read during the intervening continuation.

| Pinned word | Complete ADDs | Restoration edges | Centers | Eligible nonempty subsets |
|---|---:|---:|---:|---:|
| PR967 helper stars | 11,783 | 221 | 157 | 0 of `2^221 - 1` |
| PR1062 composition | 11,515 | 221 | 157 | 0 of `2^221 - 1` |
| PR1062 candidate | 11,500 | 236 | 162 | 0 of `2^236 - 1` |

The exclusion covers every subset by the distinct-leaf argument below, rather
than claiming to enumerate exponentially many words. The separately written
literal verifier also checks **all 678 single-edge relocations**, forward and
reverse, on **all 661 formal input columns**, and all 678 leaf-input witnesses
with a direct Boolean interpreter. Every witness changes at least eight target
outputs. It also replays the all-edges relocation in both directions for each word.

The scalar count, all register frame paths, 2,911 MOVEs, nine rank-seven COPYs
and rank mass 5,129 remain unchanged even for the invalid all-edges relocations.
These cost checks do not imply correctness. The original syntactic H2/K failures
are inherited; a terminally modified C also changes the literal H4 representation.
No checker predicate is changed, and no replacement supplier is adopted.

## Exact domain and proof

Work over F2, in chronological order, with source vector `x`, target vector `y`
and arbitrary dirty-helper vector `h`. The pinned D has boundary

`D(x,y,h) = (x, y + K h, h)`.

The raw continuation `W0 = (A, scatter, B)` has target boundary
`y -> y + x + K h` and an invertible source/helper block `U` with no target
dependence. Its literal cleanup C applies `U^-1` to those source/helper registers
and never writes targets. The verifier extracts the actual raw response K,
checks semantic D against it, checks the literal cleanup and complete arbitrary
input boundary, and compares K with the retained PR589 response. It imports no
predecessor executable code.

Choose a subset of the **final helper-restoration gates** in D. An edge is
`h[a] ^= h[b]`, with center `a` and leaf `b`. Centers and leaves are disjoint,
each leaf appears in exactly one edge, and each center has at most two leaves.
Every edge has its identical preparation gate at D's beginning. All these
helper gates commute. For the chosen subset write

`S = I + N`, where `N = sum e_a e_b^T`.

Since every column of N is a leaf and every row a center, `N^2 = 0`, hence
`S^-1 = S`. Omit just the chosen restoration gates; all target gates still run
before this final restoration region. D's new boundary is therefore

`(x,y,h) -> (x, y + K h, S h)`.

The fixed raw continuation now gives

`y -> y + x + K h + K S h = y + x + K N h`.

C restores the source/helper block to `(x,S h)`. Append the identical chosen
helper gates, now at the full frame, to return it to `(x,h)`. These last gates
cannot change the already computed targets. Thus the complete modified boundary is

`(x,y,h) -> (x, y + x + K N h, h)`.

It agrees with the desired supplier boundary **if and only if `K N = 0`**.
This is the usual reader/stabilizer condition, specialized here; it is not
claimed as a new general principle.

The column of `K N` indexed by a chosen leaf b is **exactly `K[:,a]`**.
Different edges have different leaf columns, so they cannot cancel one another
as linear maps, even when they share a center. For each of the 157/157/162
actual centers, the extracted column `K[:,a]` is nonzero. Hence every nonempty
subset fails. Input `h=e_b`, with zero sources/targets and all other helpers
zero, explicitly changes the targets in the support of `K[:,a]`, while every
source and helper is eventually restored. The smallest support size is eight.

All record/register indices in [CERTIFICATE.json](CERTIFICATE.json) are zero
based. Its single-relocation records name the center, leaf, D record, first
changed physical target and support size. The response and complete witness
list are source-bound by deterministic hashes and exact input pins.

## Failure controls and scope

PR1017 correctly showed that all final helper-restoration omissions are
invisible at the **D target boundary**. This audit follows their effect through
the whole continuation and eventual restoration; it finds no bug in PR1017.

Two common weaker tests falsely accept the terminal relocation:

* With all helper inputs zero, even an invalid single-edge relocation has no
  target defect, including on the tested nonzero source/target fixture.
* Moving both edges of a two-leaf star passes the complete all-ones input:
  `h[b1]+h[b2]=0`. It still fails the leaf-basis inputs. The receipt gives each
  word's concrete center-234 pair (D records 956/1127, or 986/1157).

Controls also check the target-only D observation, omitted eventual helper
restoration, wrong-direction terminal undo and a synthetic nonkernel reader.
A **nontrivial positive fixture** with `K[:,a]=0` accepts the relocation on all
16 arbitrary four-register inputs. This prevents overstating the obstruction
as a general prohibition on delayed restoration. Five on-disk corruption
controls and an isolated optimized relocation accompany the mathematical checks.

This domain fixes D's target compensation, the entire A/scatter/B continuation,
the old C and the moved gates' operands. It excludes altered compensation,
conjugated restorations, added target repairs, other insertion cuts, other words
and cross-call wrappers. There is no unrestricted restoration, circuit-optimality
or multiplication theorem. No precision bill for an adopted candidate, native
multistage replay, whole-hosted emission/invoice, all-size/common-label compiler,
tape, analytic transfer or Lean proof was performed. Source binding and local
frame accounting do not establish those physical interfaces.

## Reproduce

From the repository root, Python 3.12+, standard library only:

```sh
python3.12 scripts/research_package.py --package research/r439-terminal-star-restoration
```

Or run the verifier directly, including its optimized mode:

```sh
python3 -I -O -B research/r439-terminal-star-restoration/verify.py
python3 -I -O -B research/r439-terminal-star-restoration/test_package.py
```

Expected verifier output:

```text
PASS_R439_TERMINAL_STAR_RESTORATION words=3 singletons=678 forward_reverse=1356 eligible_subsets=0 no_new_kappa
```

Local validation passed on Windows x86_64 with CPython 3.12.14: the registered
replay, metadata/source pins and six focused tests, including five on-disk
corruptions and a minimal optimized export. Hosted CI is separate.

Default replay compares the entire committed certificate and writes no evidence.
`--write-certificate` explicitly regenerates it. [SOURCES.json](SOURCES.json)
pins current-main inputs at `c5108f0f68d482e5712a8e26a5978d47762dfc16`;
[TASK.json](TASK.json) records the original card, nonce, changed scope, bounded
stop rule, overlap and verification environment. Later selected-frontier changes
do not invalidate historical catalogue/selected-record provenance.

## Open next questions

Can a **different** boundary word realize the conjugated correction, including
target repairs, cheaply and with legal target/helper frames? That could turn the
excluded identical-gate relocation into a usable changed interface. First derive
the actual correction `K N` and `U S U^-1` for one pinned edge, then price every
repair and frame transition before searching. Target final frames and full-frame
helpers may block the needed reads; physical hosting and the unchanged recursive
profile also remain binding issues. This audit does not assert headroom for that
larger construction. The structured handoff is in TASK.json.

## Credit and task selection

One OS nonce `095c7b0b01f2597dd112ac3d7e2abd5b` selected bit-mechanisms,
`bit-helper-contract`, dirty-input/cut counterexample method, priority revision 2.
The prescribed PR1062 first example and selected-source baseline passed.
The original semantic-D scope is already covered by woklerx's PR1194
(`2e39c98238f543d988f9efc1b076590a4b780dca`) and Arham Tahir's PR1311
(`a2875c1834b9c9ef42a84eda4890d5462cc98fa5`). This explicitly changed adjacent
scope checks a nonrestored D-helper state across a fixed continuation.
[Discussion 1565](https://github.com/CrocSwap/integer-mult-bounds/discussions/1565)
records the claim and handoff. The complete entry overlap snapshot covered 713
open PRs and 217 Discussion records. The final complete refresh at 03:15 UTC
covered 728 open PRs and 225 Discussion records, with the cited pending heads
unchanged. All seven pinned blobs and repository guidance stayed identical at
refreshed main `ddb4371c16a5a5de9e363afa8c0d6d7c27429e3c`. Coverage limits are retained
in TASK.json.

Credit Sricharan Vagvala / PR967; Sagar Thakrar / PR1062 and the target-basis
lineage; Gareth Davidson / PR915/926; Aaron Wang / PR1015; Ross Richardson /
PR923; DreamingOfClouds / PR589; eumemic / PR555/543; and the retained scalar
compiler/checker lineage. woklerx's PR1017 owns the D omission atlas. mightyOil
(Philipp)'s PR1203 (`38459854fd5bb93099871a84324413bd0e338d8e`) and Sagar
Thakrar's PR1199 already describe the general reader/stabilizer condition; no
priority for that identity is claimed. Their mechanisms are credited as context,
without importing pending executable implementations or assuming acceptance.

Prepared by **Arham Tahir with substantial OpenAI Codex assistance** in reasoning,
implementation, verification and writing. No subagents or independent human
review. New files are Apache-2.0; predecessor bytes/notices remain unchanged.
