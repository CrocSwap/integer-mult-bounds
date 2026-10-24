# The p16 query-only shears cannot be absorbed by their neighbours

**Negative result, no new κ.** [#4440](../query-thinned-controllers/README.md)
replaced selected full native calls by copied rank-one query shears, and
[#4470](../joint-helper-lattice/README.md)'s p16 complex controller keeps 15 of
them. The retained BIT controller has the same 15. Each costs one rank-one job
per port: 1,680 complex and 1,665 BIT paid jobs, about 0.7% of each paid moment.
Because the surplus is thin, the companion package
`research/productive-lever-reprice` (separate PR) finds that free
shears on both sides would give a raw ceiling near 0.0099. #4440 lists "a
changed local query/native alphabet" as its next improvement question. This
package closes three natural ways to remove the shears, in the replay model of
`query-thinned-controllers/controller.py`.

## The thin block

At thin stage `2j` the word bridges pair `j−1` with pair `j`, applies the
forward shear `Y_{j−1} += Q^{-1} X_{j−1}`, and unbridges. Its net effect is

    Y_{j−1} += Q^{-1}(X_{j−1} + X_j),   Y_j += Q^{-1}(X_{j−1} + X_j),

one rank-one query per port that feeds two pairs. Both neighbouring full calls,
at stages `2j−1` and `2j+1`, are backward (`X += −Q Y`) on pairs `j−1` and `j`.

## 1. Fusion with a neighbouring full call needs two queries

For all 15 thin stages on each side, the verifier composes the bridged block
with the previous and with the next full call, exactly as the replay does.

- Complex: every composite has nonzero `Q^1` and `Q^{-1}` coefficient matrices.
- BIT (`Q^{-1} = Q`): every composite has a Q-coefficient matrix of rank 2 over
  GF(2)(D), shown by a nonzero 2×2 minor.

A full call `D_s S(Q^{±1})` has Laurent support `{Q^0, Q^{±1}}` and
Q-coefficient rank 1 (checked as a control). So a fused call would need two
independent query results per port, and re-framing helper boundaries cannot
absorb the shear.

## 2. Lazy central frames give nothing

Exactly,

    S_x(−Q) S_y(Q^{-1}) = signed_swap · diag(Q^{-1}, Q) · S_x(Q),

so a thin query can be traded for a change of central frame on fields. Model a
field as `Q^a · logical`, with `a` in Z/2. For BIT `Q^2 = I`; for complex `Q^2`
is a Pauli phase and is treated as free, which only favours the trade. The costs
are as follows: flipping a field costs 1; an ADD across different parities costs
1 (it becomes a Q-shear); a query between different parities is free (it becomes
a Pauli shear), and between equal parities it costs 1; a full call needs equal
parities. All fields start and end at parity 0.

**Floor.** Each thin query on pair `k` lies in a window that starts at the full
call on the same pair `k` and contains only ADD and IDLE events. At the full call
the two fields agree, ADD and IDLE never change a parity, so either the query is
paid or a flip inside the window is paid. The 15 windows are disjoint (checked on
both controllers), so the cost is at least 15. The present controller attains
15, so the optimum is 15 on both sides. An inserted SWAP breaks the window
property, as a control. A CP-SAT run over the whole word in the same model found
the same optimum; it was discovery only and is not used.

## 3. A two-query native word gains nothing in gather-type schemes

The query on port `p` is a rank-one recursive query along that port's line
`q_p`. All lines are distinct: 112 nonzero 9-bit lines in complex
(`DATA-PHASES.json`) and 111 E8-root lines up to sign in BIT (`WORD.json.gz`). In
schemes built from linear maps, rank-one queries and free scalars and routes,
one query serves one line, so a second independent query costs one rank-one job
per port. Riding on a query the native word already makes returns `Q(f+u)`, and
linearity cannot split `Qf` from `Qu` without another query. The directions
also differ, since the native result goes to `X` and the shear's to `Y`.
Changing the shape does not help either: merging a stage's 112 rank-one jobs
into 14 rank-eight jobs saves less than one unit of moment at κ = 0.00302015
(`RESULT.json`). A native word implementing the fused block therefore costs at
least the old word plus 112 rank-one jobs per stage, which is the present bill.

**Scope.** Parts 1 and 2 are exact in the stated models. Part 3 is a bound for
gather-type schemes only. It is not a proof for every circuit, for example one
that recodes addresses so that different lines meet. The remaining route is a
redesigned local family whose ports share query lines, which is the same opening
recorded for the H branch in #4580.

## Open next questions

- Is there a redesigned local family whose ports share query lines `q`, so that
  one query serves several ports? That is the only opening left by part 3, and
  the same one the H branch leaves (#4580). No candidate is known.
- Part 3 is scoped to gather-type schemes; a general lower bound for the fused
  block (any circuit, including address recoding) is open.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/thin-query-shear-floor
```

Standard library only; under one second. Prepared by Matarener (Mark) with
Claude Code assistance. Apache-2.0.
