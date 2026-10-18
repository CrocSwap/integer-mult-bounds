# Complete representation domains for the simple seven-source search

Every simple restored universal word in the pinned search's A/B multiplicity
classes has a representative in its low-template, high-path, gap and initial
domain construction. This closes the **representation** part of
[PR3244's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19002964).
It does not certify a completed search or the full `f(7)=24` claim.

The executable subject is conorholds'
[`cycle_search.cpp`](../connector-covering-code/cycle_search.cpp), SHA256
`597844fc32cde19c1d4104633fa6d3eb0d28c1ca140f8f3d2ba2cb632ecd30d1`,
on canonical main `463113d675af7410ac91d53a4fed51ec6494eb9a`.
Predecessor [PR3224](https://github.com/CrocSwap/integer-mult-bounds/pull/3224)
checks capacity; [PR3244](https://github.com/CrocSwap/integer-mult-bounds/pull/3244),
head `5964d7f22ad9cd9c27a1d2eb0b897f52b9425a13`, checks propagation and the
incidence of *emitted* templates. Neither establishes that the emitted
representation domain covers every allowed word. Their executables are not
dependencies of this package, and their findings are not rerun here.

## Contract and result

A word toggles one coordinate of `F2^7` at each step. Its prefix set contains
the states immediately before the steps. It is restored when its final state
is zero, simple when its prefix states are distinct, and universal when their
pairwise XORs cover `F2^7`. The two classes are:

| Pattern | Three high-coordinate counts | Four low-coordinate counts |
| --- | --- | --- |
| A | `(6,4,4)` | `(2,2,2,2)` |
| B | `(4,4,4)` | `(4,2,2,2)` |

These are premises, not an assertion that all possible seven-source words
belong to these classes. Full-word rotation/reversal and permutations among
equal-count coordinates are allowed. The proof concerns representation before
`capacity` and `propagate`; those are separate soundness obligations.

The independent checks establish exact set equality, not just matching totals:

| Domain | Independent enumeration | Source result |
| --- | --- | --- |
| Low A | All 2,520 labeled multiset words; 624 universal | Exactly 5 symmetry orbits |
| Low B | All 18,900 labeled multiset words; 7,860 universal | Exactly 77 symmetry orbits |
| Simple high paths from zero | All vertex sequences in `Q3`; 112 paths | Exactly 106 signatures |
| Translated high candidates | Every signature at each of 8 origins | Exactly 848 candidates |
| Initial domains | Both patterns, all first/second lengths 0..7 | 256 exact comparisons |
| A gap vectors | Eight entries in 0..7 summing to 14 | All 102,552, in the same order |
| B gap vectors | Ten entries in 0..7 summing to 12 | All 286,780, in the same order |

The 106 high-path classes comprise 100 singleton and six two-path classes.
All 82 native template constructors execute successfully before their rows
are admitted to the comparison.
All six nontrivial replacements are also checked inside a restored full-word
fixture at all eight high origins. The fixtures need not be simple or
universal: their purpose is to test preservation of the entire prefix set,
endpoint and coordinate counts under the replacement.

## Representation proof

**1. Project and choose a low orbit.** Delete the high-coordinate letters of
an allowed full word. The resulting low word is restored with the tabulated
counts. Every full prefix projects to a low prefix, so universality of the
full word implies all 16 low differences occur. Rotation of a restored word
translates its prefix set, reversal reverses the closed walk, and coordinate
permutations are invertible linear maps. Each preserves simplicity, restoration
and difference coverage. In B the four-use low label is fixed; the other three
labels may be permuted.

The Python oracle assigns position subsets to each label, without the source's
first-appearance restriction. It constructs complete group orbits using every
allowed permutation, both orientations and every rotation. The exact minimum
representative of each orbit equals the source output. In particular, B words
beginning with a two-use label are included. The orbit sizes are A:
`48 x 1, 96 x 2, 192 x 2`; B: `30 x 2, 60 x 20, 120 x 55`.
First-appearance renaming used by the source yields the lexicographically
smallest allowed relabeling, so it agrees with this explicit group action.

**2. Split into high paths.** Rotate at a block boundary and write the full
word as a high run followed by one low step, repeated 8 or 10 times. The low
state is fixed during a high run. Simplicity therefore makes each run a simple
path in the eight-vertex `Q3`, including its initial and final high states.
It has length between zero and seven. Its endpoint is a prefix state before
the following low step, so the entire visited high set is part of the block's
full prefix set. Empty runs are allowed and contribute one prefix state.

**3. Compress only by sufficient data.** Translate a high path to start at
zero. Its signature is `(visited vertex mask, final vertex, three coordinate
counts)`. Replacing it by another path with that signature preserves its
translated prefix set and final state. Later block origins therefore remain
unchanged, as do all coordinate totals. Replacing any or every block preserves
the full prefix set, restoration and simplicity, including disjointness of
blocks with the same low state. Hence it also preserves universality.

The independent oracle lists all ordered subsets of the seven nonzero vertices
and keeps precisely those with Hamming-adjacent successive vertices, rather
than using the source's coordinate DFS. It checks every source signature,
every retained representative and all eight translations. Order is genuinely
discarded: `[1,0,2,0,1,0,2]` and `[2,0,1,0,2,0,1]` share signature
`(255,1,3,2,2)`. The proof above explains why this collision is safe.

**4. Enumerate gaps and include the starting candidate.** The high-run lengths
sum to 14 in A and 12 in B. `Engine::enumerate` visits every vector in
`{0,...,7}^blocks` with that sum exactly once: at each recursive level it tries
every allowed next entry, and accepts a terminal prefix exactly when the
remaining sum is zero. The independent oracle chooses separator positions
(stars and bars), filters entries above seven and compares the complete ordered
byte stream. Inclusion-exclusion independently gives the same cardinalities:

`sum_j (-1)^j binom(blocks,j) binom(total-8j+blocks-1,blocks-1)`.

Normalize the high starting state to zero. Each high step reverses Hamming
parity; low steps leave high parity unchanged. Thus the parity required by
`domains_for` is exactly the parity of the preceding gap sum. The first domain
requires origin zero; later domains allow every origin of that parity. The
translated candidate is present by step 3. The 256 source comparisons exercise
every first-domain length and every later-domain length/parity combination in
both patterns. Although they use the first two slots as representatives, the
source loop uses only the gap length, the carried parity and whether the slot
is first. This last observation is a source-inspected induction, not an
exhaustive test of every position in every composition.

Together these steps give an admitted representation for every allowed word,
up to the stated symmetries and safe path replacement. They do not prove that
later pruning or branching exhausts all those representations.

## Reproduce and failure controls

Requires Python 3.12 and a C++17 compiler (`CXX`, default `c++`); no Python
third-party packages. Builds and captures use a private temporary directory.
Direct replay needs only this package and the two declared inputs, not Git.
Local ordinary and optimized replays used CPython 3.12.12 and Apple Clang
21.0.0 on macOS arm64. The dedicated Linux workflow declares the native build;
hosted CI is separate from this local evidence.

```sh
python3.12 -I -B scripts/research_package.py --package research/connector-domain-completeness
python3.12 -I -O -B research/connector-domain-completeness/verify.py --controls
```

[RESULT.json](RESULT.json) contains the deterministic counts, complete-domain
digests and a quotient collision. Normal replay compares against this receipt;
`--emit` prints a newly computed receipt without overwriting it.

The catalogue and initial domains are read from an unchanged, compiled private
snapshot of the pinned C++ source. **Gap enumeration uses two explicit,
uniqueness-checked instrumentation replacements**: emit a gap at the existing
composition counter; return at the capacity call. This retains the recursive
loop, terminal test and bounds while bypassing capacity and all word search.
The claim about the original loop also depends on the written source
correspondence above. The instrumentation is not a full native census.

Four compiled semantic mutants remove a low orbit, discard path counts, reset
the carried starting parity, or exclude length-seven gaps. All must be rejected
by the independent oracle. Truncated catalogue/gap streams and an ambiguous
instrumentation anchor must also fail. Explicit Python checks remain enabled
under `-O`. Input hashes are checked before compilation.

## Limits

This is author-checked executable and written evidence, with a separate AI
worker's low-word/path enumeration agreeing; it is not independent human or
formal-kernel verification. The retained scientific baseline and selected
frontier are unchanged. No full B census, complete `f(7)=24` validation, new
supplier, physical cost reduction or new kappa is claimed.

## Open next questions

The remaining search obligation is to connect complete domain coverage to the
actual branching and exhaustion receipts: inspect every leaf/abort transition
and bind all requested template IDs and flags to a complete, source-pinned
run. A useful first step is a small explicit Cartesian-domain oracle for
`Engine::search` with successful, unsatisfiable and interrupted controls; it
should precede a separately budgeted independent full B run. Capacity and
propagation findings in PR3224/3244 remain separately scoped evidence. The
literature/classification, multiplicity reduction and non-simple branch also
remain outside this audit. No further census is automatically proposed.

## Credit

Submitted for @krzysztofwojt with substantial OpenAI Codex assistance in
investigation, proof, implementation, checking and writing. A Luna worker
performed read-only overlap extraction and a separate low-word/path enumeration;
the primary agent checked its counts against the production replay. New material
is Apache-2.0.

Credit conorholds for the source construction and search; commdata2338 for
PR3224's capacity audit; Nick Petalas for PR3244's propagation audit and the
released handoff; Nicholas Stone for the parity correction; Aaron Wang for the
earlier word/set engines; James Reed for the false-prune audit; Ross Richardson
for the paired-readout model; and Douglas Colkitt for the retained framework and
Gray upper witness. Their source notices and frozen evidence are unchanged.
