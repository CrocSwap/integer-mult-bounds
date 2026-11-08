# Source-bound first-face halo transaction

**Result:** a complete, explicitly priced interface joining the new physical
first-face transport to the new shrinking-reference numerical consumer.
Original halo values are copied before core mutation, streamed into the
consumer through a checked coordinate codec, and returned exactly once to
the discarded dense coordinates. An actual retained Gaussian reference
exercises the whole interface, including identity holes and a period cut.

**No new κ.** This supplies the sparse transport/consumer/return implication
that the component proofs require. An actual same-reference core and the
full outer multiplication proof remain separate obligations; all five
selected assumptions remain.

## What the integrated contribution adds

The two component packages are retained intact:

- [Sparse halo tape transaction](../sparse-halo-tape-transaction/README.md)
  supplies the 30-role finite-alphabet enumerator, complete sparse-key sort,
  pre-copy chronology and unique return left open by #4870.
- [Shrinking reference halo](../shrinking-reference-halo/README.md) supplies
  the numerical rectangle consumer from global reference band entries,
  with shrinking domains, actual-input rounding bounds, paid page exposure,
  eight reused local roles, and explicitly priced scalar/source arithmetic.

The composition in [PROOF.md](PROOF.md) verifies their exact common
contract. A sorted rectangle prefix is consumed as one contiguous block;
there is no host dictionary or payload-array regrouping. A common saved
radius may be cropped to unequal numerical radii in one sparse pass. The
codec checks complete offsets and their canonical source suffixes, copies
payload cells unchanged, and converts only target keys back to canonical
global coordinates. The numerical payload grid, signed-word convention,
periodic coordinates, reference identity and dyadic normalizers agree.

The inherited first-face combinatorics and copy-volume formula are not
reproved as new discoveries. The direct-Neumann degree `16p^4` was already
available in #6880. The new result is the implemented, proved and tested
composition, including its full physical and scalar-macro accounting.

## Complete cost and scientific scope

Let M be dense scalars, P their bit width, B their full coordinate width,
`C_B` all common-radius copies, `C_r` a cropped consumer rectangle's volume,
`R_rect` the number of rectangles, `G=sum_i N_i(2W_i+1)` the group archive
size, and w the complete encoded data/control width. The generic bound is

```text
T_ref + O(M(P+B) + w^2 [C_B + R_rect g G
                     + sum_r C_r sum_i(J_i(2W_i+1)+K_r+1)]).
```

It retains source production `T_ref`, every repeated archive scan, all
common-radius copies, descriptor/key conversion, radix work, output copies,
returns and erasures. It does not charge a dense scan per numerical axis.
All retained backing, including erased temporary tables and bucket tails,
stays in the space bill. A fixed number of physical data/control roles
suffices; no role is allocated per rectangle or tensor dimension.

The transport's reported tape actions use a 14-symbol alphabet and have a
constant-factor binary simulation. The consumer's reported data moves are
binary; its bounded integer arithmetic and the codec's sparse metadata
arithmetic use a separate ordinary quadratic bit tariff. The complete
composition is not advertised as a fully emitted binary transition table.
The descriptor width includes `log J` even when bandwidth is zero, and
includes cumulative record counters.

Under the pinned balanced-group caller hypotheses, the complete additional
charge is `O(V d/g + V d g A p^6/L) + 2^o(p)`. This fits the inherited
conservative sparse halo allowance. It is a conditional implementation
substitution, not a stronger selected exponent or proof of the missing
core/outer premises. The generic formula remains necessary when a finite
instance does not satisfy the archive-amortization conditions.

## Reproduce the complete contribution

Canonical upstream base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The exact remote component tree parents are
`a2f3ce7358e8103f6eccd404e594276e9ccc04d8` (consumer) and
`630c9c2a5d6373ca103c55108bb606b4868bc6fd` (both components).
`SOURCES.json` pins live imported files by Git blob, SHA256 and these
heads; the final contribution descends from the combined parent.

With Python 3.12 and the standard library, from the repository root:

```sh
python3 -B research/first-face-reference-join/replay_all.py
```

Expected final line: `PASS_COMPLETE_FIRST_FACE_HALO_PACKAGE`.
The wrapper sequentially runs the registered checks for transport,
consumer, and join. It does not run unrelated repository suites. For only
the join, use:

```sh
python3 -B scripts/research_package.py --package research/first-face-reference-join
```

Expected: `PASS_REGISTERED_RESEARCH_PACKAGE`. The join registers normal
and optimized (`-O`) runs of the actual-reference transaction and the
independent whole-grid review. Failures use explicit exceptions, not
assertions. No third-party dependencies are required.

## Evidence

The actual source is `Reference(61,3,2,1,8,32)`, period 64. Its 4,096
original entries give a certified row gap `6255/8192`, identity-hole rows
11, 32 and 53, and nonzero coefficients across `0 <-> 63`. The fixture uses
`L=32`, `A=5`, saved radius 4, numerical half-bandwidth 4, two terms,
28-bit grid, radius one and normalizer two.

Four rectangles save 52 inputs and return 20 targets. Three complementary
checks establish what those outputs mean:

1. The streamed codec matches a separately loaded rectangle consumer
   bit for bit, detecting changes too small for a loose error bound.
2. A separately written whole-period recurrence with independent arithmetic
   and global indexing matches every returned bit.
3. Exact rational elimination solves the original `H y=x/2` and checks
   every residual. Maximum target error is about `0.0003996004385`, below
   the proved `0.036611087107` bound. These decimals summarize exact
   rational comparisons; two terms are a finite interface fixture, not an
   asymptotic precision allocation.

The positive transaction executes 3,753,372 transport symbol actions and
1,055,928 consumer binary actions. The displayed conservative binary-tape
primitive bound is `10*B_actions+C_actions=38,589,648`, before scalar/control
macros and their fixed control compilation factor. It retains 21,740
transport symbol cells and 41,978 consumer binary cells, including blank
backing after cleanup. Source production and coefficient arithmetic have
their separate retained bills; these figures are not a Python memory or
runtime benchmark.

The separately assigned whole-grid review also checks a spectator fixture
and two signed two-axis fixtures with unequal numerical radii `(1,0)` and
`(1,2)`. The two-axis cases return 448 and 624 targets and crop 288 and 432
saved records respectively. During codec, return and erase, it disables
tape constructors and diagnostic `inspect`/`snapshot` access, checks the
same eight consumer roles and unchanged archive, and checks full blank
backing afterward. The 1D and 2D numerical oracle does not use the codec's
grouping, local layouts or shrinking implementation.

Controls reject a changed offset, omitted period wrap, missing saved
record, wrong return key, foreign source suffix and raw negative zero.
An in-radius payload magnitude mutation is detected by exact comparison.
The core in these fixtures is a bit-complementing test double. Kept
interior values are checked as opaque current-core bits and are never
interpreted as a validated Gaussian numerical output.

`RESULT.json` records the exact actual-reference receipt. The component
receipts and full independently reviewable programs remain in their own
directories. Separate source-aware AI review is disclosed; independent
human or proof-kernel acceptance is not claimed.

## Open next questions

1. Admit a concrete rounded core on the same global reference, input grid
   and dyadic normalizers. The splice then gives error
   `max(E_keep,E_halo)` with no new codec defect. Start with one actual
   caller core and its complete all-input contract.
2. Bind canonical group-layout production, ordinary child calls, source
   transforms and all recovery scales into the selected outer proof.
   The local time substitution and finite actual-reference fixture do not
   discharge these global assumptions. Preserve the generic repeated-page
   bill whenever the balanced-group absorption cannot yet be applied.

Structured questions, first steps and blockers are in `TASK.json`.

## Attribution

Prepared for **@CubeJerry** with substantial OpenAI Codex assistance in
the transport, source-bound numerical consumer, composition, exact oracles
and separately assigned adversarial AI review. Credit Cinna Davis (#4100),
@codyw912's Astra/OpenAI-assisted #4870 enumeration package, Nick Petalas (#4217),
Jose Manuel (#4205/#4253), Ryanson Jonathan (#4517), JoyboyBrian (#5081),
the #6880 splice contribution, and their retained Gaussian/tape lineage.
The predecessor claims and attributions remain in both component packages.
Apache-2.0.
