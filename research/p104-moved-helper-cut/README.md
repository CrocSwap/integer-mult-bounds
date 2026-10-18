# An independent moved-helper cut for PR3124's P104 matching

**Scoped proof and independently implemented finite audit.** The exact matching
published in [PR3124](https://github.com/CrocSwap/integer-mult-bounds/pull/3124),
with alternating cycle `[13,203,191,63]`, cannot deliver the required P104
correction in the fixed X-only monotone common-frame model. Requiring only
helper **13** to follow one nested flag already forces the added coefficient
`X1 -> Y40` to be zero, although `C[40,1] = (I-G/2)[40,1] = 1/2`.

This independently corroborates **dcharb78's prior helper-13 exclusion in
PR3182, Pillar 2**. Discovery priority for that exclusion is not claimed.
The contribution is a separately implemented source-bound check, a small
three-vector separating proof, and a full support receipt. It does not import
any predecessor Python, propagation routine, flag enumerator or result file.
Ross Richardson's PR3032 supplies the earlier one-helper cut method for a
different matching. PR3124's positive helper-91 result remains within its
stated scope; it leaves the other 207 helpers relaxed.

The small proof bounds Y40's correction support by `{6,8,41,45}`, excluding
**44 of its 48 required coefficients**. Separately, a complete census gives:

| Missing required pairs over all 104 targets | Helper-13 flags |
|---:|---:|
| 1,002 | 225 |
| 1,020 | 477 |
| 1,023 | 477 |
| 1,025 | 117 |
| 1,026 | 8,469 |
| **Total** | **9,765** |

The flags have 22 distinct complete contact/read/write profiles. Across all
flags, **995 specific required pairs are always missing**. The census and
histogram agree with the reported PR3182 helper-13 values; the 995-pair
intersection and the small Y40 proof are recorded here explicitly. No other
PR3182 pillar, helper census or consumer-price claim is admitted by this audit.

## Contract and proof

Work in `F2^9` with the frozen PR1972/1991 X and Y frame paths. X is immutable;
Y is unread. The added correction must preserve each arbitrary initial Y
value. Helpers begin with independent arbitrary dirty inputs and follow
monotone flags from dimension zero to nine. Scalar transfers require a common
frame. No original-channel helper reads, extra lifetimes, descending frame
transports, target feedback or source-dependent frame program are granted.

For helper `h`, its dimension-two departure space is `A_h`, and its
dimension-seven space is `B_M[h]`, where M is the pinned matching. Dimensions
one and eight are the prescribed source line and target hyperplane. Every
intermediate frame F obeys `A_h <= F <= B_M[h]`.

We grant all frozen source snapshots without their actual event deadlines,
free mixing, and no restoration or physical cost. Every helper except 13 may
choose each contact independently, even when those contacts cannot coexist
in one flag. Same-layer contacts receive full transitive closure, including
fresh source reads, and all writers accumulate into each target. This is a
favorable necessary support test, not an executable correction program.

A nonzero coefficient in any allowed linear program requires a source-to-write
path of nondecreasing frame dimension. Copies, cancellation, rescaling and
independent dirty inputs cannot create a source coefficient without such a
path. Dimension zero supplies no source; at dimension nine no Y write remains.

### Complete local boundary

Literal enumeration of all admissible subspaces gives the following **complete**
other-helper contact lists. Dimensions two and seven have no other contact.

| Helper | Dimension 1 | Dimension 3 | Dimensions 4 and 5 | Dimension 6 | Dimension 8 |
|---:|---|---|---|---|---|
| 13 | 12 | 63,185 | 63,91,118,185 | 91 | 124 |
| 17 | 16 | none | none | none | 83 |
| 83 | 82 | none | 91 | 91 | 17 |
| 91 | 90 | none | 13,83 | 13,83 | 183 |

These helpers read only X6, X8, X41 and X45 respectively, at dimension one.
Each dimension-one partner has that same source and no other source there.
Y40 has no direct equal-frame X read. Its only writers are helpers 17 and 83,
both at dimension eight. The late contact from 183 into 91 cannot reach the
earlier exits from 91 into 83 at dimensions four through six.

Any new source outside `{6,8,41,45}` reaching Y40 must therefore pass through
`u -> 13 -> 91`, where `u` is 63, 118 or 185. Entry from helper 124 occurs
only at dimension eight and is too late. Entry from 91 itself cannot be the
first acquisition of an outside source into this local subsystem.

At the contact with u, helper 13's frame contains `A_u`. At its later contact
with 91, its frame lies in `B_8`, because `M[91]=8`. Nestedness would force
`A_u <= B_8`. Each possible u has an explicit contradiction:

| u | A_u basis | Vector in A_u but outside B_8 |
|---:|---|---:|
| 63 | 31,288 | 31 |
| 118 | 178,365 | 178 |
| 185 | 253,288 | 253 |

Here `B_8 = span(2,13,20,37,64,133,261)`. The integers encode binary vectors;
span and membership are over F2. Equal-dimension contacts give the same
contradiction, since a flag has just one frame at that dimension. Repeated
contacts do not evade the first-acquisition argument. These three separations
also appear among the twelve pairwise incompatibilities in PR3182's algebraic
proof for helper 13; the addition here is the complete local boundary above,
which makes `u -> 13 -> 91` the only route for an outside source into Y40.

It follows that Y40's added support lies in `{6,8,41,45}`. The checker
reconstructs the 120 doubled E8 root representatives, removes the two fixture
frames, and uses the retained lexicographic 104-port order. The doubled roots
at indices 1 and 40 are `(0,0,0,0,0,2,0,2)` and
`(1,-1,-1,1,-1,-1,-1,-1)`. Their dot product is -4, so
`C[40,1] = -(-4)/8 = 1/2`. All four allowed support positions are required,
leaving 44 other nonzero coefficients unavailable.

A separate exact rational replay of all 104 original X columns checks the
4,058-event logical channel, every common-frame ADD and all 10,816 target
coefficients against the reconstructed Gram matrix. It also checks source
preservation and zero final source response in the dirty helpers. The native
transport realization and arbitrary dirty/target entrance columns remain
inherited. The existing G/2 response in Y is not an available correction
source because Y is unread. Preserving arbitrary
initial Y forces the added increment to supply I-G/2; its missing X1
coefficient cannot be repaired by counting the existing response again.

### Finite completeness and checks

Each interval `B_M[h]/A_h` is five-dimensional. The verifier generates every
literal quotient subspace by all one-vector extensions, obtaining layer counts
`1,31,155,155,31,1`, then lifts its cosets to actual F2^9 point sets. It tests
contact by equality of literal admissible frames, not an imported interval
formula. Complete quotient flags number
`31*15*7*3*1 = 9765`; all are traversed once.

Flags are grouped only when **every** incident contact, read and write agrees
at every dimension. Literal quotient enumeration follows PR3032's credited
method, reimplemented here with integer point masks and full incidence tables.
One source-bitset connected-component engine and a
separate per-source layered BFS agree on all 104 output supports for every
class and for the unconstrained positive control. They share the new parser,
geometry and mathematical model; they are not independent human reviews.
[RESULT.json](RESULT.json) retains every class's multiplicity, representative
flag, complete output supports as 104-bit hexadecimal masks, and the 995-pair
intersection. Default replay compares every field, including JSON types.

[check_cut.py](check_cut.py) independently reconstructs the small boundary by
binary Gaussian elimination and the interval-contact lemma
`dim(A+C) <= d <= dim(B intersect D)`, with the required inclusions. It imports
neither the main checker nor predecessor code and enumerates no quotient
flags. It derives Y40's entire correction row by reverse scalar sensitivity
through the original word, including private copy/erase boundaries. This
also checks that row's initial Y coefficient is one and its other dirty
entrance coefficients vanish. The two geometry methods and forward/reverse
coefficient calculations agree exactly. The source JSON and mathematical
contract remain shared; no independent human review is claimed.

A deliberately nonnested choice, differing at one intermediate frame from a
nested flag, restores X1's path to Y40 in the favorable graph. The cut receipt
retains its literal bases. The normal flag validator rejects it. The completely
unconstrained matching reaches all 4,992 required pairs. These controls show
that the nestedness restriction is substantive, rather than a missing-edge
artifact of this implementation.

Eleven behavioral groups cover same-layer fresh-read relay, accumulation from
all writers and a direct read, prohibition on backward time travel, independent
dirty state, the nonnested control, changed contacts/coefficient, equivalent
basis order and an invalid matching, logical port-order/common-frame binding, all 17,424 interval/contact cases in F2^3,
independent algebraic cut agreement, and optimized Git-free export with source
and receipt corruption. No predecessor checker is imported or executed.

## Reproduce

Python 3.12 and standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-moved-helper-cut
```

The main marker is:

```text
PASS_P104_MOVED_HELPER_CUT flags=9765 helper=13 profiles=22 always_missing=995 no_new_kappa
```

To check the small proof boundary without enumerating the 9,765 flags:

```sh
python3 -I -O -B research/p104-moved-helper-cut/verify.py --cut-only
python3 -I -O -B research/p104-moved-helper-cut/check_cut.py
```

This prints `PASS_P104_MOVED_HELPER_SMALL_CUT target=40 source=1
missing_coefficients=44 no_new_kappa` on one line. The second prints `PASS_P104_MOVED_HELPER_ALGEBRAIC_CUT`.
All replay commands are read-only.
`verify.py --emit` emits a freshly derived full receipt to stdout. Direct
replay also works without Git when this package and its five declared JSON
inputs are copied at the same relative paths. The registered metadata check
additionally uses pinned Git provenance.

## Cost decision and limits

This rejects one proposed realization before coefficient synthesis or physical
implementation. It retains the 208-helper premise and its 1,872 formal rank-one
steps. PR2920's favorable channel/transport/ideal-idle screen is inherited,
not recertified. Actual chronology, coefficients, restoration, native ADDs,
owners, routing, precision, tape and complete consumer charges are not supplied
or treated as zero. A support failure persists even with those charges waived.

The decision is to **stop this fixed matching under this contract**. This is
not a new helper-lifetime lower bound, an exclusion of every endpoint matching,
a physical supplier admission, a complete multiplication theorem or a new
kappa. The selected result remains unchanged. No selected cold replay, Lean,
physical backend trace, hosted CI or independent human review is claimed.

## Open next questions

- A different matching or access/frame contract must pass a joint consistency
  test before coefficient synthesis. State the changed premise and test its
  source-to-target paths first; the complete consumer budget is still a blocker.
  This result does not propose a larger matching search.
- Other archived PR3182 conclusions require their own audits. This check
  isolates the helper-13 nested-flag conclusion; it establishes nothing about
  one-hop propagation, subspace-memory propagation, helper 63, the secondary
  cycle or the physical-price table. A next audit should name one such claim
  and test its exact semantic premise.

Structured questions and the complete task scope are in [TASK.json](TASK.json).

## Sources and credit

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
PR3124: `ce468c5cf22f59db3071adda269ac4cc16469c8c`.
PR3182 comparator: `ad848966cd62e13de5ad8d4b5169c221d74d2fcd`.
[SOURCES.json](SOURCES.json) pins the five raw JSON inputs by Git blob and SHA256
and records predecessor heads. The checker also reconstructs the oriented
four-cycle from the retained PR3013 control pairing, rather than trusting its
printed name. The claim is in
[Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-19001906).

Credit Cinna Davis (@1337isnot1337), PR3124, for the matching and handoff;
dcharb78, PR3182, for the prior moved-helper obstruction and histogram; Ross
Richardson, PR3032, for the one-helper monotone cut technique; Nick Petalas,
PR2981/2996/3013/3019/2920/2909/2896, for covers and matching/contact evidence;
Arham Tahir, PR2997, for the fixed-full-flag audit; Rohan Arun, PR1972, and
Chafik Boukhalfa, PR1991, for the original channel and retained inputs.
Retain the attribution to Adam Gall/1940/2090, Jeremy Diviney/2113, Josie
Elliston/1071, Ali Romman/1125, Hiroki Kumazaki, Philippe Van Velzen,
Sudarsh Chaturvedi, Sagar Thakrar, ywz65 and the original geometry/native
contributors. The earlier commdata2338 acquisition/native/precision results
are distinct and are not replayed here.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New code and writing are Apache-2.0. No independent human or formal-kernel
review is claimed.
