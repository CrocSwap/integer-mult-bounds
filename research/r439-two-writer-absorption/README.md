# PR1062: two single-donor corrections cannot absorb a helper-star restoration legally

**Exact restricted interface result; no new circuit, supplier or kappa.** On the
pinned 11,500-ADD PR1062 R439 word, omit one terminal helper-star restoration
`a ^= b`, and toggle one donor in each of two existing phase-A writes of `a`
before its first read. There are **314 exact arbitrary-dirty completions**,
including **52 with one fewer scalar ADD**, but **every completion violates the
unchanged monotone rational-frame law**. Each rejection has an explicit old-frame
source label outside the proposed receiving frame's rational span.

This answers only a bounded part of Sagar Thakrar's
[PR1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868) open question
about multi-gate splits. That predecessor already supplies the twisted-helper
contract and three legal **single-writer** absorptions. Its result is credited,
not rediscovered here. One of its actual legal moves is a positive control.

## Boundary contract and complete domain

Use zero-based physical register and A-gate indices in
`research/r439-bsection-stars-seed01/candidate.json.gz` at main
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Sources are 0–110, dirty targets
111–221, and dirty helpers 222–660. The source word has 236 terminal star
restorations. Every leaf is distinct and is never a centre.

For **each one** of those 236 edges `(a,b)` separately:

1. Remove only its final D restoration `a ^= b`. Keep the other D gates.
2. Choose two distinct original A gates `i < j`, both writing `a`, strictly
   before the first original A gate reading `a`. If A never reads it, the
   deadline is the end of A.
3. Toggle exactly one donor `s` in gate i's source set, and exactly one donor
   `t` in gate j's source set. A toggle removes an existing donor or adds a new
   one. The donor alphabet is all original source/helper registers except a:
   **549 choices at each cut**. Targets and new dirty auxiliaries are excluded.
4. Keep every other A gate, all scatter/COPY/ERASE/B/C operations, original gate
   frames, starts and final frames. The donor lists are canonically sorted;
   donor order within a common-frame XOR gate does not change the boundary.
   No new gate, frame transport, free reset, cleanup rewrite or source synthesis
   is permitted. A donorless centre gate still retains its original frame move.

The certificate lists all 236 `(centre,leaf,first-read,writers)` records. Their
writer-pair counts per edge are:

| pairs per edge | edges |
|---:|---:|
| 0 | 81 |
| 1 | 118 |
| 3 | 10 |
| 6 | 1 |
| 10 | 26 |

Thus there are **414 edge/writer pairs**, not an independently sampled set.
There are 414 × 549 = **227,286 first-donor trials**. The second donor is solved
uniquely, rather than sampled; the next argument proves this covers all
414 × 549² = 124,780,014 possible donor pairs in the declared domain.

## Exact replacement lemma

Let `r_k(u)` be the row vector giving register u's current value immediately
before original A gate k, in the 661 original dirty-input coordinates. Because
the D star suffix restores every helper, deleting `a ^= b` leaves precisely the
extra original leaf value `h_b` in centre a at the D/A cut, and no other defect.
The disjoint-star checks are material to this statement.

Before a's first read, no other register acquires the defect. Writes to a add
values independent of a, so toggling s at i adds `r_i(s)` to that defect and
toggling t at j adds `r_j(t)`. The candidate and original states agree on every
register immediately after j **if and only if**

```
r_i(s) XOR r_j(t) = e_b.                       (1)
```

Necessity follows by choosing a unit dirty-input column where the residual row
is nonzero; sufficiency follows by linearity. This is an identity over every
F2-module, not merely clean helper inputs. After that cut the unchanged
continuation receives identical scalar values. In particular, the copied totals
and their chronological ERASE obligations are unchanged. The full-word replay
checks them independently in both orientations.

Conversely, a nonzero residual at this cut cannot disappear in a legal,
unchanged continuation: ADD is invertible, COPY is injective into a clean
temporary, and ERASE is invertible on its required matching-value domain.
Consequently equality at this cut is also necessary for the complete legal
dirty boundary, rather than merely a convenient sufficient filter.

The original prefix is an invertible XOR word. Its 661 state rows are distinct
and nonzero, so for a fixed first donor s at most one register t has row
`e_b XOR r_i(s)`. The verifier builds that exact row-to-register dictionary over
the allowed second-donor alphabet. It tries every s at every eligible writer
pair. A missing row excludes every second donor; a present row gives the unique
candidate. This establishes complete coverage without a quadratic search.

Equation (1) is only a **scalar boundary criterion**. It does not imply that
its reads are legal at their proposed frames. That missing implication is the
one falsified here. It is not a defect in the existing checker or in PR1868's
explicitly frame-checked single-writer construction.

## Exact source-bound counterexample

The lexicographically first saving completion is:

```
omit D restoration: 231 ^= 459
A[9]:   [frame 6,   dest 231, donors [4]]   -> donors [4,109]
A[527]: [frame 234, dest 231, donors [459]] -> donors []
```

The first read of 231 is A[528]. Before A[9], register 109 holds `x_109`.
Before A[527], register 459 holds `h_459 XOR x_109`. Their XOR is exactly
`h_459`, so both corrections together eliminate the omitted-restoration defect
for **arbitrary dirty inputs**. Literal forward/reverse execution on all 661
columns succeeds, and the complete scalar count is 11,499 instead of 11,500.

But source 109 starts at frame 111, whose label support is `{109}`. A[9] asks
it to visit frame 6, support `{4}`. Exact rational elimination gives

```
rank_Q(line[4]) = 1
rank_Q(line[4], line[109]) = 2.
```

The required old frame is therefore not contained in the receiving frame.
There is no legal monotone climb, regardless of the perfect scalar endpoint.
All other 313 completions similarly have a checked rational noncontainment
witness, not merely a copied checker failure flag.

## Accounting

Each completion changes the complete ADD invoice by

```
-1 + (1 - 2*[s was an old donor at i])
   + (1 - 2*[t was an old donor at j]).
```

The `-1` is the omitted D restoration; C is unchanged. Exactly 52 completions
have delta -1 and 262 have delta +1. No delta -3 completion exists. None has an
admissible paid histogram under the retained frame contract; the verifier
refuses to bill an illegal path. Scalar savings cannot be substituted for a
legal recursive profile or multiplication-exponent improvement.

The source control's **complete** profile is independently recomputed from
all rational frame-rank increments plus all nine COPY ranks:
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`, rank mass **5,129**.
All nine COPY/ERASE pairs are retained. As a nontrivial positive control,
PR1868's `506 ^= 374` omission with A[288] donors changed from `[374]` to `[69]`
passes the full dirty boundary and has identical ordered frame paths and paid
profile, while reducing the scalar count to 11,499. This saving belongs to
PR1868. Both source controls' complete positive envelopes pass the inherited
strict 104/192-bit inequalities; exact integers are in `CERTIFICATE.json`.

## Reproduce

Standard-library Python 3.12, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/r439-two-writer-absorption
```

Direct commands:

```sh
python3.12 -I -O -B research/r439-two-writer-absorption/verify.py
python3.12 -I -O -B research/r439-two-writer-absorption/test_verify.py
```

The verifier prints:

```
PASS_R439_TWO_WRITER_ABSORPTION pairs=414 trials=227286 exact=314 scalar_saving=52 legal=0 columns=661 controls=7 no_new_kappa
```

`--write` explicitly regenerates only this package's certificate. Default
replay is read-only, compares every certificate field and checks input hashes.
Seven failure controls cover omitted corrections, retaining the supposedly
omitted restoration, a wrong donor, billing an illegal path and source
corruption. Seven focused tests include an independent all-eight-input Boolean
identity, exact source rows, the rational frame obstruction, and clean-helper
false acceptance of an omitted restoration. The borrowed working example
`r439-bsection-stars-seed01/verify.py` passed on CPython 3.12.12; the system
Python 3.9 attempt failed at `int.bit_count`, before the supported replay.

The registered command passed on macOS arm64 with CPython **3.12.12**, including
all seven tests and the optimized direct verifier, in **4.66 seconds** wall
time. Certificate generation took 4.32 seconds. The environment's equivalent
command is `uv run --python 3.12 --no-project python scripts/research_package.py
--package research/r439-two-writer-absorption`. An initial comparison exposed an
integer-versus-string histogram-key ordering mismatch; JSON normalization fixed
that receipt-only issue before the passing replay. No mathematical census or
source input was changed.

## Scope, overlap and provenance

The selected complex supplier binds; this audit does not change the selected
record or any frozen evidence. It neither constructs a legal two-writer word
nor rules out multi-donor splits, three or more correction gates, post-read
propagation and compensation, changed gate frames/itineraries, rebuilt A/B/C,
additional registers, or other source words. Native multistage compilation,
whole-call hosting, changed precision/tape realization, outer assembly and a
Lean multiplication theorem are not supplied or run.

The source word and unchanged checker-as-specification have exact Git/SHA256
pins in `SOURCES.json`. No predecessor executable is imported. The selected
record and catalogue are historical provenance, not moving runtime inputs.
The initial cached overlap search covered 540 open PRs including drafts at
2026-10-14 13:15:09Z and 524 discussion records at 13:10:59Z, with complete
pagination. A pre-publication offline search used the parent's newer complete
snapshot of 543 PRs at 13:23:53Z and 529 discussion records at 13:25:07Z.
Closed work is covered only by local README/TASK/ledger records; arbitrary
diffs and nested files are not searched. The precise split-absorption terms
found PR1868's open question, not a completed two-toggle census. Full bodies of
PR1868/1580/1592 and discussion1743 were read. A targeted live query before
publication confirmed PR1868 remains open at the recorded head
`6b222d01fee072bcd3a680e6a96ae7d22e13bcac`. Later claims remain possible;
these searches do not establish novelty. Exact heads and terms are in `TASK.json`.
[Discussion1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884)
records the parent-coordinated advisory scope; this package makes no priority
guarantee or public reservation.

## Open next questions

Can two writers absorb one star restoration when each may toggle a **set** of
donors? First solve the constrained row-sum equation at one actual pair of
cuts, admitting only donors whose entire subsequent frame itinerary remains
legal and pricing every ADD. No favorable legal completion or hosted invoice
is supplied here. `TASK.json` records the structured question and blockers.

## Credit and disclosure

Sagar Thakrar / **PR1868** supplies the twisted contract, single-writer census,
positive fixture and multi-gate-split question. **woklerx / PR1194** supplies
semantic-D substitution; **Arham Tahir / PR1311, PR1580, PR1592** supplies its
application and distinct terminal-deferral/compensation obstructions. The source
word is **Sagar Thakrar / PR1062**, using **Sricharan Vagvala / PR967** helper
stars, **Gareth Davidson / PR915/926** bases, **Aaron Wang / PR1015** and
**Ross Richardson / PR923** blocks, on **DreamingOfClouds / PR589** and
**eumemic / PR555/543**. The source checker and inherited frame law are eumemic's;
Zhihao Chen's PR425 and the retained scalar-interface lineage remain credited.
No earlier construction's scalar savings are claimed as new here.

New material prepared for **Adam Gall** with substantial **OpenAI Codex**
assistance in mathematics, implementation, investigation, verification and
writing. Apache-2.0. No independent human review or formal proof-assistant
verification is claimed.
