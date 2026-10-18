# Independently corroborate PR3090's scalar-capacity claim

A separately implemented replay corroborates all twelve
[PR3090](https://github.com/CrocSwap/integer-mult-bounds/pull/3090)
policy/provider/orientation comparisons at exact head
`47a2bcec53667f490df6d40550e14a8ae465cba4`. **No defect was found in the checked
arithmetic scope.** This is additional verification coverage, not another
construction claim, a physical implementation or a new kappa.

| Covered prelude/A arithmetic, per provider/orientation | Corroborated result |
|---|---:|
| Scalar macros | 9,992 |
| Scratch-control real instruction slots | 64,782 |
| Either digit-walk real instruction slots | 57,710 |
| Common fractional bits | 7 |
| Common signed width at 64-bit normalized input | 84 |

The generic recipes and their saving belong to PR3078. PR3090 binds their
construction microstates to PR3089's native capacity. This audit adds an
integer engine that **independently propagates the original normalized
scalar/warp stream**, as well as interpreting the serialized unit recipes.
It corroborates the existing 7,072-slot saving and unchanged capacity; it
does not claim priority for either result. Counts include both real
components, before tensor-coordinate replication. They are not Boolean gate
counts, physical timings or optimality claims.

## Added checking coverage

```
fresh frozen native generator
  original scalar/warp stream
    Fraction normalized rows + recipe execution
    independent integer normalized rows + serialized recipe execution
      every changed recipe-row prefix digest must agree
      original scalar/warp endpoint digest must match PR3089
  twelve derived recipe/capacity/census comparisons against PR3090's receipt
```

PR3090's coefficient interpreters share the native normalized-row propagation.
Here the integer engine starts from all 632 original input columns and has
its own ADD, SCALE and reduced warp-word propagation. It does not call the
native propagation helper or receive the Fraction engine's per-macro inputs.
Thus an error in those shared per-macro inputs cannot make both new engines
agree silently. A two-macro dirty-source fixture checks explicit final rows
while making calls to the native propagation helper fail.

No PR3090 executable source is imported or run. Only its frozen claimed
receipt is read. The compiler, PR3078 recipe selector, Gaussian-monomial
interpretation and PR3089 native-frame theorem are deliberately reused.
This is not independent verification of those inherited dependencies, nor
independent human or proof-kernel review.

The exact comparisons include macro/instruction counts, source writes,
scratch-using macros, all twelve recipe hashes, scalar grid/norm/width and
combined native grid/norm/width. Witness labels and observation counts are
not compared. This audit also observes recipe entrances, so their first
witnesses/counts can differ without changing the mathematical envelopes.
[RESULT.json](RESULT.json) records both derived evidence and the comparison.

## Checked arithmetic statement

Let every initial normalized input component be an integer in `[-L,L-1]`,
where `L=2^(P-1)` and `P>=3`. Retain PR3089's exact residual-adapter endpoint,
canonical-frame and Gaussian-monomial hypotheses. Execute the literal
zero-frame prelude and ordinary A stage, stopping immediately before centres.
Each orientation includes 9,992 scalar macros, 96 interspersed logical warps
and 1,020 A climbs. The source-digit policy temporarily writes its source and
restores it. The target-digit policy never writes its source. Scratch
fallback recipes remain charged and return initially-zero scratch to zero.

For each policy the independently replayed sufficient envelopes agree with
the pinned claim:

| Arithmetic | Forward D | Forward bound | Backward D | Backward bound |
|---|---:|---:|---:|---:|
| Scalar recipe prefixes | 5 | `2928 L` | 7 | `550 L` |
| Including inherited frame/C arithmetic | 5 | `4896 L` | 7 | `934 L` |

These are sufficient bounds, not minimum-width theorems. Union with the
inherited native arithmetic leaves separate widths `P+18` forward and
`P+17` backward unchanged. On the common grid `2^-7`, `P+20` signed bits
suffice, or 84 bits at P=64.

### Why recipe prefixes are covered

An actual normalized row is `sum q_(v,w) K_w x_v`, with dyadic q and
Gaussian-monomial warp words K. A real rational scalar instruction commutes
with the common complex frame. Therefore every local recipe register,
including scratch under construction, equals that frame applied to the
corresponding propagated normalized row. A zero scratch field initially has
every frame. Its provision and movement remain physical obligations.

After every instruction the checker reduces equal formal atoms, then measures
maximum denominator depth d and coefficient l1 norm N. For a rank-r canonical
frame, PR3089's paired Fourier bound adds `ceil(r/2)` fractional bits and
multiplies the symmetric real-component bound by `2^ceil(r/2)`. The resulting
physical component has grid depth at most `d+ceil(r/2)` and magnitude at most
`L*N*2^ceil(r/2)`. Actual monomial coincidences can only reduce this sufficient
bound. The inverse-transpose orientation uses conjugated frames.

The separate integer engine propagates the original rows with denominator
`2^32`, reads the emitted JSONL instructions, checks every division remainder
and reproduces every changed-row digest. A half instruction is exact on the
physical common grid because its resulting row still lies on that grid, so
its incoming encoded integer is even. The strict signed condition is

```
L * B * 2^D < 2^(W-1).
```

For the common format, `4896*2^7 < 2^20` proves `W=P+20` for every P>=3.
Strictness permits negation of the most negative input. Endpoints, source
restoration and scratch return are checked at every macro, so the inherited
correlated native-frame bound continues to apply at the next event.

## Reproduce

Python 3.12, standard library only. From the repository root, choose a fresh
external session directory RUN:

```sh
mkdir -p "$RUN/tmp"
export PYTHONPYCACHEPREFIX="$RUN/bytecode"
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-scalar-microstates/verify.py --work "$RUN/replay" > "$RUN/result.json"
cmp "$RUN/result.json" research/rank7-scalar-microstates/RESULT.json
TMPDIR="$RUN/tmp" python3.12 -O -W error -B \
  research/rank7-scalar-microstates/test_microstates.py
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-scalar-microstates
```

The twelve inspectable JSONL expansions and fresh native outputs live only
under --work. That option refuses existing paths or paths in the checkout.
Without it, temporary outputs are removed. Direct replay needs no Git or
network; the generic hook also checks historical Git provenance.
[SOURCES.json](SOURCES.json) pins the baseline and catalogue.
[VENDOR.json](VENDOR.json) pins 25 reused files by exact source commit,
Git blob and SHA-256. Frozen bytes and notices are unchanged.

Seventeen behavioral groups cover explicit `7/8`, `3/8`, `3/2`, `-7/4` cases,
3,072 signed numerical recipe executions, independent original-row
propagation, wrong division, missing source restoration/clear, malformed
instructions, literal frame/event binding, truncation, source corruption,
endpoint-correct hidden grid/overflow, insufficient grid/width and corrupted
claim comparisons. Contracts remain
active under optimization. [CHECKS.json](CHECKS.json) records execution
commands and environments; [ENGINEERING.md](ENGINEERING.md) states limits.

## Scope and concurrent work

This work initially took PR3089's released coefficient-construction handoff.
The three policies were measured and checked before the submission refresh
found concurrent PR3090. The task was then narrowed to this explicit
corroboration, with its additional independent original-row replay. The
construction scope is superseded by PR3090, which retains its credit. No
other branch, selected record or shared compiler is changed.

Stop at this bounded audit. Adapter interiors, producer delivery, clean
scratch provision, physical copy/clear/shift/ADD, routing, consumer precision,
recursive approximation and the complete physical/recursive/outer invoice
remain **unknown here**, not priced as zero. CLEAR is a counted exact
arithmetic primitive, not a synthesized reversible bit eraser or restoration
of arbitrary borrowed scratch. Non-scalar costs and the paid child profile
are unchanged. No supplier admission or selected-frontier update follows.

## Open next questions

Can one residual adapter supply the required A entrance values at this
capacity? Start with a literal pre-A adapter and its dirty-state range.
Its physical interior, access and full bill remain unproved.

Can a bit-level caller implement an actual non-half coefficient such as
`7/8` with paid copy, shifts and scratch erasure? Start with the aligned ADD
machinery from PR3080/3081. Clean stock, reversible cleanup, routing and
non-ADD costs remain blockers.

Can the later consumer avoid repaying the arithmetic saving? Start with the
first centre conversion from the exact normalized A exit grid. Its precision,
ownership and complete invoice are outside this audit. Structured questions
are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed this separately implemented arithmetic audit.
PR3090 is the concurrent construction report; PR3089 supplied the native
frame/C bound and PR3078 the scalar recipes. Retain credit to
PR3086/3084/3083, PR3076/3060/3056, dcharb78/PR3042, Jeremy Kothe/PR3015,
Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226, DLamdata, eumemic/PR411,
icekylinx, Tekalign and the retained geometry/native/owner lineage. Frozen
credit/license notices are included unchanged. New work is Apache-2.0.
Development used substantial automated assistance. No independent human
review is claimed.
