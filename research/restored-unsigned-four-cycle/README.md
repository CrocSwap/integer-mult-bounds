# An ordinary four-cycle costs exactly ten with restored dirty donors

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with an exact finite exclusion certificate.
The minimum scalar arithmetic cost of

```text
(x0,x1,x2,x3) -> (x1,x2,x3,x0)
```

is **ten primitives**, even with any finite number of additional arbitrary
dirty registers that must each finish with their own initial value. The
target is the ordinary four-cycle, with no output sign changes. The result
also applies to its inverse and coordinate relabellings.

This answers one new instance of Philipp / mightyOil's
[PR #1303](https://github.com/CrocSwap/integer-mult-bounds/pull/1303), second
Open next question, about further restored-permutation gaps. That package's
disjoint two-plus-three-cycle theorem and signed-four-cycle control are cited
predecessors, not results replayed here. We use its two unchanged, credited
metric-ball engines on the new ordinary-four-cycle endpoint only, apart from
small implementation controls. The new contribution is the endpoint
exclusion, its unbounded-donor application and the resulting exact price.

## Exact interface

Each register initially contains an arbitrary independent real scalar. One
paid primitive is a distinct-register ADD or SUB, unary NEG, DOUBLE or HALVE,
COPY, or CLEAR. There are no free signs, renamings, initialized cells or
discarded coordinates. Every donor is restored individually. Intermediate
rows may be arbitrary dyadic linear combinations. The model and read-only
specialization originate in Ross Richardson's
[#1216](https://github.com/CrocSwap/integer-mult-bounds/pull/1216) and
[#1145](https://github.com/CrocSwap/integer-mult-bounds/pull/1145).

## Reduction to a finite six-register question

The complete required map is invertible, so a distinct-register COPY or
CLEAR cannot occur: it loses matrix rank permanently. Delete self-COPY.
Every remaining prefix is invertible over the dyadic rationals.

The cycle-write lemma of #1303 implies that at least five writes target the
four moved coordinates. For completeness, if all four were written just
once, consider the first such write, to coordinate i. Its only write would
have to produce its final row e_p(i). Coordinate p(i) is still untouched and
has that same row, contradicting prefix invertibility.

A written restored donor needs at least two writes, as in #1216. Before its
first write it has its original basis row. A nonidentity unary scale changes
it, and an ADD or SUB changes it by a nonzero source row. A single write
therefore cannot restore it. A putative word of length at most nine can write
to at most `floor((9-5)/2)=2` donors.

All other donors are read-only. Specialize their independent inputs to zero
and remove their zero-source additions. The universal endpoint identity
still holds on the retained coordinates, and the reduced arithmetic word
has no greater length. This is a lower-bound existence reduction, not a
permission to initialize actual workspace for free. Embed the resulting
word in six registers by leaving missing donors idle.

Reduce `Z[1/2]` modulo three. ADD and SUB remain elementary row additions;
NEG, DOUBLE and HALVE all reduce to row negation. The inverse-closed
six-register generating set has `6+2*6*5=66` elements. Thus it suffices to
exclude the modular endpoint with rows

```text
P = (e1,e2,e3,e0,e4,e5), encoded as 123045.
```

## Complete new endpoint exclusion

Let B be the entire radius-four ball about identity in that metric, with
minimum distances. A word through length eight exists exactly when `AP`
belongs to B for some A in B. A word through length nine exists exactly when
that direct meet succeeds or `gAP` belongs to B for some A in B and generator g.
Indeed write `P=UhV`, where U and V have length at most four and h is one
generator, then take `A=U^-1` and `g=h^-1`. The converse constructs the word
from such a hit. Shorter words are covered by the direct meet. No determinant,
write-order, symmetry or sampling pruning enters the scan.

Both native representations independently enumerate the complete ball and
scan this new endpoint. Each obtains

```text
radius layers       1, 66, 2655, 83270, 2213925
states              2299917
generators          66
middle transitions  151794522 = 2299917 * 66
direct hits         0
middle hits         0
```

The verifier compares the full sorted matrix/distance streams byte for byte,
then hashes that common stream. One engine uses base-three row tables in a
64-bit matrix key; the other uses two-bit entries in a 128-bit key and literal
coordinate updates. Their generation and multiplication implementations
remain the credited source bytes. The repeated ball cardinality is a
prerequisite of the new endpoint query, not a new claim about that ball.
All nine-step modular words are excluded. The preceding reduction transfers
that finite exclusion to every finite number of restored dirty donors.

## Matching exact rational upper word

The first four operations swap coordinates zero and one. The remaining six
cycle coordinates one, two and three, using the predecessor's elementary
swap and three-cycle templates. Their overlapping composition gives the
new endpoint without a temporary register:

```text
x0 += x1
x1 -= x0
x0 += x1
x1  = -x1
x3 -= x2
x1 -= x3
x2 += x3
x3 += x1
x1 -= x3
x1 += x2
```

The checker multiplies the literal rational row operations on every one of
six independent input columns, verifies both donors are unchanged, checks
the inverse word, and rejects all ten single-operation omissions. This upper
witness together with the exclusion proves the exact minimum ten.

## Reproduce and evidence boundary

From the repository root, with CPython 3.12 and a C++17 compiler named `c++`
supporting `unsigned __int128`:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/restored-unsigned-four-cycle
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/restored-unsigned-four-cycle --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/restored-unsigned-four-cycle/verify.py
```

The registered normal and optimized commands both run the complete new
endpoint exclusion, with no quick mode. Expected status is
`PASS_RESTORED_UNSIGNED_FOUR_CYCLE`, `scalar_minimum=10`. A standalone export
needs this directory and the four declared live source files; its verifier
uses no Git or network. `SOURCES.json` authenticates those source bytes before
compilation. The normal metadata launcher separately authenticates their Git
pins and the originating catalogue. Historical provenance is not scientific
acceptance.

An independently represented dense Python radius-four ball supplies small
implementation controls. Both native engines must match every one of its
matrix/distance pairs for the identity and one-/two-negation endpoints. They
must reject invalid dimension and repeated-column domains. Six damaged
endpoint reports are rejected, including missing middle transitions, an
alleged hit, wrong target and a boolean substituted for a dimension. Explicit
exceptions retain all checks under optimized Python.

Replay prints a generated receipt bound to the hashes of every package file
and every live source. `--emit /absolute/path/outside/repository/receipt.json`
also writes it to a new file. Temporary binaries, metric balls and reports
are removed on exit; no receipt or transient output is written in the checkout.
The source code, metadata and full finite query are the reproducible evidence.

This is an exact scalar boundary result. It does not bind a current native
four-cycle caller, remove a paid recursive child, supply a physical frame or
tape layout, or improve kappa. A changed composite boundary, promised inputs,
clean/disposable workspace, free monomial maps, arbitrary scalar multipliers,
joint complex-component arithmetic or nonlinear gates are different models.
Selected #7000 is unchanged. Full supplier, precision, hosting, compiler and
outer-theorem obligations are unrun. Independent human and formal proof-kernel
review are unclaimed. Hosted CI status belongs in the PR body.

## Open next questions

1. Can an actual four-cycle boundary and an adjacent scalar run be synthesized
   below the isolated price ten? First pin that complete caller map and its
   physical frame and ownership ledger. No such caller is supplied here.
2. Can a write-pattern or support invariant replace the large finite ball for
   this exclusion? Start with this fixed endpoint and allow mixed intermediate
   rows. A complete symbolic certificate is missing. This package authorizes
   no larger permutation search and stops at the first exact new price.

The motivations, first steps and blockers are also in `TASK.json`.

## Credit and implementation constraints

Philipp / mightyOil #1303 supplied the cycle-sensitive reduction and ternary
engine, and extended Ross Richardson's #1216 packed engine with the middle
scan. Ross Richardson #1216/#1145 supplied the restored-donor model,
read-only specialization, modular method and elementary upper templates.
ToikY's historical #969 and the credited Sagar Thakrar, faw01, Jeremy Kothe,
Chafik Boukhalfa, icekylinx and supplier lineage retain their predecessor credit.
No predecessor file or notice is modified. The finite-group metric and
matrix identities use elementary classical methods; no literature-wide
priority claim is made.

The new Python wrapper has no recursion, dynamic code evaluation or external
callbacks. Its loops have fixed finite domains or explicit byte bounds. The
native domain is fixed to six registers/radius four for the scientific query
and two registers for controls, with 60-second compilation and 180-second
execution limits. At most two six-register metric-ball files coexist. Native compilation
uses `-Wall -Wextra -Werror`; Python runs warning-strict in normal and optimized
modes. Separate static type analysis is not claimed.

Power of Ten deviations are restricted to the managed Python runtime and
unchanged frozen source engines. Rule 3: dynamic integers, containers and
native hash tables remain, bounded here by the fixed domain and the explicit
`sum(66^k,k=0..4)` state bound, 1 MiB source-file limits and bounded report/ball
reads. Runtime allocator overhead is not measured. A future physical lowering
needs a fixed-storage representation. Rule 4: the inherited native `main`
functions exceed sixty lines. Editing frozen source for a refactor would expand
this result's scope; the wrapper keeps their byte pins and independent complete
stream comparison. A separately authorized engine refactor can address that.
Rule 10: the packed engine's existing 128-bit extension prevents portable
pedantic ISO-only compilation; the warning-strict C++17 builds and explicit
compiler requirement are retained. No warning is suppressed and no native
source change is made here.
