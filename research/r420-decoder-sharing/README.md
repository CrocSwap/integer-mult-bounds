# Restored sharing in R420's nine decoder totals

This finite bit-circuit construction saves **114 binary XOR additions** in
eumemic's PR543 R420 word: **26,916 to 26,802**. It changes the last nine
phase-A decoder-total gates and their literal reverse cleanup. It preserves
the complete phase-A operator on arbitrary source and helper inputs, every
register's ordered frame path, 420 helpers, nine retained totals, and the
original H1-H5 interface. **No new kappa is claimed.**

The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. At that base the
selected conditional result is #626 with #543,
`kappa = 51110230636731/31250000000000000 = 0.001635527380375392`.
The source is followed through `certificates/selected-result.json` and
`docs/research/community-k492-review.md`, rather than historical frontiers
in the bit supplier's README. [SOURCES.json](SOURCES.json) pins the reviewed
PR543 head, canonical word content, checker, generator and supplier README proof.
No existing construction or selected-frontier file is edited.

## Reproduce

Python 3.11+ and its standard library suffice for the exact local check:

```sh
python3 -B research/r420-decoder-sharing/verify.py
```

Expected final line:

```text
PASS_R420_DECODER_SHARING decoder=321->264 native_ADDs=26916->26802 saved=114 columns=660 controls=7 no_new_kappa
```

This recomputes the bounded nomination, reconstructs the candidate, checks
source pins, runs the unchanged PR543 checker and the separate set-valued
interpreter, rejects seven controls, and compares every field of
[CERTIFICATE.json](CERTIFICATE.json). Run without `-O`, because the inherited
checker contains assertions. `--show-report` prints the full certificate;
`--output /absolute/new/directory` also writes both words and the report.
Existing output directories are refused.

For native nine-stage replay, choose two new output directories:

```sh
python3 -B research/r420-decoder-sharing/verify.py --output /tmp/decoder-words
BOOST_INCLUDE=/path/to/boost CXX=c++ python3 -B research/r420-decoder-sharing/native.py \
  /tmp/decoder-words/baseline.json.gz /tmp/decoder-words/candidate.json.gz /tmp/decoder-native
```

The optional [native.py](native.py) helper binds both inputs to the canonical
word hashes in the local certificate.
It uses the unchanged record exporter, legality checker and C++ nine-stage
column checker. A C++17 compiler and Boost headers are required. Native
results and environment details are recorded separately in
[VALIDATION.json](VALIDATION.json).

## Circuit and full cost

At the start of the nine-total suffix, choose two non-retained operand
registers `a,b`. Temporarily apply `a <- a XOR b`. In each total's source
set containing `a`, toggle membership of `b`. After all nine totals,
apply `a <- a XOR b` again. The register `b` is unchanged, so this restores
the exact incoming value of `a`, including arbitrary dirty-input terms.

To check a total algebraically, let its old coefficients of `a,b` be `p,q`
in F2. Its new expression is `p(a+b)+(q+p)b = pa+qb`. All other operands
are unchanged. The 27 pairs are disjoint and exclude every retained total,
so their substitutions commute and no total gate writes a temporary
operand. Each retained total's value agrees after its gate, and the complete
phase-A operator agrees after restoration, with no zero-scratch assumption.
The same scatter, B and D then
remain valid. Rebuilding C as the literal reverse of all A/B z-gates
retains H4 and restores every source and helper.

For one oriented pair, write `u` for the number of rows containing both
operands and `v` for rows containing `a` but not `b`. The net phase-A
saving is `u-v-2`; the two charged operations are preparation and
restoration. The exact phase-A saving over the 27 pairs is 57. Cleanup
saves the same amount.

| Charged binary additions | Original | New |
|---|---:|---:|
| Decoder-total source reads | 321 | 210 |
| Temporary preparation and restoration | 0 | 54 |
| Complete decoder suffix | 321 | 264 |
| All phase A | 2,376 | 2,319 |
| All cleanup C | 2,973 | 2,916 |
| D, scatter and B together | 21,567 | 21,567 |
| Complete native word | 26,916 | 26,802 |

Every temporary operand already occurs at FULL in the old suffix. All
new operations are at FULL, after the same earlier frame visits. The
checker compares every register's entire frame-ID sequence, including
final climbs. All operand reads, including preparation and restoration,
are charged in the ADD counts. No helper, copy, erase, frame transition or
recursive child is added. The inherited paid profile therefore remains
`{1:1320, 2:1440, 4:60, 5:120, 8:9}`, with rank mass 5,112.
The JSON multi-source gate count increases by 108 across A and C; the
binary ADD count above is the physical scalar count, not that JSON count.

Positive arithmetic is priced separately. Cancellation-free scalar-word
maximum row sums rise from 144,651 to 193,441, and maximum column sums
from 40,742 to 53,780. These are exact integer norms, not bounds for the
complete hosted program. They do not justify inheriting its prefix bill.
The unchanged native checker gives forward bounds 144,651 to 193,441 and
reverse bounds 2,270,064 to 2,702,178. Its nine-stage payload charge rises
from 100 to 102 bits, still below its 104-bit budget. Both words pass all
1,380 formal physical columns and all 18 omitted-bridge controls. The
complete hosted invoice remains an integration obligation.

## Search coverage and controls

The operating-system assignment seed is 15. Three candidate tasks and the
local claim are recorded in [CLAIM.json](CLAIM.json); GitHub returned no
pinned coordination issue. The chosen search fixes the nine totals, their
hosts, their order, the original retained basis and the rest of the word.
It covers all **6,320 oriented pairs** of the 80 non-retained operands;
463 have positive complete savings. One greedy disjoint matching is taken
in descending saving order, after a seed-15 shuffle to break ties. The
stopping rule is the end of that single list. The frozen 27-pair recipe is
in [recipe.json](recipe.json). There is no claim of a minimum circuit or
optimal matching, and no closed decoder-rank search is reopened.

The controls remove restoration, corrupt a decoder operand, retain a
scalar-valid but nonliteral old cleanup, move preparation illegally to
frame zero, attempt a retained-register temporary, overlap pairs, and
remove dirty compensation. The first two also fail the separate
set-valued checker. The old cleanup is deliberately classified as
scalar-valid but outside literal H4, not as a false endpoint identity.

## Scope, prior work and attribution

This stops at a finite native bit circuit. The selected assembly is
complex-limited; unchanged recursive profiles do not create a new bit
exponent. Full parent construction, whole-owner hosting and the changed
global positive-prefix invoice still need replay before integrating this
word into an accepted supplier. The all-size compiler, common-label and
mutable-basis realization, pooled-cell hosting, precision/tape, residual
and analytic-transfer assumptions remain inherited. Finite symbolic
execution is not a formal proof of the full multiplication theorem.

Credit belongs to eumemic for PR543/493's R420 construction, decoder-total
schedule and interleaved-source interface; Dylan Crow for the earlier
bit-word/exporter line; DreamingOfClouds for retained-total and supplier
pricing work; Zhihao Chen for the mutable-basis scalar interface; and the
full realization, geometry, hosting and assembly lineage retained by
the original package and selected review.

Concurrent PR686 and PR694 are credited for restored pair sharing in
frame-zero dirt compensation. This contribution applies that algebraic
mechanism to the separate nine-total suffix at FULL, with complete A
operator equality and the original H2 unchanged. It imports no code or
circuits from them. PR670/674/688 alter phase-B blocks, PR691 alters
phase-A quad 13, and PR661 fixes phase-B gates and excludes resynthesis.
Composition with those changes is not claimed. PR620's decoder-floor
research concerns a different question from synthesizing these fixed
retained totals.

Prepared for **Sagar Thakrar (@thakrarsagar)** with substantial **OpenAI
Codex assistance** in nomination, proof, implementation, verification and
packaging, including separate Codex workers for independent replay and
native checks. No independent human review is claimed. This contribution
is under Apache-2.0, retaining the repository and predecessor licenses.
