# Independent compact ADD pass-vector review

**Verdict: PASS; no blocking issue found in the successful-call vector.**

This is a separate OpenAI-assisted review by the native-physical agent for
@CubeJerry, using shared immutable source. It does not read or import
`audit.py`, run a numerical table, benchmark, or execute the full word.
It is not human or proof-assistant verification. Source census and tariff
unit conversion are separate lead-review obligations.

## Source pins and replay

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

| Retained file | Public commit | Original Git blob |
|---|---|---|
| `kernel/compact_tables.py` | `38cd824c60f2bb5c6f2603f848a9487cb3a57965` | `b90ecb6052e270095fdd048f992f9fc786f3f8c7` |
| `kernel/machine.py` | `ab239cb6ee884e7a900dd9101c34448077fad0b0` | `acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592` |
| `kernel/exact_builder.py` | `13193a22b1070a74a8580c5d3ea27470443f815a` | `1cc22f75fbe53d48b84be42782e581c04820cd49` |

From this review directory:

```sh
python -I -B independent_vector.py /path/to/research/literal-tariff-conversion-audit --output RESULT.json
```

Expected `PASS_STATIC_INDEPENDENT_VECTOR`; executed successfully. The
script authenticates SHA256 pins and counts literal ordinary-state AST
bodies. It does not assume the claimed vector. Its manual premises are
the universal traversal and lifecycle arguments below; it is not a
general Python cost verifier.

## Literal primitives and emitted paths

On a valid nonblank codeword, `CodedPort.read` has one initial BLANK-test
read plus three code-bit reads, three forward moves and three return
moves: `(4,0,6)` physical reads/writes/moves. `write` uses three `emit`
calls plus three return moves: `(0,3,6)`. Either successful ordinary
coded move uses one read and three moves: `(1,0,3)`. Right-frontier
materialization adds nonnegative work; left-origin crossing rejects.

`Builder.emit` appends exactly one row. Its `goto` and `branch` each call
emit once. `finish` appends one resolved row per existing row, without
peephole elimination. Every branch/write/move/goto is thus one fetched
row in the unchanged executor. Leading-zero coefficient passes survive.

Logical tuple order is `(branches,writes,coded moves,gotos)`; physical
tuple order is `(reads,writes,unit moves,flat rows)`.

| Phase | Literal tags | Logical tuple | Physical tuple |
|---|---|---|---|
| Initialization + rewind | `init/init-y/init-zero/reset-back/reset-public` | `(3,1,6,2)` | `(18,3,42,12)` |
| Horner + rewind | `hscan/hy/hn/hdigit/reset-back/reset-public` | `(4,1,6,2)` | `(22,3,48,13)` |
| Offset + rewind | `offset/offset-digit/rewind` | `(2,1,2,1)` | `(10,3,24,6)` |
| Odd residue + rewind | `residue/res-digit/rewind` | `(2,0,2,1)` | `(10,0,18,5)` |
| Quotient | `emit/emit-y/emit-n/emit-digit` | `(3,1,4,1)` | `(16,3,36,9)` |
| Whole reverse | `global-bits/global-public` | `(1,0,4,1)` | `(8,0,18,6)` |
| Installation | `install/install-symbol` | `(1,1,2,1)` | `(6,3,18,5)` |

Let `R` be the positive even component count, `B=sum w_i`, `S=B+R`,
`K=L+2`, and `U=1+S+(K+1)R`. Every successful call visits every public
data bit in all seven phases. Initialization writes one numerator bit
per public bit, then K high bits. Its reset skips K high bits, then does
one `reset-back/reset-public` cycle per public bit. Each Horner pass
does the same; `hfinish` advances i until exactly L passes finish.
Offset and residue scan all `w_i+K` numerator bits, so retaining only
w_i forward and reverse iterations is a lower bound. The residue path
occurs exactly when the odd denominator part exceeds one. The `rewind`
branch jumps directly back, without a separate goto.

Quotient staging advances output, numerator, target and source: FOUR
moves per public bit. The script's accounting mutation deletes the
numerator move and changes `(16,3,36,9)` to `(15,3,33,8)`. It detects
this change; no numerical execution of the mutant is claimed. Correct
ordinary quotient cost is 55 raw actions, 64 including rows. The prior
illustrative 59 omitted that move; its slack 128U upper bound is unaffected.

Global reverse uses numerator markers, skips high bits and moves the
other three heads once per public bit. Installation reads every output
bit, writes the target and advances both heads. Delimiters and markers
add work. No whole-field-zero shortcut exists.

## Head returns, erasure and sum

Global reverse returns all four heads to their origins. Installation
leaves target and output at physical distance 3S, source and numerator
at origin. `execute_table` then calls `origin` on every port. At distance
D>=0, literal origin costs exactly D+1 reads and D+2 moves. The two long
returns therefore contribute at least `(6B,0,6B,0)`.

Private numerator and output have contiguous binary bodies 3U and 3S.
Logical symbols 4/5/6 remain three physical binary bits and cannot end
the physical erase. Starting at origin, `retire` of length D makes
exactly `(2D+3,D,2D+4)`: initial origin, erase and frontier read, final
origin. `Controller.primitive` calls it on both work ports after every
successful table return. Since U>=S>=B, the two erasures contribute at
least `(12B,6B,12B,0)`. Entry cleanup and historical larger bodies cannot
subtract from these current-body costs. Historical space and current
erase length remain separate quantities.

Adding the rows gives exactly

```text
B * ((76,18,156,38) + L*(22,3,48,13) + delta*(10,0,18,5)).
```

Raw action sum is `B*(250+73L+28delta)`; including rows it is
`B*(288+86L+33delta)`. This matches the proposed vector.

## All-zero success and omitted-cost signs

For arbitrary positive matching widths and positive even R, all-zero
inputs give zero in every Horner prefix, even for negative coefficients.
The positive widths establish zero input signs before delimiters; all
expanded high bits and carries close. The rounding offset is c=floor(b/2),
with 0<=c<b. Since b has at most L bits and K=L+2, c fits strictly in
the expanded signed numerator at every positive width. The offset endpoint
sign/carry check also closes after the high bits.

For b=2^d o, the residue and odd quotient produce floor(c/o), including
the trivial o=1 case. Dropping d low quotient bits gives
floor(floor(c/o)/2^d)=floor(c/b)=0. All remaining high output bits and
sign are zero, so the signed-range guards accept. For b=1, c=d=0.
Positive even R closes parity and frontier checks. There is no data-zero
optimization, so all counted loops still execute. This proves a nonempty
successful local domain universally, not by finite fixture extrapolation.
Whole-source zero composition additionally needs all other services'
zero-preserving contracts; it is not executed or established here.

Omitted costs are nonnegative: delimiters/start/global markers, K high
bits, d quotient drops, high-bit and terminal guards, halt, transitions,
shape/source preparation, table construction, contexts, entry retirement
and other wrappers. Early rejecting calls can omit later passes and are
outside the successful-call theorem.

This is a lower bound for the pinned literal implementation and metrics.
A simultaneous multitape step, a tariff unit, a logical bit and a flat row
are different units. No general implementation lower bound, full-program
runtime lower bound, physical tariff conversion, multiplication lower
bound, new exponent or global assumption discharge follows here.
