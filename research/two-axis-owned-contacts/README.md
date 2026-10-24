# Coupled two-axis owned contacts

One complete five-choice contact solve returned the unchanged round-three
paid/helper profile. One actual contact changes without changing any child
count. There is no higher kappa and no exact optimality theorem. The selected
conditional kappa at the base is .00302015.

## Scope and evidence

This extends PR5144's binary common-kernel model to all five preimages of
subspaces of a two-dimensional quotient, jointly at every contact. The binary
forms are fixed to coordinates 1 and 2; no coordinate-pair census was run.
The monotone owned-wire floor in PR5140 does not apply to this model.

For each original chart U, a contact chooses U, its intersections with
ker(1), ker(2), ker(3), or ker(1) intersect ker(2). Duplicate choices are
removed. Scalar operands retain a common physical chart. Main endpoints,
other owned contacts and unselected native boundaries stay fixed. Both
boundaries of all 408 arbitrary independent helpers may vary.

Every persistent edge, including originally zero bridges, pays relative
Fourier rank dim(A)+dim(B)-2dim(A intersect B). All eight owned COPY charts
may move; the opposite center chart stays zero and each full center rank
power is paid. Each of 72 late native maps is released, preserving the twelve
actual prelude line pairs. PR5144's exact line-preserving minimum-rank
formula supplies these tables. Signed map synthesis is not supplied.

The source model has 19,207 nodes, 34,646 paid incidences and 408 helper residuals.
There are 9,652 variable contacts: 1,282 with two choices and 8,370 with all five.
The MILP has 44,414 binary one-hot labels, 15,265 pair tables, 384,525 variables
and 135,874 equality constraints. Continuous pair marginals are forced to
their joint integral choice by the binary contact labels. Additive row and
column terms become unary before pair marginals are allocated.

At comparison saving .00302177585, SciPy 1.18.1/HiGHS reported status 0 in 43.321
seconds under a 180-second cap. Its floating objective was -1.077e-13 and dual
bound zero. Those are numerical reports only. The returned choice is
node 11424, state 2. Exact reassessment gives paid histogram
`{1:2201,2:412,3:510,4:127,5:40,8:8}` and helper histogram
`{4:28,7:7,8:47,9:326}`, identical to the source as integers. That specific
assignment therefore has zero improvement at every rank price. This does
not prove optimality or exclude other assignments or contact models.

[DISCOVERY.json](DISCOVERY.json) retains the numerical receipt and assignment.
[TASK.json](TASK.json) records the source heads, boundary, full obligation
ledger and decision to stop this alphabet after one model. Inputs are pinned
in [SOURCES.json](SOURCES.json); frozen predecessor bytes are unchanged.

## Reproduce

Python 3.12 and its standard library suffice for registered verification:

```sh
python3 -B scripts/research_package.py --package research/two-axis-owned-contacts
python3 -I -O -B research/two-axis-owned-contacts/verify.py
```

The read-only checks authenticate imported sources, reconstruct the literal
source bill, check all quotient preimages for 4,429 distinct source spaces
against a separate literal-set enumeration, check main endpoints and every
changed center rank, and reassess the returned histograms exactly. Eight
controls reject invalid assignments, dropped centers/helpers, undercharged
changed centers and dependent forms. Model-table SHA256 is
a7d1547f754ec68ddc7306d68ad9064b45373a7b5f8a95f2eb058038e2ce18c9.

Optional discovery needs NumPy 2.5.4 and SciPy 1.18.1:

```sh
python3 -B research/two-axis-owned-contacts/discover.py --seconds 180 --output /tmp/two-axis-discovery.json
```

The verifier does not rerun or prove the numerical optimum. Native absolute
phases, both literal orientations, owned cleanup, uniform compilation,
precision/tape and outer admission are not checked for a changed construction.
Unknown costs are not zero. No selected cold replay or Lean was run.

## Open next questions

A changed paid scalar/contact or controller-demand contract might alter the
bill. Specify one actual physical edit and its complete replacement cost,
then require a favorable whole paid-minus-productive invoice before native
implementation. This test gives no reason for a larger axis census. Signed
native replay and supplier/outer funding remain required for a positive candidate.

## Credit

Cao Yifan/intqwq supplies the round-three word and joint native-map lineage;
Cinna Davis/1337isnot1337 supplies the general contact and PR5144 owned/shared
model; Dugongue supplies the transported-frame/rank grammar; Matarener
supplies prior owned-wire propagation arguments. Retain zxv, Jacob Alan
Sussman and all native/helper/compiler/source attribution. Prepared by
Cinna Davis/1337isnot1337 with substantial OpenAI Codex assistance; no
subagents. Apache-2.0. Author-checked, without independent human or proof-kernel acceptance.
