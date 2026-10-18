# Added phase children cannot pay for one idle-group consolidation

**Scoped negative result; no new kappa or supplier admission.** Retaining the
original local and hosted calls, one replica/port group's idle-axis repacking
cannot pay even one additional positive-rank repair child under the declared
fixed-mass invoice. This tests a constructive repair route left outside the
fixed-schedule transfer obstructions, rather than rerunning their census.

For `0 <= a <= 1/400`, raw recursive child cost is `r^(1-a)`. With at most
twenty original residual slots and new residual ranks at most 51, even ideal
fractional rank-51 packing saves **less than `153/160` raw units**. One actual
additional child costs at least one. The resulting raw moment therefore
increases by **more than `7/160`**, before extra overhead. [PROOF.md](PROOF.md)
gives the all-parameter argument, endpoint handling and normalization.

The essential hypothesis is that repairs are paid **in addition to the fixed
original residual rank mass**. The source coverage formula can instead deduct
new local rank from idle mass; that alternative invoice is outside this result.
Changing original children, stock, normalization, interactions or rank cap, or
sharing one repair across groups, also requires a new comparison. Exact positive
relaxed-invoice controls show why those distinctions matter.

A concrete PR3184 component on PR3148 owner replica zero / port zero moves
axis 16 from child 10 to child 12. It changes the exact eight-stream operator
by rank two over `Q(i)` at character 16; a `2x2` minor has determinant `-2`.
One inserted single-stream phase child changes it by rank at most one at any
retained caller-level cut. Two signed rank-one phase children restore the
original factors, including global phase, for every character; they simply
repay the transfer. The inverse uses `C_v^-1=C_v X_v`, with translation movement
granted free by the optimistic screen. This is an arbitrary-input operator statement, not a
zero-helper experiment. Omitted repairs and a wrong inverse fail.

## Sources and coverage

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) pins nineteen live inputs, plus catalogue and
selected-record provenance. The verifier authenticates all 2,717,280 decoded
T740 fill rows and reconstructs owner-replica-zero inventories at all 112
ports. Every source recipe has twenty idle slots and full ranks in
`{0,8,16,32,48}`. The inherited strict halving cap is 51.

The retained exact eight-stream interpreter and rational moment enclosures are
reused unchanged. An independent mathematical-specialist implementation checked
the operator witness, and a separate cost reviewer rederived the continuous
bound. The latter's independent integer-power method is included in
[allowance.py](allowance.py), covering the endpoint `a=1/400`, integer ranks
0..51 and four excluded relaxed invoices. It does not replace the written
proof on the whole interval. There is no formal-kernel or independent human
review, new full native/controller replay, supplier admission or outer theorem.

## Reproduce

From the repository root:

```sh
python3.12 scripts/research_package.py --package research/idle-additive-repair-budget
```

Expected: `PASS_IDLE_ADDITIVE_REPAIR_BUDGET` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.
The registered command verifies the committed [RESULT.json](RESULT.json).
For a fresh deterministic receipt use `verify.py --output /absolute/new.json`;
the output must be new and outside this package. It does not modify sources.

## Open next questions

The bounded repair test is complete. [TASK.json](TASK.json) records two precise
reopening routes: absorb a correction into original children while proving
what existing cost disappears, or construct a shared correction across groups
and account for its actual joint operator, stock, routing and restoration.
Neither route is claimed to work or reserved by this package.

## Credit and license

The source construction, proposals and physical-stream objections remain due
to Rohan Arun (#3184/#3190), Gonzalo-Mier (#1252/#3196/#3199), Gareth Davidson
(#1387), Nick Petalas (#3187), Tekalign (#3204), Jeremy Diviney (#3148),
dcharb78, Marius-Paul Dumitrean, Jeremy Kothe and all retained word, native,
geometry and compiler predecessors. The selected record is unchanged;
archival of a predecessor is not scientific admission.

This package adds the explicit additive-repair allowance, its source-bound
application, exact insertion witness and scope-sensitive invoice controls.
Prepared by Ross Richardson with substantial OpenAI Codex assistance, including
independent mathematical-specialist checks. New material is Apache-2.0.
Frozen predecessors and their notices remain unchanged.
