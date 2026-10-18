# R420 adjacent A-gate exchanges have no frame freedom

**Scoped negative result. No new bit exponent or κ.** In eumemic's PR543 R420
word, each of the 1,735 commuting adjacent A-gate pairs can be reversed, but
neither gate can change its frame. This holds even if the two new frames may
be arbitrary rational subspaces, beyond the existing catalogue. Every such
single exchange preserves the local paid recursive profile.

The base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. At that commit the
[selected record](../../certificates/selected-result.json) uses #626 with
#543 and has conditional κ = `51110230636731/31250000000000000`, or
`0.001635527380375392`. Its
[maintainer review](../../docs/research/community-k492-review.md) identifies
the retained assumptions. Larger numbers in open PRs are pending claims.
This package changes no selected artifact or file under `upstream/`.

## Reproduce

From the repository root, with Python 3.11+ and the standard library:

```sh
python3 -B research/r420-adjacent-a-seed00/verify.py
python3 -B research/r420-adjacent-a-seed00/independent_check.py
```

The first command checks the pinned predecessor's exact labels, 660 symbolic
dirty-input columns and H1–H5, checks every frame-rigidity obligation, recounts
the complete local paid profile, runs eight controls and compares the result
with `CERTIFICATE.json`. Its final line is:

```text
PASS_R420_ADJACENT_A_RIGIDITY positions=2063 commuting=1735 forced=3470 gaps=0 rank_mass=5112 controls=8
```

The second implementation imports no project checker. It independently checks
the 672 frame closures and exact orthogonal complements, recomputes all
dimension equalities, and replays the entire A phase after every one of the
1,735 swaps on all 660 symbolic inputs. It also checks that every excluded
dependency pair changes the A operator when swapped. Expected final census:

```text
Forced-frame rank census: {"1": 479, "2": 360, "4": 2140, "6": 480, "8": 11}
A rank-jump histogram: {"1": 600, "2": 989, "4": 60}
```

`verify.py --print-certificate` prints the freshly computed certificate without
overwriting it. The witness digest covers canonical JSON rows
`[pair_index, [[original_frame, prior_frame_ids, next_frame_ids, lower_rank,
upper_rank], ...]]`, sorted by original pair index. Frame-ID sets are sorted.
The verifier regenerates the rows from the pinned word; the digest is a
reproduction checksum, not a substitute for the dimension checks.

## Exact search class

Choose one index `i` in `0..2062` of the original 2,064-gate A list. Gates are
original records, including single-source gates and the nine multi-source
totals. They are not flattened, factored or synthesized. A gate acts as
`destination ^= XOR(sources)` and every operand uses its gate frame.

Only pairs with neither destination in the other gate's source list are
admitted. This includes 726 pairs with the same destination. Reverse the two
records and choose both replacement frames jointly. All other A records,
the exact entry and end-of-A frames, D, scatter, B, final frames, registers,
retained totals and decoder remain fixed. Preserve H4 by mirroring the
exchange in the literal reverse cleanup C, at the full frame.

All 2,063 positions are classified: 1,735 commute and 328 have a dependency.
For the admitted pairs there are 3,470 gate-occurrences to check. The stopping
rule is completion of this finite list, with no random search or timeout.
OS assignment seed 00 selected this object from the three candidates in
`CLAIM.json`; the resulting enumeration is deterministic.

The first experiment found exactly one feasible catalogue-frame pair at each
commuting position, always the original two frames. The delivered argument
strengthens that observation to all rational subspaces, using exact lower
spans and upper intersections. No claim of catalogue completeness is needed.

## Why the frames are forced

For a chosen pair and an operand register `r`, let `P_r` be its frame immediately
before the pair. Let `N_r` be the frame at its first later A use outside the
pair, or its prescribed end-of-A frame if it has no later A use. These are
fixed independently of the two proposed replacement frames.

For either gate `g`, define subspaces of the eight-dimensional rational label
space:

```text
L_g = sum of P_r over every operand r of g
U_g = intersection of N_r over every operand r of g
```

Monotone frame paths necessarily imply `L_g ⊆ F_g ⊆ U_g`, regardless of which
gate goes first. Even when a register also visits the other gate, nesting
still puts its earlier `P_r` below `F_g` and its later `N_r` above `F_g`.
These are necessary bounds, so omitting the coupling between gates only
relaxes the proposed schedule.

For every gate-occurrence the checker establishes both containments for the
original frame `F_old` and the exact equalities
`dim L_g = dim F_old = dim U_g`. Hence `L_g = F_old = U_g` and any admissible
new frame equals `F_old`. The table gives the completed obligations:

| Forced dimension | Gate-occurrences |
| --- | ---: |
| 1 | 479 |
| 2 | 360 |
| 4 | 2,140 |
| 6 | 480 |
| 8 | 11 |

All ranks use exact rational elimination. In particular, the upper dimension
is computed as `8 - rank(sum of orthogonal complements of N_r)`. Intersecting
the sets of listed root lines would be insufficient: an intersection can
contain a direction absent from those lists. A synthetic two-plane control
explicitly exercises this case.

Every shared operand in an admitted pair uses equal original frames in the
two gates. Once those frames are forced, exchanging the gates preserves that
register's frame path after repeated equal-frame visits are removed. An
operand used in only one gate also keeps its frame path. Thus all rank jumps
and retained COPY ranks remain equal, with no numerical comparison of powers.

## Complete local cost and boundary obligations

The complete local paid profile remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, with rank mass 5,112. Its moment is
unchanged for every positive exponent, as an equality of profiles. There are
still 420 helpers, nine retained COPYs of rank 8, and 26,916 binary ADDs.
D's dirty compensation, source accesses, all other climbs, scatter, B,
restoration and final climbs have not been omitted from that profile.

The two XOR maps commute because neither reads the other's destination.
For a common destination both add unchanged source parities to the same row.
The rest of A therefore sees exactly the same values, including arbitrary
helper dirt. B and scatter keep the same input. Mirroring the two records in
C preserves its literal-reverse interface, with the same full-frame operands
and number of ADDs. Leaving C bytewise fixed would preserve the scalar inverse
but violate the syntactic H4 check; a control catches this distinction.

This is a local paid-profile statement. It does not optimize changed owner
maps, call windows, scalar prefix bounds or other nonrecursive costs. Under
the same replication and idle remainder, the global recursive moment cannot
improve from this equal local profile. We did not rerun or change the full
assembly, and do not infer a new κ.

## Controls and limits

The main verifier checks a non-root intersection, a deliberately flexible
interval, a noncommuting dependency, an accepted same-destination pair, an
unmirrored cleanup rejection, an accepted mirrored full-word swap, a
noncommuting full-word rejection, and an equal-rank wrong-frame rejection.
The independent checker additionally rejects all 328 actual dependency swaps
by comparing their exact symbolic A operators.

The conclusion covers one exchange in the original word. It does not cover
sequences of exchanges, nonadjacent transport, splitting a source list,
changed circuits, altered boundaries, other words, or improved hosting. This
is an exact finite-instance certificate with a written subspace argument,
not formal verification of the full multiplication theorem. The inherited
uniform compiler, mutable-basis/common-label realization, physical hosting,
precision, tape and analytic assumptions remain open as recorded upstream.

## Relation to concurrent work and attribution

PR661 proves a fixed-order phase-B moment bound for the same R420 word. This
package treats A, permits an order change and proves frame uniqueness rather
than comparing different rank partitions. No PR661 code is imported. PR589
searches elementary-operation transports and reframing on the punctured P111
word. Its circuit and search class differ. PR691 resynthesizes an R420 quad;
PR694 changes the frame-zero helper basis. Concurrent PR708 shares restored
operands while resynthesizing the decoder totals. Those mechanisms are outside this
gate-preserving class and are not contradicted by this result.

The source construction and independent predecessor audit are eumemic's
PR543, head `2065fe4f72a914d907f1046603f5a36f17018535`. Credit also belongs to
Dylan Crow for the PR370 format, DreamingOfClouds for the nine-stage chain
and PR589 frame-transport work, Dugongue for PR541/548 transport mechanisms,
and Rohan Arun for PR542 least-frame work. The complete earlier source lineage
remains in the predecessor's notices. `SOURCES.json` records exact input pins,
the selected context and related PR heads; context hashes are historical and
are not enforced as runtime dependencies.

Contribution by `thakrarsagar`, with substantial OpenAI Codex
assistance for the experiment, proof, implementation, independent second
implementation and review. New work is under the repository's Apache-2.0
license; predecessor notices and source files are unchanged.
