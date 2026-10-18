# Coupled partial read exchanges: a finite negative result

**Attempted complex-supplier improvement; no new kappa.** On the pinned
P6k4 word underlying Jeremy Kothe's [PR #699](https://github.com/CrocSwap/integer-mult-bounds/pull/699),
we enumerated **175,456 two-pair group/mask cases** and a further **27,344
three-pair cases**. Every candidate violates a target hyperplane under the
specified frame-repair policy. Thus none reaches scalar or global admission.
This closes the stated finite search, not arbitrary multi-pair rewrites.

The experiment starts from exact promoted-word content
`0390ec65dc4d47df1887aabdc2ec5b6ddea3cfc8e65582873fdfeba81d100073`.
It compares against the existing four-exchange SW4 word
`d232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59`.
Both are freshly reconstructed from pinned sources. The main repository still
selects #626/#543; #699's stronger bound is a pending conditional contribution.

## Why this could have improved kappa

PR #699 exchanges reads between an entering helper h and a register r after
`h += r`, adjusting target pre-reads so that the dirty initial value of h is
compensated. It finds four favorable full single-pair exchanges. Its search note
explicitly leaves combinations of partial exchanges across different pairs open.
A change that is frame-illegal alone might be repaired by another change that
shrinks a relevant frame. We test that possibility directly.

The fixed SW4 local paid profile is
`{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}`. Its helper residual width is
3778 and rank mass is 5634. With helper identities and start/end frames fixed,
the complete global profile is 72 times the local profile plus idle children
`{1:1, 3:1, 44:1, 48:2396}`. All source, target, center, tail and helper-end
climbs remain charged. This would permit reuse of the existing owner map;
scalar-operation savings alone would not improve the recursive bound.

The unchanged #589 bit supplier leaves room above #699's complex rate. At the
reported complex endpoint `0.001663428754540205730067`, replacing the entire
SW4 recipe on bare P6k4 would need a local weighted-cost reduction exceeding
about `0.00698679`. Our search instead retains known exchanges on untouched
pairs and compares the jointly refitted profile directly with SW4. Floating
arithmetic is only a nomination aid; every candidate here fails an exact binary
frame check before any floating score is used. No new global moment is claimed.

## Exact search class

An eligible pair (h,r) satisfies the following rules in the original B section:

1. h is an entering helper. Its first B write is `h += r` with coefficient 1,
   where r is not a target. Earlier B uses of h are target pre-reads only.
2. Movable reads write a target from h or r, after that copy and before the next
   write to either h or r. An h-to-r change requires a unique literal matching
   opposite-coefficient pre-read of h; that pre-read is deleted. An r-to-h change
   inserts its opposite-coefficient pre-read immediately after h's last existing
   pre-read, or at the copy if no pre-read exists.
3. All indices refer to the original input word. Combined edits are applied
   once, not sequentially refitted. Conflicting replacements or deletions are
   rejected. Known SW4 moves on pairs outside the selected group stay fixed.
4. A moved or inserted gate takes the join of its current operand frames. Every
   untouched B gate retains its original frame as a lower bound and also joins
   its current operand frames. Early-tail frames retain their original lower
   bounds. All helpers keep their original identities and start/end frames.
5. Every selected pair uses a nonempty subset of its movable reads, and at least
   one selected pair is partial. All-full combinations are outside the new class.

There are 54 eligible pairs: 38 have four movable reads, eight have two, and
eight have one. Their 602 nonempty single-pair choices recover the historical
38 legal / 564 cap-rejected split on this current input. Counts in #699's
historical P6k3/NP notes are not assumed; the checker regenerates them on P6k4.

| Domain | Selected groups | Group/mask cases | Target-cap rejections |
|---|---:|---:|---:|
| All unordered pairs of eligible pairs | 1,431 | 175,456 | 175,456 |
| Connected triples in the direct-target overlap graph | 16 | 27,344 | 27,344 |

For a group with move counts m_i, the number of choices is
`product_i (2^m_i - 1) - 1`: remove only the all-full choice.
These count parameterized cases, not distinct completed rewrites. Retaining
known full SW4 moves outside a selected group means different group/mask choices
can produce the same completed recipe, including across the two rows. Every
reported case is replayed; no uniqueness claim is made. An initial shared-direct-
target two-pair screen covered 5,840 cases already included in the first row and
is not included again in the 202,800-case total.

The three-pair follow-up is deliberately narrower than all triples. Its graph
joins two pairs when their movable reads directly touch a common target. It has
16 components of size three and six isolated vertices. **These are not proved
independent circuit components:** downstream target-to-target gates can connect
pairs whose direct target sets are disjoint. The exhaustive two-pair result
includes all such pairs; the triple result covers only the stated 16 groups.

## Reproduce offline

Python 3.11+ and the standard library are sufficient. From the repository root:

```sh
python3 -B -I research/complex-read-exchange/verify.py
```

The command reconstructs the known SW4 word, re-enumerates both new domains,
and independently replays every rejection. It checks deterministic evidence
against EXPECTED.json and runs mathematical failure controls. No optimizer,
network, or third-party package is used, and no repository file is rewritten.
Execution timings and tested Python versions are recorded in VALIDATION.md.

The primary implementation uses reduced binary bases. The independent checker
uses explicit sets of all vectors in each subspace, independently discovers the
eligible pairs, and checks the exact group/mask traversal and first refusal of
every candidate. Failure-site hashes bind the ordered per-candidate evidence;
the independent witness hash also binds an explicit vector outside the target
hyperplane. These hashes summarize recomputed evidence, not replace it.

As positive controls, both implementations reconstruct the known SW4 word byte
for byte. The independent engine checks its B-end scalar map with exact rational
arithmetic on all 728 input columns and recounts the full frame profile. These
controls distinguish rejection of the new class from blanket rejection.

## Scope and provenance

A frame F used by target t must lie in `u_t^perp` over F2. A vector x in F with
`x dot u_t = 1` is a concrete reason that a candidate is inadmissible. Both
implementations find such violations for every member of the stated domains.
This finite result depends on the pinned word, eligibility/insertion rules,
fixed untouched SW4 moves, and the inherited frame-floor policy.

It does not exclude arbitrary triples or larger groups, alternative pre-read
positions, simultaneous full exchanges, changed scalar factories, relaxed frame
floors, moved boundaries, other helper roles, or a different decoder. No candidate
passed frames, so no new wrapper, phase, owner, invoice or outer-assembly admission
was attempted. The known baseline's source reconstruction and local audits are
recorded separately from the search. Finite checks are not a proof-assistant
formalization or a proof of the full multiplication theorem.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. SOURCE.json pins the
reconstructed input and inherited recipe; RECONSTRUCTION.json records the fresh
baseline replay. CLAIM.md records deliberate track selection, OS seed 21 and the
single evidence-driven follow-up. NOTICE.md and retained input notices credit
Jeremy Kothe, BRoute's read-exchange construction, the upstream supplier authors,
and substantial OpenAI Codex assistance. The selected frontier and upstream/
are unchanged. This contribution is separate from completed PR #666.

At handoff, the overlap refresh covered 586 open PRs through #767. Concurrent
[#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741) improves the full
SW4 word by raising eight B-gate frames and coalescing paid jumps. That changes
frame annotations without a partial read exchange and is outside this search.
Its reported stronger bound is not ours. #699's head advanced to
`f042731cb332359166e8215839f9a3da28c46c5b` through a README/MANIFEST-only
change; the construction and input bytes used here are unchanged.
