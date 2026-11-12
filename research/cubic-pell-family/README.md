# An infinite equal-weight family for cubic-reader repair

**Scoped proof and exact checks; no new κ.** Prepared by apoursh with
substantial OpenAI Codex and subagent assistance. Apache-2.0.

This answers **Open next question 2 of Nick Petalas's
[PR6653](https://github.com/CrocSwap/integer-mult-bounds/pull/6653)**.
Its certificates at arities 7 and 97 have weights `(-r,r/2,r/2)` on
integer directions `(0,d,e)`. We classify that pattern for every integer
`r>2`, even allowing arbitrary rational directions:

```text
D_r(A,B) = -r*A^3 + (r/2)*(A+d*B)^3 + (r/2)*(A+e*B)^3
iff
r^2 - 3*n^2 = 1,  n a positive integer,
{d,e} = {(r-1-n)/2, (r-1+n)/2}.
```

Here `D_r = sum_{i<r}(A+i*B)^3 - r*A^3`. All admissible directions
are integers. All positive Pell solutions arise from
`(r,n)=(1,0)` by `(r,n) -> (2r+3n,r+2n)`; the nondegenerate repairs start
at `(7,4)`. The proof includes elementary descent, not just a recurrence
that generates examples.

The even-index subsequence with half-index not divisible by three gives
infinitely many arities outside every earlier infinite class listed by
PR6653. Its first values are `7,97,18817,262087,50843527,708158977`.
The first two remain Petalas's existing examples. The new result is their
uniform continuation and the complete classification of this weight pattern.

After retaining all `r` children `y += a^3; a += b`, the repair is:

```text
a += (e-r)*b
y -= (r/2)*a^3
a -= n*b
y -= (r/2)*a^3
a -= d*b
y += r*a^3
```

It uses **three cube queries and three integer shears** and ends at
`(y,a,b)=(Y+r*A^3,A,B)` for arbitrary incoming `Y,A,B`. PR6212's cited
dyadic lower bound makes three queries optimal in its stated model at
these arities. This package does not re-prove that lower bound or claim
three-shear optimality. See [PROOF.md](PROOF.md) for all hypotheses and
exceptions, including the collapsed `r=2` boundary.

## Evidence and reproduction

CPython 3.12.14, macOS arm64, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/cubic-pell-family
python3.12 -I -W error -B research/cubic-pell-family/verify.py
python3.12 -I -W error -B research/cubic-pell-family/independent_check.py
python3.12 -B scripts/check_research_commit.py --package research/cubic-pell-family --check-modes --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/cubic-pell-family --ref HEAD --output /tmp/cubic-pell.tar
python3.12 -B scripts/export_research_package.py check /tmp/cubic-pell.tar
```

The registered hook runs both engines normally and with `-O`, isolated and
warning-strict. No predecessor executable is imported.

- `verify.py` checks all four cubic coefficients of the exact **symbolic**
  off-Pell residual in the two indeterminates `(r,n)`, corroborates 96
  recurrence terms and 32 terms outside the earlier classes, screens arities
  3 through 10,000 by integer square roots, and rejects 12 algebra/domain
  controls. It authenticates four predecessor files and rejects altered
  bytes for each using in-memory mutations.
- `independent_check.py` uses its own sparse-polynomial interpreter. It
  executes every original child and the literal repair for seven arities
  through 18,817, retaining a formal arbitrary dirty destination. It checks
  40 rational dirty-input examples and all 1,063,536 direction pairs in the
  declared domains: `0<=d<e<=r` at integer arities 3–160 on the integer grid,
  and arities 3–32 on the one-eighth grid. Five hits across these two grids
  agree with Pell membership; the two grids overlap. It also checks 32
  recurrence terms and 528 descent steps, rejects nine program/algebra
  mutants and five domain errors. Child defects are accumulated directly,
  without the primary engine's power-sum formulas.

Finite checks corroborate implementation and scope. The all-arity claim is
proved in Sections 1–3 of PROOF.md. Independent here means a separately
implemented Codex-agent checker, not independent human or formal-kernel review.

## Selection, overlap and scope

Canonical main was pulled at entry: `e54523517d0f03e58352e647c403a5af3e525a57`.
The full original `joint-query-controller` card is retained in TASK.json,
with its scope explicitly **changed** to this source-specific algebraic side
question. The contextual picker reports revision 8's historical PR5599
assessment differs from selected PR7000, κ `363005817/100000000000`.
The selected source-binding orientation passed after materializing its 221
paths; its scientific cold replay was not run.

PR6653 is merged, at retained head
`3ea9965e13457fdafc70b784305d026ebfa8faa2`. The live all-state PR searches
`6653`, `Pell`, `Pell cubic` and `cubic repair` returned 3, 3, 2 and 21
results respectively. No later answer to this question was found. PR6212's
Pell equation concerns **two-query** feasibility; PR5209 concerns
integer-transvection length. Full HEAD filename inventory and relevant cubic
package notes were also checked. These searches do not prove novelty.

The dedicated author-filtered `find_source_overlap.py --reference 6653
--pr-author petalas --created-since 2026-10-27 --include-closed` intake was
attempted, but `gh` is absent and its remote corpora were null. Public
start-here, active Discussions and newest-sorted handoffs were inspected;
the retrieved newest handoff was dated November 11, so November 12 comment
coverage was incomplete. An advance PR claim could not be posted through
the connector (403); no public reservation is claimed. The source's specific
open question and exact dependency bytes remain explicit.

## Limits and expansion decision

This classifies only the fixed weights `(-r,r/2,r/2)` and directions
`(0,d,e)`. Non-Pell arities can still admit other three-query repairs.
It does not classify arbitrary weights, nonmonic forms or general frames.

The source transformations and query coefficients are fixed independently
of input data. The lower-bound model excludes output feedback, nonlinear
source updates, intermediate observations and child-interior access.
Three weighted cube accumulations and three shears are operation counts;
their coefficients grow. No physical backend, coefficient preparation,
routing, precision/storage price, complete caller bill or supplier admission
is supplied. The selected bound and its five assumptions are unchanged.

**Decision: narrow to this uniform local module.** Stop before downstream
optimization unless a source-compatible physical caller and complete cost
comparison make it useful. Unknown costs are not zero.

## Open next questions

1. For arities outside this family and the earlier constructions, such as
   `r=15`, can unequal weights or general dyadic frames attain three queries?
   Start with PR6653's node condition and odd-prime weight valuations; a
   bounded search failure is not a four-query obstruction.
2. Does the three-shear schedule improve a fully priced caller at `r=7`
   or `97`? Use one pinned backend and the complete comparison in PR6250's
   PROOF.md. Query, coefficient, preparation/routing and precision/storage
   costs must be included before extending the construction.

## Credit and source boundaries

Nick Petalas's PR6653 supplies the question and finite seed examples; its
PR6200 predecessor supplies the fixed cubic reader. apoursh's PR6212 supplies
the dyadic interface/lower bound and PR6215 another direction family.
AAAmirinu's PR6246 and CubeJerry's PR6250 supply the earlier power-of-two
and power-of-two-plus-one constructions. Their attribution is retained in
four live, hash-pinned input notes declared in SOURCES.json and VERIFY.json.
No predecessor files are changed. Pell equations, descent and power-sum
identities are classical; no literature-priority claim is made.
