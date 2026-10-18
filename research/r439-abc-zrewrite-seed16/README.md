# Seed16: commuting rewrites on the complete ABC/star-D bit circuit

**Construction / finite circuit improvement.** Applying 55 same-frame
Steinberg 3-to-2 rewrites to the complete pending PR1122 circuit reduces
**10,652 to 10,542 ADDs**. This measures the resulting full word, including
its rebuilt literal cleanup; it does not add predecessor savings on different
words. No new kappa, paid-moment gain or selected-frontier change is claimed.

| Complete invoice | Frozen PR1122 | This candidate |
|---|---:|---:|
| D / A / scatter / B / C ADDs | 5548 / 1706 / 527 / 800 / 2071 | 5548 / 1652 / 527 / 799 / 2016 |
| All scalar ADDs | 10652 | 10542 |
| Positive forward prefix F | 15223 | 13721 |
| Positive reverse prefix B | 3910388 | 3663878 |
| Local precision bits | 92 | 91 |
| Nine-stage precision bits | 176 | 174 |
| Actual E8 paid rank mass | 5129 | 5129 |
| Dirty local input columns | 661 | 661 |
| Retained COPY / ERASE lifetimes | 9 / 9 | 9 / 9 |

Every ordered register MOVE path, COPY/ERASE record, source-access operation,
helper stock, restoration obligation and paid recursive rank histogram is
unchanged. The 439 helpers and nine rank-seven copied centers remain charged.
The complete staged ADD invoices, including bridges, are 53376 / 96876 /
118626 for five / nine / eleven stages. These are finite scalar savings;
unchanged paid ranks leave the bit moment unchanged, and the selected
assembly's complex constraint continues to bind.

## Reproduce

From the repository root, with Python3.9+, a C++17 compiler and Boost headers:

```sh
BOOST_INCLUDE=/path/to/boost python3 -I -B research/r439-abc-zrewrite-seed16/native.py
```

Expected final output:

```text
PASS_R439_ABC_ZREWRITE_NATIVE: 2 words; 5/9/11 stages; 96 bridge controls; rank_mass5129; no_new_kappa
```

This one command independently reconstructs the witness and checks
`CERTIFICATE.json`, then freshly exports both words, compiles the pinned native
checkers and reproduces `NATIVE.json`. It checks all 883/1327/1549 formal columns
at 5/9/11 stages, every paid rank, all 45/81/99 fresh center copies, all bridges,
and 96 omitted-bridge controls. The exact local and nine-stage formulas are
bound to the pinned source AST. Eleven-stage endpoint coverage does not assert
192-bit admission for that stage count.

A quick standard-library replay, also tested with optimization enabled, is:

```sh
python3 -I -B research/r439-abc-zrewrite-seed16/verify.py
python3 -I -O -B research/r439-abc-zrewrite-seed16/verify.py
```

Both print `PASS_COMPLETE_WORD_REWRITE_AND_PRECISION moves 55 ADDs 10542`.
Discovery regeneration is `python3 -I -B research/r439-abc-zrewrite-seed16/search.py`;
it rewrites only the three discovery artifacts in this package. Compare decoded
canonical payloads, not newly compressed-container bytes. No external Python
packages are required. The tested environment was macOS, Python3.9.6, Apple
clang21, Boost1.87.0 (`BOOST_INCLUDE=/private/tmp/boost_1_87_0`). Native build
logs can be retained with `--output NEW_DIRECTORY`; the default uses a temporary
folder and leaves repository sources unchanged.

## Search domain and new evidence

The assignment was one fresh OS-random draw, **seed16**, bit-supplier track.
`CLAIM.json` records three considered tasks, the favorable complete-cost budget,
timing, scope and local coordination receipt. No pinned sprint coordination
issue existed; open PRs and discussions were checked. The new object is PR1122's
complete A/B/star-D word. PR1127 investigates the PR589 word and explicitly
leaves application to this composed lineage as future work.

Search exhausts distinct-register triangle occurrences in the current A/B
z-program, restricted to one section and strictly commuting intervening
transvections/read barriers. Greedy windows run right to left; SHA256 of
`16:b:a:x` breaks ties. Stop at a filtered fixed point or 60 rounds, without
restarts. Fifty moves were accepted in round 1 and five in round 2; round 3
exhausted 417 occurrences: 79 cross-section and 338 noncommuting, with zero clear
candidates. Two earlier candidates were skipped because their edges were already
consumed. `SEARCH-LOG.json` contains the complete per-round census. This fixed
point is neither a globally shortest circuit nor an impossibility theorem.

All 55 accepted triangles have one common physical frame (54 in A, one in B).
`MOVES.json` names exact donor-group occurrences; `verify.py` does not import
`search.py`. The discovery adaptation fixes value-based `list.index/remove`
lookup of duplicate equal gates by selecting their occurrence and moving the
actual object. Trial failures before that repair were implementation failures,
not counterexamples to the algebraic identity.

The predecessor discovery's frame-label cardinality is not E8 vector-space rank.
The retained `frame_label_profile` is only auxiliary search bookkeeping; its
large indices are not paid dimensions. Actual rank mass 5129 and the complete
paid histogram are obtained from the owning/native E8 checks in `NATIVE.json`.

## Concurrent overlap

Before submission, open PRs were refreshed through #1199. Gareth Davidson's
concurrent [PR1188](https://github.com/CrocSwap/integer-mult-bounds/pull/1188),
head `6e142e72e94515566e87c964c0fca39eea93156f`, reduces the same PR1122 word to
10492 ADDs using exact five-wire window programs. This triangle result is not
an ADD-count record. Its independently checked precision tradeoff is distinct:

| Complete result | ADDs | F | B | Exact nine-stage envelope |
|---|---:|---:|---:|---:|
| PR1188 five-wire programs | 10492 | 13667 | 3758418 | 24941709210337926871896158204497246778939630375927808 (175 bits) |
| These commuting triangles | 10542 | 13721 | 3663878 | 22973795977533615901914742933524089773622692690264064 (174 bits) |

`verify.py` independently replays the frozen PR1188 word's complete literal
endpoints and price, and records that exact comparison in `CERTIFICATE.json`.
Its original notice and input word are retained solely for this comparison.
The GL5 optimum/BFS certificate and its native proof are not rerun here, and
savings from the two sibling programs are not assumed additive.

Concurrent PR1181 supplies a PR1015 retention/credit receipt and clarifies that
PR1062 is already retained in main. PR1194 supplies a pending semantic-D scalar
contract proof for the PR1062 word; this package does not review or adopt it.
The original syntactic flags and selected-supplier obligations remain explicit.

## Sources, scope and inherited obligations

Exact repository base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.

- Gareth Davidson (@bitplane), PR1122, head
  `a2551e70fce0cc34348f50f1a94e7cc4c80bbcbf`, supplies the frozen complete word.
- Aaron Wang (@navinor), PR1127, head
  `2e9dc9d3356a6b7258ed869ddcee46352907f746`, supplies the discovery pattern.
- Their unchanged files and original notices are retained in `vendor/`.
  These archival scripts are reference sources; use the new package's entry
  points, whose root paths and complete pins are adapted for this layout.
- `SOURCES.json` binds 17 unchanged repository dependencies and all retained
  predecessor and comparison files. Candidate canonical SHA256 is
  `85df062ca4cdffc17113fe12e32588db91dc950c1ec9a089b59920a3be17e353`.

At this base the selected certificate remains PR1094,
`research/community-frontier1094-audit/ASSEMBLY.json`, SHA256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`,
with kappa `836330098538459/500000000000000000` and maintainer review
`docs/research/community-batch1099-review.md`. Pending supplier constructions
are not accepted frontier records.

The star-D lineage retains **false** syntactic
`H2_D_frame0_targets_from_helpers` and `K_equals_D`, while all other owning H/K
checks pass. Complete dirty endpoints and scalar precision do not supply the
missing semantic-D supplier interface proof or prove the full conditional
integer-multiplication theorem. No native acceptance predicate is disabled.
`PROOF.md` gives the scoped algebra and exact envelopes; `NOTICE.md` credits the
predecessor chain and substantial AI assistance.
