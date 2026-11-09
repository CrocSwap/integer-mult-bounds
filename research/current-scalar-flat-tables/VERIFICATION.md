# Verification record

Prepared for **@CubeJerry**, with substantial OpenAI assistance. No new κ.

## What is proved and what is tested

`PROOF.md` gives the all-width, all-record-count finite-carry theorem, complete
field staging, exact source-token substitution and complete linear tape bill.
The finite checks below challenge its implementation; their bounded coverage
is not a substitute for the quantified proof or the inherited caller premises.

The three vendored dependencies are byte-identical to the published commits
in `DEPENDENCIES.json`. Every test checks their Git blob and SHA256 before
import. Both runtime input files are checked against `SOURCES.json` before
decoding. These pins have no authority over the truth of the mathematics.

## Exact replay coverage

The four suites have deterministic receipts in `RESULT.json`. Each replay
compares its entire JSON result with that committed receipt using an explicit
exception, including under Python optimization. No proof obligation or test
guard depends on an `assert` statement.

| Suite | Coverage | Result |
| --- | --- | --- |
| `arithmetic` | All 42 current operation/coefficient pairs, widths 1–4, every signed target and every signed ADD source | 10,870 cases: 2,887 accepts and 7,983 rejects |
| `arithmetic` | 168 complete wider fields and 168 wide zero controls, widths 5, 16, 65, 129 | Exact endpoint/representation equivalence; bounded current work and physical actions |
| `arithmetic` | Extra SCALE(1/3), SCALE(-7/6), ADD(1/5), full small signed domains | 400 cases; a generic rational primitive check, without successor caller admission |
| `binding` | Original complete 642,410-event caller | 366,842 scalar service instances, 42 tables, 58,544 table rows; exact source/owner receipts |
| `controller` | Actual source scalar events 1..9895 after INIT(778), with 799 borrowed fields of two 11-bit components | All endpoints match a separate Fraction interpreter; 41,088,794 physical cell actions |
| `controls` | 25 targeted failures and boundary cases | Every named failure detected; valid endpoint-only headroom cases accepted |

The arithmetic suite uses the unchanged published `execute_table` on metered
physical tapes. Fixture construction and the independent post-execution
Fraction oracle inspect numerical values and tape storage; the runtime table
does neither. The controller suite additionally uses the original
`Controller.run`/`Controller.primitive` and the original #5356 physical
continuation constructor. Its owner initialization is explicitly supplied at
the prefix entry; it does not exercise the complete caller or recursive row
providers. All extra descriptor/context ports remain protected.

The controls include late-component failure before any target write, negative
inexact division, odd-denominator inexact division, most-negative negation,
width smaller than the denominator's power of two, malformed shape/codeword,
physical operand alias, altered coefficient, wrong source site, malformed
wrapper grammar, unsupported operation, source/dependency byte corruption,
wrong final-carry sign, missing sign extension, omitted raw scratch retirement
and shrinking reuse of erased warm backing. The binding suite separately
tests chronological product wrappers that retain an issuing PAID token: it
follows the active scalar token rather than mistaking that provenance for a
second scalar origin.

## Independent mathematical review

A separate lead AI reviewer read proof Sections 1–5 and the table's core state
machine, independently derived the telescoping identity and final sign guard,
and reported an independent digit/Fraction exhaustive check of 14,260 cases,
with 3,037 accepts. Its domain was SCALE and ADD, widths 1–5, every signed
operand, and coefficients `{1/2,-1/2,3/8,-5/16,1/3,-2/3,6/5,-7/10,9,-9}`.
The reviewer found no mismatch in rejection equivalence or carry bounds and
confirmed the geometry/staging argument under distinct-tape and well-formed
input premises. This is a separate mathematical audit reported during the
research session, not another physical-executor run, an independent human
review or formal proof-kernel acceptance. The registered package's own
reproduction commands do not purport to replay that external review.

## Corrections found before freeze

The first development draft reversed the sign of the telescoping terminal
carry condition. Its first most-negative negative-half fixture exposed the
error; the proof and generator were corrected before the recorded exhaustive
runs. A retained wrong-sign mutation control now detects this exact defect.
One initial width-1 negative fixture was itself out of range and was replaced
by a valid signed value before the reported controls passed.

During source-composition review, an initial recursive search over all token
members was found too broad for `product-right`, which retains both issuing
PAID provenance and the active token. It was replaced by the exact original
wrapper grammar, and a nested chronological-product positive control was
added. All direct caller receipts remain unchanged.

## Reproduction and publication boundary

From a checkout with the two declared source inputs:

```sh
python3 -B scripts/research_package.py --package research/current-scalar-flat-tables
```

`VERIFY.json` registers eight commands: normal and optimized execution of the
four suites. All eight passed in the final registered replay, with unchanged
exact receipts. Each command has a 120-second limit and requires only Python 3.12
and its standard library. `TASK.json` records the exact canonical task card,
base, narrowed claim and remaining obligations. Publication must include the
committed-byte preflight; [the final execution log](evidence/registered-replay.log)
records the eight registered checks and their
`PASS_REGISTERED_RESEARCH_PACKAGE` marker.

The all-success caller substitution still assumes common grid, signed range,
aligned actual owners, all supplied heads at current origins, contiguous
binary dirty work prefixes and the original lifecycle contracts. Immediate reject
leaves public contents intact but can leave work occupied and heads advanced;
no physical rollback theorem is claimed. Native maps, row/recursive services,
their error returns, the complete machine constant and analytic recovery
remain separate. All five selected assumptions remain in force.
