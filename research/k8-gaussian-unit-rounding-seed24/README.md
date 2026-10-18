# Common rounding of static Gaussian helper gauges

**Scoped negative result, with exact finite circuits; no new κ.** Enlarging
static real-dyadic helper gauges to all units of `Z[1/2,i]` does not improve the
unconstrained scalar-cost optimum under the lowering and boundary contract
below. For any finite simultaneous assignment, two explicitly defined
real-dyadic assignments have costs `C0,C1` satisfying

\[
C_G \;\ge\; (C_0+C_1)/2+4N_{\rm odd}.
\]

Here `Nodd` counts helpers with an odd power of `1+i`. Thus one common rounding
costs at least `4Nodd` fewer primitives whenever an odd factor is present.
This is a written proof about a specified scalar circuit class. It does not
assert that rounding preserves an additional precision or physical-admission
constraint, and it does not cover a better Gaussian lowering or boundary fusion.

The selected k8 word gives a concrete comparison over all 237 eligible helpers,
both orientations, every integer exponent and all four unit phases:

| Scalar program | Forward | Backward | Saving per orientation |
|---|---:|---:|---:|
| Retained word with PR696 lowering | 149,002 | 149,018 | — |
| Best single real-dyadic gauge, already in PR1161 | 148,670 | 148,686 | 332 |
| Best single odd Gaussian gauge in this class | 148,944 | 148,960 | 58 |

All winners use L427, which has 123 incident ADDs. The real factors are `1/4`
forward and `4` backward. The odd Gaussian factors are `(1+i)/8` forward and
`4(1+i)` backward. Both boundary transformations, both real components and all
coefficient-work cleanup are charged. The new odd circuits are cheaper than the
original word but are dominated by the known real choice. The 332 saving is
predecessor work, not a new record.

## Exact source and accounting scope

Base: `410026dc5513b87db92ae98571d1d5984c69a983`; assignment seed **24**, drawn
from OS randomness for the user's complex-supplier track. The selected record
at that base is the conditional PR1094 construction with
κ `836330098538459/500000000000000000`. [SOURCES.json](SOURCES.json) records Git
blobs and SHA256 hashes. The verifier checks that the PR1042 local word/programs
are byte-identical to the actual PR1094 provider aliases and checks their
retained receipt bindings. It does not rerun the complete selected cold replay.

The circuit class fixes the real-dyadic ADD topology and all original SCALEs.
A helper has a constant gauge throughout the program. Its entry and inverse
exit use its own two real coordinates, with no boundary workspace or sharing
between helpers. Elementary operations are signed additions, doubling,
halving, negation, copy and clear. COPY and clear cannot occur in an invertible
two-register boundary word, since their singularity cannot be repaired without
another register. Each boundary circuit implements its full map on arbitrary
dirty inputs. Original helper SCALEs are not fused into these boundaries.

In the k8 census, helpers must be cold/FULL (`start=0`, `final=1`), unwrapped,
non-center, and absent from every scalar COPY/clear in either orientation.
Exactly 237 of the 480 helpers qualify. This is narrower than PR1161's 477-helper
search domain and matches the relevant restriction used in PR1214. The complete
one-helper census is [CENSUS.json.gz](CENSUS.json.gz). Simultaneous assignments
are covered by the theorem; a new joint optimum is **not** computed.

Each changed ADD is lowered locally, sharing a coefficient product between its
two target channels. The two existing real coefficient-work registers may be
dirty on entry and are cleared on exit. No new helper or source register is
introduced. Original COPY/clear, SCALE, frame, adapter and recursive-call events
are retained. The finite invoices count every scalar primitive, including
source reads, product preparation, accumulation and restoration. The paid
recursive histogram is compared unchanged, not replaced by the scalar count.

## Proof of the common-rounding inequality

**1. The unit class is complete.** If `z` and `1/z` lie in `Z[1/2,i]`, then
their squared norms lie in `Z[1/2]` and multiply to one. Hence `|z|²` is an
integer power of two. Write `z=(u+iv)/2^s`, remove common factors of two from
`u,v`, and use `u²+v²=2^k`. If exactly one of the remaining integers is odd,
the sum is odd, so it equals one. If both are odd, the sum is two modulo four,
so it equals two. The remaining pair is therefore an axis unit or `(±1,±1)`.
Every unit has the form

\[
g_h=2^{a_h}i^{j_h}(1+i)^{b_h},\quad
a_h\in\mathbb Z,\quad j_h\in\{0,1,2,3\},\quad b_h\in\{0,1\}.
\]

This argument is elementary and all-exponent; the finite unit census below is
a check of its implementation, not its proof.

**2. The exact macro costs.** For nonzero real dyadic `q=±p 2^e`, with `p` odd
and positive, Sagar Thakrar's PR696 copy-initialized circuit has real cost

\[
c(q)=2+\lfloor\log_2 p\rfloor+\operatorname{popcount}(p)+|e|
-[p=1\text{ and }e=0].
\]

Thus `c(2q)-c(q) ≤ 2`; equality occurs at `q=±1`. Ignoring this unit discount
would incorrectly replace two by one. A real or purely imaginary complex ADD
costs `2c(q)`, with signs or exchanged source channels as appropriate.

For coefficient `q(1+i)`, form each real source-channel product once, add it
to both target channels with the required signs, then clear its work register.
This inserts one accumulation into each PR696 word, for cost `2c(q)+2`. When
`|q|=1`, use the source directly twice and clear its initially dirty work.
The signs in `q(1-i)` and multiplication by `i^j` have the same cost.
[model.py](model.py) emits these circuits. Each has the full six-real-register
map `(T,S,W) -> (T+zS,S,0)`; it assumes neither clean work nor independent data.
The cost is for this explicit lowering, not a lower bound for all Gaussian
ADD circuits.

**3. Standalone boundaries have an exact minimum.** The real matrix of
multiplication by `g_h` has determinant `2^(2a_h+b_h)`. Signed additions and
negation do not change the determinant's power of two; each doubling or halving
changes it by one. Each boundary therefore costs at least `|2a_h+b_h|` such
operations. If `b_h=1`, all four matrix entries are nonzero, requiring at least
two additions: diagonal operations and one shear cannot make both off-diagonal
entries nonzero. Entry and exit together cost at least

\[
B(a,b)=2|2a+b|+4b.
\]

The lower bound is attained at phase zero. For `a≥0`, first scale both
coordinates by `2^a`, then apply
`y+=x; x*=2; x-=y`, which multiplies by `1+i`. For `a≤-1`, first scale by
`2^(a+1)`, then apply `x-=y; x/=2; y+=x`, which multiplies by `(1+i)/2`.
Reverse the word and invert each elementary operation for the exit. Real
gauges use direct scaling and its inverse, costing `4|a|`. Other unit phases
cannot beat the lower bound and have identical internal ADD costs, so phase
zero suffices for the optimum.

**4. Round all odd gauges with the same bit.** Discard unit phases and define
two real assignments `g_h^(θ)=2^(a_h+θ b_h)`, for a single common `θ=0,1`.
An original coefficient `q` on `source -> target` becomes `q g_target/g_source`.
If both endpoints have the same `b`, their factor of `1+i` cancels and the two
rounded costs equal the Gaussian cost. If the `b`s differ, the Gaussian
coefficient is a unit phase times `r(1±i)`, while the two rounded coefficients
have magnitudes `|r|,|2r|`. Consequently their average complex cost is

\[
c(r)+c(2r)\le 2c(r)+2,
\]

the charged Gaussian cost. Shared edges between two gauged helpers are included;
rounding helpers independently would invalidate the equal-parity case.

For a real gauge, boundary costs are unchanged. For an odd gauge, the average
rounded boundary cost is `2|a|+2|a+1|=2|2a+1|`, since `a` is integral. Its
Gaussian boundary costs at least four more. Sum over all ADDs and helpers,
then add the unchanged scalar costs, to obtain the stated inequality.
At least one of the two rounded complete assignments is no more expensive than
their average. The real assignments are themselves in the Gaussian-unit class,
so the unconstrained scalar-cost infima agree. This does not prove that an
external admissibility predicate is closed under rounding.

## Finite coverage and verification

For one helper, the real objective is `4|k|` plus its incident real-ADD deltas.
The odd objective is `2|2a+1|+4` plus the incident shared-product deltas. Both
are affine between integer coefficient-exponent breakpoints; unit discounts
only lower breakpoint values. The odd boundary kink is at `-1/2`, so include
both `-1,0`. The two outward tail slopes are `4+2d`, where `d` is the number of
incident ADDs. Every integer minimum is therefore attained in the recorded
finite breakpoint set. No heuristic cutoff or random search is used.

[CERTIFICATE.json](CERTIFICATE.json) records 5,166 breakpoint evaluations across
both orientations, the complete minima, actual emitted primitive-stream hashes,
unchanged paid histograms, and eight simultaneous common-rounding fixtures.
The baseline, real winner and odd winner each pass all 712 formal complex input
columns (equivalently 1,424 real columns), including 480 arbitrary dirty helpers
and eight private centers. All 464 distinct macro fixtures check six real input
columns, including both arbitrary dirty work registers; 66 boundary pairs check
their exact maps and inverses. The complete literal positive envelopes remain
52 bits forward and 68 backward for all three variants; the inherited 192-bit
charge is retained. These finite envelopes do not discharge the all-size
precision/tape obligation.

[independent.py](independent.py) separately reconstructs the helper domain and
incident coefficients, enumerates all integers in a provably sufficient interval,
and prices them by the literal pinned PR696 lowerer. It uses neither the
producer's cost formula nor its breakpoint search. [INDEPENDENT.json](INDEPENDENT.json)
records 13,684 grid evaluations, 1,115,016 incident-term evaluations, 2,532
literal coefficients, and 3,488 distinct Gaussian inputs classified by checking
their actual reciprocal (64 units, 3,424 nonunits). Both implementations are by
the same AI-assisted author; this is not independent human review.

Sixteen controls reject missing product initialization, omitted accumulation,
wrong cross-channel sign, uncleared dirt, missing/inaccurate inverse boundaries,
aliasing, invalid coefficient support, nondyadic coefficients, Gaussian nonunits,
zero factors, a false unit-cost inequality, false independent rounding, and
missing or modified source bindings. Certificates are compared canonically;
compressed output equality is based on decompressed content.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 scripts/research_package.py --package research/k8-gaussian-unit-rounding-seed24
```

The three registered commands print:

```text
PASS_GAUSSIAN_UNIT_COMMON_ROUNDING helpers=237 orientations=2 real_saving=332 odd_saving=58 controls=16
PASS_INDEPENDENT_LITERAL_GAUSSIAN_GRID
PASS_GAUSSIAN_PACKAGE_CONTROLS read_only_export=2 corrupted_artifacts=3 equivalent_gzip=1
```

Direct `python3 -I -O -B research/k8-gaussian-unit-rounding-seed24/verify.py`
and the corresponding `independent.py` command are also supported. Default
replay is read-only and offline. `--write` on either script regenerates only
this package's own receipts. Metadata/provenance checking uses full Git history;
direct replay needs only the package and the pinned input files.

This is a scalar circuit result and a scoped cost obstruction. Native/global
admission, the selected cold replay, compiler/realization, whole-call hosting,
roundoff, tape, recovery and analytic obligations have not been newly verified.
No supplier is installed, no selected certificate is changed, and no κ gain,
arbitrary-circuit optimum or Lean multiplication theorem is claimed.

## Open next questions

Can sharing a coefficient product **across distinct ADD macros**, while restoring
all dirty state and respecting chronological frames, break the inequality used
here? A useful first test would be an explicit two-ADD word whose complete bill
beats the sum of the two macro bills. That needs a new local interface and full
frame/precision accounting; a larger static Gaussian exponent search adds no
new evidence within this class.

Can a joint boundary circuit across multiple helpers reduce the sum of the
standalone determinant charges? Opposite determinant exponents make this a
different problem. Start with two helpers and an exact four-real-register
boundary map; all source restoration and subsequent coefficients must be priced.
Neither possible escape is asserted to work. Structured questions and the
changed catalogue scope are in [TASK.json](TASK.json).

## Credit and disclosure

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in the argument,
implementation, verification and writing. New work is Apache-2.0. Credit
Sagar Thakrar's PR696 coefficient lowering; woklerx's
[PR1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161)
at `d210969d3158a1e6c505e41f67dd84e555c88564`; Hanson's
[PR1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214)
at `26162c56ec9c50a80e49949f36d4dd9a137a76a6`; and the retained complex-supplier
lineage of icekylinx, Jeremy Kothe, Rohan Arun and the other contributors credited
in Douglas Colkitt's PR1094 review. No pending predecessor implementation is
vendored or required. Source licenses and frozen evidence remain unchanged.
