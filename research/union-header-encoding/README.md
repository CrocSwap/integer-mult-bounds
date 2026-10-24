# A sufficient serialized header for the PR4100 union schedule

**Scoped interface result. No new kappa.** The per-microbox sparse-union
schedule has a concrete header format of

`H = 2gh + g + 2 ceil(log2(g+1)) + 2` bits,

where `h = ceil(log2 L)`. At #4100's actual core side
`L = 2^ceil(400 log2 p)` and `beta = 1 - 3/10^30`, this is `o(p)`.
For `g <= p^beta`, `H <= 810 p^beta log2 p`. For routine group rounding
with `g <= 2p^beta`, double that bound. If `p >= 2^(40 * 10^30)`, then
respectively `H < p/32` or `H < p/16`. This is a sufficient **header-width**
cutoff, not a practical size estimate or a cutoff for the complete algorithm.
The proof and exact integer cutoff check never materialize that `p`.

This answers the field-capacity part of [#4327's open question 2](../pr4100-union-head-travel/README.md)
and [its handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19092954),
also left open by #4376. It supplies a reference codec and a finite adaptation
of #4327's tape simulator. It does **not** claim that #4100 already contains
this serialized implementation or discharge the complete producer/global-context
tape obligations. Status: [Discussion #4576](https://github.com/CrocSwap/integer-mult-bounds/discussions/4576).

## Exact caller and source bindings

Base: canonical main `f626db5c3a3d781d8f7695038776c621651f75e1`, priority
revision 7. #4100's retained source head is
`337d04939571a637aeab54a0f58f54fde811663a`; #4327's artifact head is
`a020d6c25cb9201d19bebdf0ab5675b780a3caa2`.
[SOURCES.json](SOURCES.json) authenticates the main bytes of six inputs:
#4100 GAUSSIAN.md, PROOF.md, composition-controls.json, UNION-SCHEDULE.md,
and #4327 README/verifier. The ledger's exact `group_headers` slack equals
`1-beta = 3/10^30`. Historical decimals in UNION-SCHEDULE section 5b are not
substituted for the current ledger. No frozen source, selected record or
predecessor receipt changes. Selected conditional kappa remains `23/10000`.

## Boundary contract and encoding

An invocation has one fixed microbox/coarse context, `g >= 1`, side `L >= 2`,
and sorted boundary sets `E_i` within `[0,L)`. A record contains local
coordinates `x` and a payload. The payload changes; its address and flags
do not. The round index, carving description, coarse page, tape end markers
and transpose tree are shared context, not hidden per-record fields.

The fixed-width, big-endian fields in [header.py](header.py) are:

| Field | Width | Meaning |
|---|---:|---|
| Record marker | 2 | `01`; other codes are rejected by the record parser |
| Local coordinates | `gh` | All `x_0,...,x_(g-1)` |
| Flags | `g` | Membership `x_i in E_i` |
| Boundary ordinals | `gh` | Rank in `E_i` when flagged; canonical zero otherwise |
| Flag count | `b` | `|F(x)|`; `b=ceil(log2(g+1))` |
| Current tag | `b` | Active axis, or sentinel `g` before tagging |

Storing **all** ordinals is a deliberate constant-factor refinement of the
source's active-ordinal field. The source computes membership/rank from its
carving description; retaining those ranks avoids another rank-generation
step whenever the active axis changes. No complexity bound for arbitrary
set membership is inferred. The finite codec's explicit `E_i` lists are
semantic test oracles, not proposed all-size tables.

Coordinates give injectivity inside a context. Each coordinate/ordinal is
below `L <= 2^h`; each count/sentinel is at most `g < 2^b`. In zero-based
round `r`, the `(r+1)`st set flag gives axis `f`. Keep the record precisely
when its count exceeds `r+1`. Prefix boundaries use `x[:f]`; the transpose
uses ordinal `f`. Thus these fields supply the local metadata queries in
UNION-SCHEDULE steps 1, 3, 4 and 7. Tag updates leave the other fields
unchanged, and copies/radix/transpose inverses preserve the header.

A fixed number of scratch tapes can scan, copy and compare these bits and
maintain the short counters sequentially. Even conservative
`O(H polylog p)` reader work is `o(p)` for fixed `1-beta>0`, so it fits
the asymptotic per-visit allowance. This is an existence/accounting argument
for the readers, not a bit-step TM implementation. The explicit cutoff above
certifies width only, not operation constants or the carving/rank producer.

## Width proof and exact cutoff

Put `t=log2 p >= 1`, `h=ceil(400t)` and `b=ceil(log2(g+1))`.
For each integer `g>=1`, `b<=g`, since `g+1<=2^g`. Consequently

```
H = 2gh + g + 2b + 2
  <= 2gh + 5g
  <= 800gt + 7g
  <= 807gt
  < 810gt.
```

For `g<=p^beta`, divide by `p`: `H/p <= 810t 2^(-delta t)`,
where `delta=1-beta>0`. This tends to zero. Allowing `g<=2p^beta`
doubles the bound, covering floor/ceiling and neighboring power-of-two rounding.

At `t0=40*10^30`, `delta*t0=120`. Exact integer comparisons give
`810*t0 < 2^115` and `1620*t0 < 2^116`, so the two ratios are below
`1/32` and `1/16`. For all `t>=t0`, the bound decreases: the derivative of
`t*2^(-delta*t)` has the sign of `1-delta*t*ln(2)`, which is negative
because `ln(2)>1/2` and `delta*t>=120`. This proves the entire tail.
A `p`-bit payload plus this header therefore has width `p(1+o(1))`,
and is below `17p/16` beyond the cutoff even with upward rounding.
Adding this header to a `Cp+o(p)` payload likewise adds only `o(p)` bits.

The beta/core assertions are source-bound. This elementary all-size proof
is written mathematics, not a formal-kernel result. Finite tests use
`(p**400-1).bit_length()` for the exact ceiling; floating-point values do
not accept any bound.

## Evidence and meaning of the simulator adaptation

[RESULT.json](RESULT.json) records:

- 2,040 finite width checks and the symbolic huge-cutoff inequalities;
- 746 round trips, including all boundary subsets and coordinates in the
  declared small domains, plus fields of up to 1,200 coordinate bits;
- 688 active headers checking tags, prefixes, ordinals and keep decisions;
- 14 rejected inconsistent headers/layouts;
- six executions of #4327's unchanged `run`, with 287 records, 705 visits,
  355 lines, 12,635 record writes and 28,976 header decodes.

Each record tape cell in the adaptation carries a serialized header.
Coordinate access decodes and validates it. The source's exact Kronecker
reference, visit identity and movement bounds pass with `RW=128+H`.
Only the in-memory adapter and width parameter change; frozen source bytes
do not. The source still queries its finite flag/rank tables from decoded
coordinates. Separate active-header tests check the equivalent queries through
stored fields. This is **reused schedule evidence**, not an independently
implemented schedule or a complete bit-level cost measurement. Finite sizes
calibrate the codec; they are not executions at the enormous cutoff.

Rejections cover truncation/extra bits, framing/nonbinary data, coordinates,
flags, ordinals, counts, tags/rounds, boundary lists and inactive ordinals.
Two different prefixes with equal active ordinals show why ordinal-only keys
fail. A two-context fixture has identical local headers but distinct coarse
page actions: context boundaries cannot be deleted. Also, `p=2^(2k)`,
`g=2^k`, `log2 L=2^k` gives `H>2p` despite `beta=1/2<1`, showing why the
polynomial-core hypothesis matters. The parser is not a corruption-detecting
code: a change to another internally consistent record need not be detected.

## Reproduce and limits

Python 3.12, standard library only; about one second per direct run locally.

```sh
python -B scripts/research_package.py --package research/union-header-encoding --check-only
python -B scripts/research_package.py --package research/union-header-encoding
python -I -O -B research/union-header-encoding/verify.py
```

Registered commands compare every result field with the committed receipt
without rewriting it. `--write-result` is an explicit authoring option,
absent from VERIFY.json. All live inputs are SHA256-authenticated before
predecessor import and declared for CI invalidation. The direct verifier
supports a Git-free export of the package and those inputs.

Not covered: actual carving/rank production, coarse-context gather/delivery,
global counters/stacks, bit-level parsing travel, boundary arithmetic,
precision, stock, native semantics, outer recovery or the full #4100 theorem.
#4327's schedule proof remains a dependency. Mixing contexts needs a separately
priced identification mechanism; arbitrary spectator lengths are not encoded
for free. The optional full-history publication check is unavailable in this
shallow checkout; pins use its present base and no foreign heads. The baseline
orientation command stopped on sparse-omitted selected packages. No selected
cold replay or hosted CI success is claimed here.

## Open next questions

1. **Emit fields on actual tapes.** Bind a concrete carving description to
   sequential flag/ordinal generation and charge counters/rewinds. This
   connects capacity to production; the actual emitter is not supplied here.
   Stop if generation or context costs exceed the allowance.
2. **Bind two coarse contexts at the grouped caller.** Trace the gather to
   separate union invocations, or price an added context key. Start with two
   coarse pages and equal local coordinates. The global gather and page
   delivery remain outside this package.

[TASK.json](TASK.json) records the refined `uniform-transfer-audit` assignment.
Initial overlap covered 355 open PR bodies and 3,470 Discussion records with
complete reported pagination. Local notes were sparse and are not novelty
evidence. #4376's padding and #4327's tape travel are complementary results.

## Credit

Cinna Davis (#4100); Jeremy Kothe's PR1731 schedule lineage; Vlado
Vojdanovski's PR1673 layout; Ryanson Jonathan (#4327); unpaidmoon (#4376);
rtyu193-rgb's operator/volume review and LeverRank's retained checker.
The imported simulator retains its original attribution. Prepared for
Mihir Srivastava / mihir-s-05 with substantial OpenAI Codex assistance.
No subagents, independent human review or formal-kernel acceptance.
New work is Apache-2.0; predecessor notices are unchanged.
