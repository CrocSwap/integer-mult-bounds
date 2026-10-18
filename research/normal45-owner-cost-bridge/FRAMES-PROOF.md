# Explicit-subset frame and cleanup invoice

This is a finite replay of the four frozen `WORD-{base,extra}` and
`PARENT-{base,extra}` inputs from PR2942 at
`a027b0f6fdb0ab2b42ba10fc31b53960166bf2bf`, exported under `inputs/` and
listed in `INPUTS.json`. The scientific checkout base is
`a23bdc1b07be96bea0101d44ae27d14de67a79ed`.
Source-byte authentication belongs to the enclosing package verifier;
`analyze(word)` checks the supplied decoded mathematical object and does not
authenticate a Git commit. No predecessor executable or existing independent
ledger is imported or executed.

For both providers, the reconstructed final profile is

\[
2434H_1+632H_2+286H_3+104H_4+26H_5+8H_8,
\]

with 408 helper widths `{4:26, 5:2, 7:62, 8:100, 9:218}` and exactly 86 named
private cleanup registers. The parent gives

\[
2416H_1+640H_2+280H_3+110H_4+26H_5+8H_8,
\]

widths `{4:26, 5:2, 7:62, 8:96, 9:222}`, and 82 named private cleanup registers.
These are frame-accounting and syntax results, not a new kappa or a supplier
admission.

## Assumptions and exact covered domain

The frame space is `GF(2)^9`, represented by the integers 0 through 511 with
XOR as addition. The register convention is fixed: 112 data registers
`0..111`, 112 target registers `112..223`, and 480 candidate helpers
`224..703`. The 72 explicitly removed helper names leave 632 live registers,
including 408 helpers. The implementation rejects other `h`, `v`, or `R`.
Its input grammar is the exact set of word fields used by these four inputs.
It validates register ranges and live membership, gate tags and arities,
nonzero dyadic scalar coefficients, signed warp references, frame vectors,
and report types. Boolean aliases for integers are rejected.

The adopted cost convention charges one `H_d` for each monotone frame increase
of dimension `d > 0` on an incident register. The two incident registers of an
addition are considered separately. Centre readout descents contribute their
own `H_d` charges. Scalar arithmetic at a frame is not separately charged by
this histogram; neither a native warp routine nor an operator correction is
implemented by this certificate. The zero-frame precondition and compensation
primitives and the initial-correction grammar are checked, but their operator
identities are outside this replay.

All data, target, and helper entrance *values* may be arbitrary dirty values.
A zero frame is the subspace `{0}`, not a promise that a register contains the
number zero. The private cleanup names are the supplier's declared zero-buffer
interface; this replay checks their names and inverse-program syntax, not the
zero-entry or zero-return property of their values.

## Explicit finite subspaces

For generators `g_1,...,g_k`, `frames.py` starts with `{0}` and repeatedly
replaces a set `S` by `S union {x XOR g_i : x in S}`. Induction on `i` proves
that the result is exactly the span of the first `i` generators. Thus the
implementation uses the complete subspace itself, with at most 512 elements.
Containment is subset inclusion and equality is set equality. A subspace's
cardinality is `2^d`, so its dimension is obtained from its cardinality; no
pivot-basis implementation or rank-only containment rule is used.

Each listed B-warp has nine columns whose XOR closure is the complete space.
Its linear map is therefore invertible. Applying that map pointwise to its
declared old subspace must give exactly its declared new subspace. For a
negative signed A-warp, the forward map must instead take the declared new
subspace back to the declared old one. All 72 listed maps and all 24 signed
A-warp applications pass these exact tests. This establishes the finite frame
transport, without establishing native phases or a Clifford realization.

## Chronological invoice and boundary widths

Entrance frames are the lines spanned by the 112 ports on data registers and
the zero frame elsewhere, then overridden by `start_extra`. Terminal frames
are FULL on data and helpers and the port's perpendicular hyperplane on each
target, then overridden by `helper_final` on the named helpers.

The replay consumes every A primitive in order. Before each A-warp, the actual
current subset must equal its declared old subset. After A, each of the eight
centre registers must have its stated centre frame. The distinct readout
levels for that centre are ordered by decreasing dimension, and every level
must be a subset of the preceding one. Their descents are charged separately;
the main B-register carrier retains its post-A frame.

The B loop visits every insertion cut from 0 through `len(B)`, including the
last cut. At a cut it applies listed warps in their actual input order, checks
the exact old subset, and then consumes the B primitive at that cut if any.
It then consumes every restore primitive and climbs every live register to
its actual terminal frame. All 632 live endpoints are included, even when a
register has no positive final climb. There are 434 positive endpoint climbs
for the changed word and 438 for the parent.

| Portion | Parent paid profile | Changed paid profile |
| --- | --- | --- |
| A | `950 H1 + 12 H2 + 18 H3 + 38 H4` | `952 H1 + 12 H2 + 24 H3 + 32 H4` |
| B | `1096 H1 + 518 H2 + 198 H3 + 72 H4 + 26 H5` | same |
| Centre descents | `8 H8` | same |
| Restore | `60 H1 + 38 H2 + 8 H3` | `72 H1 + 38 H2 + 8 H3` |
| Final endpoints | `310 H1 + 72 H2 + 56 H3` | `314 H1 + 64 H2 + 56 H3` |

Consequently the complete local *frame* delta is

\[
18H_1-8H_2+6H_3-6H_4.
\]

The 408 widths are returned in increasing order of the actual live helper
index, as required by the owner interface. Width means
`dim(terminal[h]) - dim(entrance[h])` under this supplier's boundary model.
Only helpers `249,251,265,267`, at zero-based positions `25,27,41,43` in that
ordered list, change width, each from 9 to 8. Their entrance frame is `{0}`;
their changed terminal frame is exactly

\[
E_{45}=\{x\in\mathbf F_2^9:\operatorname{popcount}(x\mathbin\&45)=0\pmod2\}.
\]

The physical residual remains the paired quantity
`T_terminal T_entrance^-1`. Here the four newly changed pairs are
`(entrance={0}, terminal=E_45)`, compared with the parent's
`(entrance={0}, terminal=FULL)`. The width calculation does not certify a
wrapper for either residual, a native phase, restoration of arbitrary dirt,
or the paired row/column isolation equations. Those require the supplier's
operator proof. A terminal rank by itself is insufficient.

There is also an independent rank-mass check inside the analyzer. Invertible
warps preserve dimension, so all ordinary monotone increases telescope to
terminal dimension minus entrance dimension. Data and targets contribute
`112*8 + 112*8 = 1792`; the eight separate centre descents contribute 64.
Hence

```
parent: 1792 + 3314 + 64 = 5170
changed: 1792 + 3310 + 64 = 5166
```

The numbers of positive paid events are respectively 3480 and 3490.
The reconstructed profile and width inventory must also match their actual
input report; the report is not used to generate either quantity.

## Cleanup syntax and private namespace

For these inputs `prelude_events=84`. The cleanup convention excludes this
prelude. The independent reconstruction concatenates `A[84:]`, the chronologically
interleaved B warps and B primitives, and restore. It removes primitives whose
destination is a target. Reversing the remaining stream, it negates every
addition coefficient, reciprocates every scale coefficient, and reverses every
signed warp identifier. Every register `h` in `helper_final` is renamed to
`704+h`; other register names remain unchanged. Every actual cleanup primitive
must equal the resulting primitive, with rational coefficients compared
exactly, and its frame must span FULL. These are checks of the supplied word,
not an invocation of the predecessor's cleanup producer.

The resulting inverse syntax matches all 4,992 changed cleanup primitives and
all 4,829 parent cleanup primitives, with 72 cleanup warps in either case.
The changed A has 3,907 primitives versus 3,785 in the parent; restore has 158
versus 117, and compensation has 5,980 versus 6,156. B has 1,876, cut 176,
and precondition 192 in either word. The API also returns every section's
primitive-tag inventory; these counts do not price native implementations.
The actual distinct cleanup names at least 704 must equal exactly

```
{704 + h : h is a helper_final key}
```

The changed word adds names `953,955,969,971`, corresponding to the four
helpers above. The count rises by four, from 82 to 86. A stale endpoint
dictionary, a missing private name, a damaged full frame, a wrong inverse
coefficient, or a changed inverse order is rejected. Matching inverse syntax
does not establish zero return: that further conclusion needs the forward
non-target operator, dirty-input, compensation, and copied-buffer semantics.
Likewise 86 names do not constitute a chronological physical allocation of 86
available cells, and this count is distinct from any inherited ambient-space
parameter.

## Reproduction and defect controls

From the checkout root, standard-library Python 3.12 or later is sufficient:

```sh
python3.12 -I -O -B research/normal45-owner-cost-bridge/frames.py
python3.12 -I -O -B research/normal45-owner-cost-bridge/test_frames.py
```

Both commands read inputs and emit diagnostics only. The analyzer does not
change the input dictionary. There are no Python `assert` statements serving
as runtime predicates, so the checks remain active under `-O`.

The 23 test methods include input changes for an equal-dimension wrong scalar
subspace, an omitted terminal override with stale cleanup, an incompatible
terminal frame, an omitted endpoint charge in the input report, missing
cleanup names and frames, wrong inverse coefficients and order, a changed
prelude boundary, a noninvertible warp, a wrong equal-rank warp preimage, a
changed B-warp schedule, an incorrect centre frame, a forbidden centre descent,
Boolean and nondyadic coefficients, and a forged width report. Each must fail
its corresponding explicit predicate. Positive controls admit redundant or
reordered frame generators and an equivalent rational coefficient, verify all
four frozen inputs, and check that the supplied word remains unmodified.

## Credit and remaining obligations

The changed word and four extractions are Marius-Paul Dumitrean's PR2942 work.
Mason Hale supplied the PR2917 parent words and owner chronology; Jeremy
Diviney supplied the paired extraction method and compensation architecture;
Jeremy Kothe supplied the inherited frame chronology and inverse-cleanup
convention. The exact accounting convention was inspected in
`research/paired-extension-normal45/vendor/preload_move.py:frame_report`,
without importing it. ToikY's `research/paired-helper-frame-ledger/README.md`
at the scientific base documents the explicit-subset ledger precedent for
PR2917 at `224bd5e56041c40078ff6b5fa7393733a215de5c`; this is a new input-specific
replay of that known method, not a new subspace method. Retained source credits
also include Yiyang Lu, Dugongue, Philippe Van Velzen, Tekalign, and icekylinx.
This implementation, tests, and exposition used substantial OpenAI Codex AI
assistance. They are not independent human review or a formal-kernel proof.

The covered result is the exact finite frame invoice, ordered boundary-width
list, and cleanup syntax/namespace implication for these four inputs under the
declared tariff. This component does not redo the full arbitrary-dirty
operator algebra, target compensation, row/column extraction identities,
native phases, native implementation, buffer-zero proof, owner allocation,
physical stock, source-access charges, precision/tape/compiler realization,
outer recurrence or root admission, or inherited all-size hypotheses. A
chronological owner realization and the native and all-size gates remain
separate obligations; no stronger kappa claim follows from this component.
