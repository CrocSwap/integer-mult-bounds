# Four bits also suffice inside the first physical P104 collector

The actual two rank-seven native recipes at events 2031 and 2033 admit an
integer implementation that rounds after every binary butterfly and still
cleans the private collector to exactly zero. Four extra fractional bits
suffice throughout both recipes. They are also necessary for this fixed
uniform nearest-even implementation on arbitrary entrance-grid data.

This closes the first open question of ywz65's
[PR2730](https://github.com/CrocSwap/integer-mult-bounds/pull/2730), which proves
the completed-output contract but leaves internal execution open. It adds a
source-bound census of every internal prefix and an in-place integer kernel.
The general Gaussian denominator calculation is prior work, including
[Alejandro Zarzuelo Urdiales's Gaussian parity package](../gaussian-parity/README.md).
The new check is the correlated return through these exact physical charts,
the literal collector boundary, and its explicit finite implementation bill.
No predecessor executable is imported.

## Contract and exact sources

Let `h=2^-b`, `b>=0`. All real and imaginary coordinates of the five dirty
sources `D31,D30,D29,D28,D27` and dirty query `Q7` enter on `h Z`.
The sources are read only. The private collector starts at zero, receives
their sum `S`, undergoes `U`, is added once to `Q7`, undergoes `V`, and has
the same sources subtracted in reverse order. Each array has 512 complex
coordinates. The endpoint is `Q7'=Q7+US`, unchanged sources and `C=0`.

The buffer uses the fixed grid `(h/16) Z[i]` throughout, including the return.
Nearest-even quantization occurs after each pair update. Monomial coordinate
permutations, powers of `i`, and unit ADDs are exact. No overflow is allowed.
The final returned collector is on the original h-grid, so conversion back
to that grid is exact. The query remains on the fine grid.

[SOURCES.json](SOURCES.json) authenticates the unchanged word, full native
archive and source README from PR2730 head
`99a81c88d095bbde548d3e67cdb986009cb3e99e`. Their lineage is Arham Tahir's
PR2665 `f9e96e979b7630b7a70705c9774d00fc07014110` and ywz65's physical dual
PR2586 `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`. Original source notices
are retained in [the source README](inputs/PR2730-README.md).

The replay tracks all 2,025 preceding frame events, checks all five entrance
frames and the query frame, matches the exact fifteen collector instructions,
and binds both recipes to their unique native event occurrences. This checks
frame availability, not numerical grid availability through a rounded prefix.
The physical chart/compiler correctness remains inherited from the sources.

## All-input internal proof

For one address pair, write its complex values as `a+ib` and `c+id`.
The native factor `C=((1+i)I+(1-i)X)/2` writes

```
((a-b+c+d)/2, (a+b-c+d)/2)
((a+b+c-d)/2, (b-a+c+d)/2).
```

There are seven such binary-coordinate stages between two Gaussian
monomials per recipe. Each monomial is a coordinate permutation with phases
in `{1,i,-1,-i}`. `inplace_native` in [verify.py](verify.py) executes exactly
these integer operations. Four numerator scratch slots keep both inputs
available until all four outputs have been computed. Monomials execute in
place by cycles, using the same scratch slots and a 512-bit visited set.

Treat a buffer integer as its physical value divided by `h/16`. On the
real basis input `h e_j`, its integer value is `16 e_j`. The checker executes
every prefix on all 512 such columns. Every halving has an even numerator.
The matrices are complex linear, so the imaginary basis columns are their
`i` multiples. Thus this covers all 1,024 real basis directions, and every
Gaussian-integer combination of them. Induction over the pair updates proves
that quantization is the identity for every allowed input. This linearity
argument applies to the exact path after divisibility has been established;
it does not assume that a general rounded program is linear.

The least extra fractional bits for each prefix matrix are:

| Prefix | Before binary stages | After stages 1 through 7 | After final monomial |
|---|---:|---|---:|
| Outbound, applied to `S` | 0 | 1, 1, 2, 2, 3, 3, 4 | 4 |
| Return, applied to the actual `US` | 4 | 3, 3, 2, 2, 1, 1, 0 | 0 |

The return line describes `V_prefix U`, not arbitrary fine-grid inputs to
`V_prefix`. This correlation is essential. For all 512 columns the final
composition is the identity. Consequently the return is exactly `S` and
the five cleanup ADDs erase `C` exactly. The one-way query write leaves
the collector unchanged.

As a separate check on the native arithmetic, both completed recipes on all
512 coarse basis columns agree with the closed tensor coefficient formula
`(1-i)(-i)^k/16`, surrounded by their actual monomials. The in-place kernel
also agrees with the prefix evaluator on all forward and correlated-return
columns. This is a finite exact certificate with an all-input argument,
not a proof-assistant result or independent human review.

For sharpness, set `D31=h e_0` and the other inputs to zero. With a uniform
guard `g=0,1,2,3`, nearest-even rounding after each pair loses this vector
by the outbound endpoint. The query and returned collector are zero and
cleanup leaves `-h e_0`. All four literal in-place executions are checked.
This is necessity for this fixed schedule and quantizer. Different arithmetic
algorithms, retained residues and restricted entrances are outside that claim.

## Range, storage and finite operation bill

Assume every real and imaginary entrance component has magnitude at most `B`.
Then `S` has component magnitude at most `5B`. For each prefix matrix `A`,
the checker sums `abs(Re A_ij)+abs(Im A_ij)` along every row. The exact maximum
row bounds in the same order as the grid table are:

```
outbound: 1 | 2, 2, 4, 4, 8, 8, 16 | 16
return: 16 | 8, 8, 4, 4, 2, 2, 1 | 1
```

Therefore every stored collector component is at most `80B`, including all
internal stages. Query components are at most `81B`. A scratch numerator,
including a partial sum of its four signed terms, is at most `320B`.
These are sufficient bounds. They do not claim minimal range.

The private payload is 1,024 signed integers on the h/16 grid. Compared with
b fractional bits, it needs 4,096 additional fractional storage bits. The
persistent fine-grid query separately needs another 4,096 bits. The native
microprogram also needs four signed scratch integers with physical range
`320B`, a 512-bit visited set, and a static monomial table containing 2,048
destination/phase records. Nine destination bits and two phase bits per record
give 22,528 table payload bits, excluding table framing and control code.
No additional full vector or rounding-history register is required by the
in-place arithmetic kernel. The offline verifier retains more data for checks.

For example, an explicit sufficient signed width for a scratch integer is
`1+ceil(log2(320B*2^(b+4)+1))` bits. Analogous formulas with `80B` and `81B`
bound the collector and query. This prices magnitude as well as fractional
precision; it does not assume that unbounded integers occupy constant space.

| Quantity for this one complete collector | Count |
|---|---:|
| Binary pair updates in the two native recipes | 3,584 |
| Real ADD/SUB operations in those updates | 43,008 |
| Exact real halvings | 14,336 |
| Real unit ADD/SUB operations in five gathers, query and five cleanup writes | 11,264 |
| Complex monomial placements | 2,048 |
| Real monomial negations | 2,048 |

Each four-term numerator uses three real ADD/SUB operations. The monomial
phase census is 512 occurrences of each power of `i`. The source-level
invoice remains two rank-seven children, eleven unit ADDs, one zero allocation
and one exact erasure. The scalar expansion above implements the two fixed
512-coordinate maps. It is not an additional recursive-child invoice and
does not prove that scalar expansion has the cost promised to an arbitrary
recursive caller. Traversal, reads/writes, descriptor access and physical tape
movement are not priced as real ADDs in this table.

## Reproduce and controls

Python 3.12 or later, standard library only:

```sh
python3.12 -I -B research/p104-internal-grid-collector/verify.py
python3.12 -I -B research/p104-internal-grid-collector/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-internal-grid-collector
```

The exact census checks 9,216 correlated prefix columns, 1,024 closed-form
native columns and the in-place endpoints. Five dense fixtures populate all
dirty sources and the query. Controls cover every insufficient guard, wrong
cleanup sign, wrong inverse phase, and an arbitrary h/16-grid return entrance
outside `U(h Z[i]^512)`. Source checks precede parsing and execution. Full
receipt comparison distinguishes integers from Booleans and rejects duplicate
JSON keys. Export and failure tests are described in [test_verify.py](test_verify.py).

The registered replay and six package tests passed locally on CPython 3.12.15
and the package tests also passed on CPython 3.14.8, macOS arm64. The repository's
70 research-workflow tests passed on 3.12.15 with three skips. A separate local
review reconstructed all prefix columns using unreduced integer denominators
and independently reproduced the lattice profile, row bounds and inverse.
Hosted CI and independent human review are not claimed.

The Power of Ten inspection keeps the arithmetic loops bounded by 512
coordinates, seven stages and two recipes, with no recursion. Every function
is below 60 physical lines. Python big integers and diagnostic prefix arrays
allocate dynamically, a managed-runtime deviation. Their live sizes are bounded
per invocation by these fixed dimensions and the input integer bit length;
the explicit kernel storage bill above is separate from verifier memory.
No compiler is present. Optimized replay, warning-enabled compilation and
behavioral failure tests are the local diagnostics. A physical implementation
must replace managed buffers with the stated finite capacity before claiming
that storage bill at runtime.

## Family decision and limits

Narrow and finish this local precision obligation. The finite kernel preserves
the completed map under internal pair rounding at the same four-bit guard.
This does not supply entrance grids from a rounded physical prefix, admission
of the exact query to later consumers, recursive-child cost, whole-word range
or precision, owners, hosting, physical tape work, remaining 102 forward
corrections, all-size admission, a favorable complete supplier or a new kappa.
The current selected frontier is unchanged. No further construction round is
justified solely by this local precision closure.

## Open next questions

- Can a real rounded prefix supply these five coarse entrance grids and can a
  subsequent consumer retain the fine query? Trace one actual producer and
  query reader, including magnitude and paid conversion costs. The existing
  local proof assumes the entrance grids and does not supply that caller.
- Can the recursive child interface realize this exact fixed-grid arithmetic
  within its promised cost? First derive a bit-operation, access and movement
  bill for one admitted recursive representation. The finite scalar expansion
  and unitary chart identity alone do not imply that cost contract.

## Credit and freshness

Credit ywz65 for PR2730's mixed-grid contract and handoff, Arham Tahir for
PR2665's actual collector and rounding obstruction, ywz65 for PR2586's physical
dual, Nick Petalas for the PR2549 precision question and PR2550 complementary
frames, and Alejandro Zarzuelo Urdiales for the Gaussian parity work. The
retained source README records the complete native/compiler and P104 lineage.
These source-specific credits and notices remain unchanged. Apache-2.0.

Base main `34588a98dabb668d4c53e5e776cd7b3927174d26`, priority revision 5.
Task selection, source pins, scope, overlap coverage and verification are in
[TASK.json](TASK.json). The canonical investigation is
[Discussion #2750](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750).
The pre-submission fetch at 2026-10-15 20:16 UTC found canonical main
`5e83b4caaafcee18c3e88580db5af6dfe4bc4121`. Guidance, selected result and
replay dependencies are unchanged; the scientific source pins above remain fixed.

## Maintainer integration: provenance-only selection

The selected-record pin records the historical frontier at submission; this
local collector calculation never reads that record. Its original hashes remain
in SOURCES.json as provenance. VERIFY.json now lists no external runtime
inputs; the authenticated local word and native recipes remain unchanged.
The complete numerical receipt is unchanged.
