# A source-specific literal cost vector and tariff conversion boundary

Prepared for @CubeJerry with substantial OpenAI assistance. This is a
conditional implementation-cost audit. No new kappa, physical supplier
admission, or multiplication lower bound is claimed.

## 1. Result and exact scope

Fix the published compact rounded ADD constructor at CubeJerry commit
`38cd824c60f2bb5c6f2603f848a9487cb3a57965`, executed by the unchanged
lifecycle machine at `ab239cb6ee884e7a900dd9101c34448077fad0b0`. Let the
coefficient be reduced a/b, b>0, oddpart(b)<=125, and let

    L = max(bitlength(abs(a)), bitlength(b)),
    delta = 1 if oddpart(b)>1, otherwise 0.

For each successful invocation on matching positive component widths w_i,
put B=sum_i w_i. B counts public numeric data bits in ONE field: it excludes
numeric delimiters, the three-bit physical code expansion and all private
copies. The component count is positive and even. The data/grid/alias/head/
frontier premises are precisely those of the retained compact theorem.

In the physical metric of that actual implementation, the invocation makes
at least the following vector of operations:

    physical reads       >= B*(76 + 22L + 10 delta),
    physical writes      >= B*(18 +  3L),
    physical unit moves  >= B*(156 + 48L + 18 delta),
    executed flat rows   >= B*(38 + 13L +  5 delta).

Thus raw reads+writes+moves are at least B*(250+73L+28 delta).
Including executed flat rows gives B*(288+86L+33 delta). These are lower
bounds, not estimates obtained from a slack implementation upper bound.
They hold for every successful admitted input. In particular, the all-zero
input is successful at every positive width: all Horner prefixes are zero,
the rounding offset satisfies 0<=floor(b/2)<b, and the final output is zero.

Now consider the proposed direct substitution of this generic constructor
at every ADD in DreamingOfClouds' exact #6936 local word, used at the 18
joint contacts of the published QUERY-only caller #6937 lineage. The source
has 61,052 ADDs, sum L=167,955 and 4,079 odd-denominator ADDs per local word.
There is separately ONE COPY, excluded throughout this theorem. If all
these invocations have the same B, their mandatory vector is at least B
times

    (150,763,536 reads, 28,850,418 writes,
     317,868,732 moves, 81,428,148 flat rows).

The raw action total is 497,482,686 B; the raw-plus-row total is
578,910,834 B. With different volumes, the first per-invocation formula
must instead be summed with each actual B_e. Equal volume is an explicit
comparison premise, not inferred from an uninstalled exporter.

The predecessor has a generic arithmetic proof but installs only three
actual source tokens. This audit does NOT install the other ADDs, COPY,
the caller exporter, rounded SCALE or LAMBDA, or recursive services. It
analyzes exactly the suggested direct generic-ADD substitution. Its
nonempty all-zero path can be composed with zero-preserving native and
child operations; no whole numerical source execution is claimed.

## 2. Source pins and the three distinct units

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The local
word is #6936 tested head `03626137d0bd57f09b0bf9597376183ce6fa9683`, blob
`d93e67ca7628bf5531ae6e369da4dd7b7907b88f`. Latest observed #6936 head
`d360b1182b6d21b1ee2354856abcb50646ad618b` changes only VERIFY timeout;
it does not replace the tested bytes. The QUERY-only caller is public
`617903497387a98f7ca929ad0b6928dd32abffec`, descended from #6937 at
`a98df73ddae1d1ea85a62b6bdf2714b28cb7b359`. Its precision screen is public
`56bc9383594a3efc303148e00bb746851abd1ed5`.

Rounded SCALE is public `6476455a1cf7cd29d6a2a81c3b6f02fd3a3bbf57`.
The global LAMBDA implementation is public
`591394d8b791f6e8ac6e1aa36f8c3ea5389178c2`. Those services retain their
own explicit bills; this lower bound does not count them as free. Their
future physical costs and rebindings remain separate positive obligations.
`DEPENDENCIES.json` records exact commit/path/bytes/Git-blob/SHA256 pins.

The units must be kept separate:

1. A physical action here is one invocation of Tape.read, Tape.write or
   Tape.move(+/-1) by the pinned implementation. A flat row is one row
   fetched by its unchanged execute_table. Counting both is a useful
   conservative implementation metric, not the definition of a TM step.
2. Canonical `02-streams.tex` defines a fixed multi-tape step that may
   read/write/move on multiple tapes at once. It licenses elementary
   operations in O(V), with implementation-dependent constants and all
   resets/cleanup included. Its logical volume excludes duplicate work
   streams. It does not set one tariff unit equal to one physical action,
   one flat row, one three-bit symbol, or one simultaneous machine step.
3. The proposed invoice counts scalar/pass allowances and 1000-unit route
   allowances. #6937's ROUNDED-DIVISION section 7 explicitly calls its
   4(bits+1)-per-scan charge a model/judgement and leaves a text-derived
   charge model owed. Precision section 6 preserves that qualification.

The old warning is credited, not claimed new. Canonical FINITE-PRECOMPILATION
section 6 also requires substituting actual finite constants before reusing
an old scalar cap. `05-layers.tex` supplies fixed-number-of-scans O(V)
statements, not a missing numeric conversion theorem. Fixed constants can
be absorbed asymptotically only after the necessary substitutions are
written; this does not establish a particular displayed 10^9 invoice.

## 3. Exact coded instruction costs

On an existing valid nonblank numeric codeword, CodedPort.read performs
four physical reads and six moves. Its initial blank test is an additional
read before the three code bits are inspected. A write makes three writes
and six moves. Either direction of a successful ordinary coded move makes
one read and three moves. Consequently the instruction vectors are

| Coded operation | Reads | Writes | Moves | Flat rows |
|---|---:|---:|---:|---:|
| branch/read | 4 | 0 | 6 | 1 |
| write | 0 | 3 | 6 | 1 |
| unit move on a nonblank body | 1 | 0 | 3 | 1 |
| goto | 0 | 0 | 0 | 1 |

Moving right from a blank frontier is more expensive; omitting that extra
work is safe for a lower bound. At ordinary positions in the listed passes,
the relevant cells were already written or belong to complete input bodies.
Every control dispatch inside the Python implementation not represented
by one of these flat rows is omitted rather than treated as free in an
upper certificate. The kernel's loops do not branch on a whole-field-zero
shortcut. A different optimized implementation is outside the theorem.

For each ordinary public data bit, the following phase contributions are
forced by the retained source. The table is vector-valued so a future
conversion may give reads, writes, moves and rows different weights.

| Phase | Reads | Writes | Moves | Rows |
|---|---:|---:|---:|---:|
| Numerator initialization and public rewind | 18 | 3 | 42 | 12 |
| One Horner pass and its public rewind | 22 | 3 | 48 | 13 |
| Offset pass and numerator rewind | 10 | 3 | 24 | 6 |
| Odd-residue pass and numerator rewind, when o>1 | 10 | 0 | 18 | 5 |
| Quotient staging | 16 | 3 | 36 | 9 |
| Whole-field reverse scan | 8 | 0 | 18 | 6 |
| Final installation | 6 | 3 | 18 | 5 |
| Two long executor head returns | 6 | 0 | 6 | 0 |
| Retirement of two current private bodies | 12 | 6 | 12 | 0 |

For example, a Horner bit uses three coded reads, one write, three moves
and one goto: (15,3,33,8). Its required public/numerator rewind uses three
moves, one read and one goto: (7,0,15,5). Their sum is (22,3,48,13).
There are exactly L such passes, including leading zero coefficient bits
in either member of the fixed pair. Each pass visits every public bit.

Quotient staging uses three reads, one write and FOUR moves: numerator,
output, target and source. It therefore costs (16,3,36,9), or 55 physical
actions and 64 actions-plus-rows per ordinary bit. The predecessor proof's
illustrative sentence giving 59 for this particular phase omitted that
fourth move. Its deliberately slack 128U phase upper bound is unaffected;
this audit does not infer that the predecessor cost theorem fails.

Initialization and its rewind contribute (18,3,42,12). The offset has a
single numerator read/write/advance and a one-tape rewind, giving
(10,3,24,6). An odd-residue traversal and rewind use no writes, giving
(10,0,18,5). The global reverse uses the numerator guide to move all three
other heads left once per public bit. Installation reads staged output,
writes the target and advances both heads. These yield the two indicated
rows directly. Delimiters, markers, extra K=L+2 numerator positions,
quotient low-bit drops, terminal guards and all phase transitions add
nonnegative work and are omitted from this lower bound.

At final halt, both target and staged-output heads are at physical distance
3S, where S=sum_i(w_i+1), from their origins. The other heads are already
at their origins. The unchanged execute_table must return those two heads:
each origin operation makes at least 3S reads and 3S moves. Since S>=B,
the contribution is at least (6B,0,6B,0).

The numerator body has length 3U with U=1+S+(K+1)R, and the output body has
length 3S. They are contiguous physical binary bodies, even where their
logical symbols encode blanks. A successful retire at an origin reads at
least twice the body's length, writes each physical cell once and moves
at least twice the body's length. Since U>=S>=B, both retirements together
contribute at least (12B,6B,12B,0). Entry retirement of arbitrary old bodies,
historically longer capacities, contexts, shape preparation, static table
construction and other wrappers are positive omitted costs. The bound
does not assert that any of them vanish or that allocated capacity shrinks.

Summing the table, repeating Horner L times and residue delta times, proves
the four inequalities in section 1 for arbitrary matching widths. No
finite-width extrapolation or operation-time measurement enters the proof.

## 4. Exact complete source census and maximal ADD credit

The checker independently reconstructs the frozen source formula, including
the 18 local words, all outer ports, all main/idle/query maps, the second
LAMBDA charge, and the retained 1125 conversions. It obtains 826,265,904.
It independently adds the precision model's 17,165,584 to recover
843,431,488. These are arithmetic identities in the stated model.

For an ADD with a=abs(numerator), b=denominator, the existing per-call
reviewed charge is 4(bitlength(a)+popcount(a)+bitlength(b)+1). Its rounded
offset/residue surcharge is zero for b=1 and otherwise
4(bitlength(b)+1)*(1+3*[oddpart(b)>1]). Summing ONLY the 61,052 ADDs gives

| Existing term | One local word | All 18 words |
|---|---:|---:|
| Reviewed ADD tariff | 1,717,220 | 30,909,960 |
| ADD rounding surcharge | 920,796 | 16,574,328 |
| Total removable ADD credit | 2,638,016 | 47,484,288 |

This credit is fully removed when substituting a new complete ADD charge;
there is no double billing of old and new ADD costs. The untouched
conditional invoice is therefore 795,947,200, leaving 204,052,800 below
10^9 for replacement ADD work. This is more generous than comparing the
new ADD cost with the old 156,568,512 margin alone.

The exact source sum of the universal vectors gives the section 1 numbers.
It excludes COPY, all 3,660 local SCALEs per word, all native MOVEs and
owned administrative operations, and the outer 54,352 ADDs, 8,480 SCALEs,
14,480 LAMBDAs, 35,672 SWAPs and 416 QUERY lifetimes. Those terms remain in
the old invoice for the next conditional comparison; no claim is made
that those old tariffs have been physically verified.

## 5. Necessary conversion condition, not a full-runtime obstruction

Define rho>0 by the following proposed conversion contract: a tariff
allocation u, on a comparison volume B, permits at most rho*u*B physical
reads+writes+moves of the chosen implementation. This explicitly fixes
the volume convention as well as the operation metric. If another
comparison volume, f-dependent factor, simulator constant, simultaneous
multi-tape clock or delimiter convention is intended, it must be supplied
and folded into rho or into the individual event volumes. The source
does not currently supply this contract with a numeric rho.

Consider the specific replacement certificate that keeps every other
existing invoice term and gives all the released ADD credit plus remaining
slack to the direct compact implementation. A necessary condition is

    rho >= 497482686 / 204052800
        = 82913781 / 34008800.

If the tariff must also pay one extra unit for each fetched flat row in
the same metric, the necessary condition becomes

    rho >= 578910834 / 204052800
        = 96485139 / 34008800.

Under the explicit equal-unit proposal rho=1, this fixed replacement
ledger has lower endpoints 1,293,429,886 or 1,374,858,034, respectively,
both above 10^9. That is an obstruction to THIS numeric substitution
certificate under THAT conversion. It is not a lower bound on the full
program's actual runtime: the retained 795,947,200 consists of inherited
upper/model charges, not lower bounds. Repricing other work more sharply,
changing the implementation, fusing services, specializing small scalars,
or proving a different conversion is outside this certificate. In
particular rho=3 passes this necessary lower-bound screen; that fact is
not a sufficient upper-cost admission.

More generally, if a converter prices the vector with nonnegative weights
(c_r,c_w,c_m,c_u), the necessary left side is

    150763536*c_r + 28850418*c_w
      + 317868732*c_m + 81428148*c_u.

It must be at most the replacement allocation in the corresponding
normalized units. This exposes the exact quantitative obligation rather
than assuming that unlike counters have equal units.

## 6. Evidence, limitations and next obligation

`verify.py` authenticates 19 immutable dependencies, recomputes all source
counts and both complete model invoices, and exercises the unchanged table
executor on 36 all-zero cases. The cases include heterogeneous widths,
width1, width65, both signs, even/odd denominators, three actual maximal
coefficient witnesses, and dirty displaced private banks. An independent
hardware meter checks each vector coordinate against the proved lower
bound and checks output/source preservation and cleanup. The numerical
tests corroborate the control-flow proof; they do not replace it. Small
primitive probes independently distinguish the actual 10-action coded
read from a three-read shortcut. Accounting controls distinguish omitted
18-fold expansion, COPY contamination, residue rewinds and the fourth
quotient move. No complete numerical caller is executed.

The original warning about the tariff unit is not novel. The new result
is the all-width forced pass vector, its exact 1,098,936-occurrence source
sum, the maximal legitimate released credit and the resulting necessary
conversion inequality. The weakest next useful proof is a concrete common
volume and machine-clock conversion with a certified complete upper bill,
including native routing, all rounded services, source/shape work, setup,
head returns, cleanup, old backing and simultaneous recursive ancestors.
Only then can the displayed ordinary cap be accepted or rejected for an
actual complete implementation. All five foundational assumptions remain
global premises, the selected certificate is unchanged, and no new kappa
is claimed.

Credit DreamingOfClouds' #6936/#6937 source and tariff qualifications;
CubeJerry's lifecycle, scalar, compact ADD, QUERY-only, precision and
global LAMBDA packages; and the canonical stream/finite-precompilation
authors. The counting principle is elementary. Separate AI review, when
recorded, is not human or proof-kernel acceptance.
