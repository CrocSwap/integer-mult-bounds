# Fractional-grid audit of bidirectional Horner

**Mathematical audit / finite precision-interface result; no new κ.** The
bidirectional Horner circuits in [#837](https://github.com/CrocSwap/integer-mult-bounds/pull/837)
preserve their exact endpoint maps and improve primitive counts. Their
intermediate fractional-grid requirement can nevertheless increase. This
package quantifies that previously unresolved precision obligation.

For the complete **scalar primitive projections**, the exact minimum number
of fractional guard bits beyond the input grid is:

| Program | Forward binary/NAF baseline | Bidirectional | Change |
|---|---:|---:|---:|
| CK forward | 3 | **5** | +2 |
| CK backward | 8 | 8 | 0 |
| JP8 forward | 4 | 4 | 0 |
| JP8 backward | 27 | 27 | 0 |
| SW4 forward | 3 | 3 | 0 |
| SW4 backward | 19 | 19 | 0 |

These values are necessary and sufficient for **every intermediate to remain
exact for every input on the initial dyadic grid**. A shared guard covering
both orientations is unchanged: **8 for CK, 27 for JP8, 19 for SW4**. This is
not a counterexample to the selected #799 construction, a claim that its
physical precision reserve is inadequate, or a full compiler precision budget.

At the individual coefficient interface, **18 of 962 coefficients** require
one or two additional bits under #837's chosen circuits. They occur in 21 CK,
4 JP8 and 5 SW4 additions per orientation. Local requirements do not add
across macros: actual source divisibility and other larger requirements can
absorb them, as the full traces demonstrate.

## Concrete fixed-grid counterexamples

For `t += (31/8)*s`, with `s=1`, `t=0`, forward NAF uses 12 real primitives
and needs three fractional bits. Reverse NAF uses 11 and needs five. On a
three-bit fractional grid, rounding each halving toward minus infinity gives
**4 instead of 31/8** with the reverse circuit. Five bits restore exactness.
All copies, additions, subtractions and doublings are exact in this model;
the integer part is unbounded. Arbitrary incoming coefficient work is cleared
by the same pinned circuits.

There is also a complete-word witness. Set native input column 16 to 1 and
all other native/private inputs to 0 in CK forward. The baseline at three
guard bits has no discarded halves and the correct endpoint. The reversed
program on that grid has three discarded halves and these endpoint errors:

| Register | Error |
|---|---:|
| source `L43` | -1/8 |
| dirty helper `L422` | +1/8 |
| dirty helper `L425` | +1/8 |

Four bits still leave errors at `L43` and `L425`. Five bits produce the exact
endpoint with no discarded halves. The first loss occurs in event 22014's
`-31/8` coefficient work. This is a literal integer-grid execution of the
entire scalar projection, not an inference from a large denominator alone.
In general, an unrepresentable intermediate need not imply a wrong endpoint;
the explicit execution establishes that additional fact for this witness.

## Reproduce

Python 3.11+, standard library, offline, no writes by default:

```sh
python3 -B -I research/dyadic-fractional-grid/verify.py
python3 -B -I research/dyadic-fractional-grid/crosscheck.py
python3 -B -I research/dyadic-fractional-grid/test_grid.py
```

Expected main marker:

```text
PASS_DYADIC_FRACTIONAL_GRID programs=6 coefficients=962 extra_grid_coefficients=18 kappa=unchanged
```

The independent checker reports `PASS_FRACTION_GRID_CROSSCHECK` for all twelve
complete traces: six programs under each lowering. Nine focused tests run in
the last command. `verify.py --write /new/path.json` reconstructs the receipt
and refuses an existing destination. [EXPECTED.json](EXPECTED.json) contains
every coefficient, candidate depth, full-program trace digest, sharpness
witness and rounding counterexample. [VALIDATION.md](VALIDATION.md) records
the executed checks and limitations.

## Exactness criterion and proof

Let inputs lie in `2^-p Z^N`, and let every scalar primitive use the fixed
grid `2^-(p+g) Z`, with an unbounded integer part. Let `P_j` be the exact
linear map after primitive j, including arbitrary initial native and private
inputs. Clears are linear projections and require no invertibility. Define

```text
D = max over all j, rows r and columns c of
    log2(denominator of the reduced dyadic coefficient (P_j)[r,c]),
```

with zero and integer coefficients contributing zero. **Every prefix is
exactly representable for every input if and only if `g >= D`.**

For sufficiency, write an input as `2^-p z`, `z in Z^N`. If every coefficient
denominator divides `2^g`, each coordinate of every `P_j 2^-p z` belongs to
the working grid. Induction over primitives then makes any rounding rule
that fixes grid points exact at every step. For necessity, take a coefficient
with reduced form `a/2^D`, a odd. Input `2^-p e_c` produces
`a/2^(p+D)` at that row and prefix, which is outside every grid with `g<D`.
The committed witness names the primitive, register, column and odd numerator.

Magnitude bounds and this denominator bound address different quantities.
A small value can require many fractional bits. #837's positive-prefix
envelopes remain valid; they did not settle this fixed-grid obligation.
The table counts fractional guard bits, not total register width; headroom
for the integer part must be budgeted separately.

For a reduced coefficient `q = sign*a*2^e`, a positive odd, let a chosen
binary or signed expansion have height h and least digit `d_0=±1`. Reverse
Horner's work after digit i is

```text
d_0 * (sum(d_j*2^j, j=0..i)) / 2^i * s.
```

The numerator is odd, so the source coefficient has denominator exactly
`2^i`. Final shifts either reduce that depth or extend it to the reduced
denominator depth `k=max(0,-e)`. Hence reverse Horner's exact local depth is
**max(h,k)**. Forward Horner first forms an integer numerator, then halves k
times, so its depth is **k**. Unit shortcuts have depth zero. The checker
confirms these formulas on all **3,842 candidate circuits** for the full
962-coefficient census, including candidates that do not win on gate count.

## Implementations and scope

[rows.py](rows.py) represents each complete row by integer numerators and one
normalized binary denominator. Exact cancellation and common powers of two
are removed after every operation. The main replay checks all 716+9 CK/JP8
or 728+9 SW4 arbitrary input columns, macro boundaries, final maps, private
erasure, original event inventory and unchanged paid profiles. All twelve
depth maxima have sharpness witnesses independently evaluated with ordinary
`Fraction` arithmetic on a single basis input.

[crosscheck.py](crosscheck.py) separately represents every coefficient by a
`Fraction`, recomputes every target-row depth at every primitive, and compares
the complete depth-stream digests, maxima, costs and endpoints. It does not
use the integer-row operations. [fixed_grid.py](fixed_grid.py) uses integer
registers and directed halving for the 18 local and complete CK counterexamples.
The tests reject altered witnesses, missing copy/halving/clear operations and
undercharged grids; they cover cancellation, zero rows, source preservation,
negative rounding and signed/unreduced raw denominators.

These programs are **scalar projections**: native frame labels are retained,
but frame changes, phases, recursive children and physical realizations are
not evaluated as numerical operators here. The table therefore does not
certify a full physical fixed-point or floating-point implementation, rounding
error stability, integer overflow, coefficient preparation or asymptotic
precision/tape bounds. It supplies one exact finite obligation for future
integration. No production lowering, selected artifact or `upstream/` file is
edited, and no new κ follows.

## Sources and attribution

Base: **f567884aeb8851b6e794af1184119a3bfbe1e631**, where #799 is selected.
The investigated #626 and #741 programs are historical checkpoints.
[SOURCES.json](SOURCES.json) binds their records, manifests, SPECs and program
payloads. Gzip/tar inputs are compared through the consumed payloads; committed
container/Git hashes are retained separately for provenance.

Our **#837** lowering at `0a2977195efc8fb2a918fbfb694ec8d294387f08` is vendored
verbatim, including Sagar Thakrar's **#696** binary copy/unit module and its
notice. Credit Sagar's **#723** for forward NAF, Chris Pagolu's **#734** for
bounded forward-Horner prefixes, and the earlier #787 composition. This audit
does not retract their exact symbolic circuit counts or endpoint identities.

Credit icekylinx, Jeremy Kothe, Chafik Boukhalfa, DreamingOfClouds, Rohan Arun,
eumemic and the retained #622/#626/#741 construction and verification lineage.
Related #821 studies inter-replica magnitude growth, #830 transposes batched
work and #764 bounds cyclic-scan rounding; their precision questions differ
from the within-coefficient fixed-grid issue here. The local [claim](CLAIM.json)
records seed **60**, alternatives, scope and the absence of a coordination
issue.

Prepared for **Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance**. Apache-2.0. Both new implementations were written by one AI
agent, not independent human reviewers. The written finite-grid proof and
exact replays do not formalize the complete multiplication theorem; inherited
compiler, realization, hosting, precision/tape and analytic assumptions remain.
