# Retimed P104 dual: completed errors and exact private recovery

The literal retimed word from [PR2725](https://github.com/CrocSwap/integer-mult-bounds/pull/2725)
admits the conditional error bound

```
E <= 5534*u*B / (1 - (6047/4)*u),       (6047/4)*u < 1.
```

E is the largest error at any completed-event boundary in any live register,
in the **maximum of individual register Hilbert norms**. B bounds every initial
public register norm. For every integer b >= 0, `u <= 2^(-b-13)` gives
`E < B*2^-b`. This is not an addresswise maximum norm.

Approximate private cancellation need not produce a literal zero. Under the
grid and completed-error premises below, nearest-grid recovery makes all eight
private fields exactly zero before erasure. Their smaller cut-specific constants
give a tighter recovery threshold than using the global maximum there.

This is an author-checked local precision/cleanup lemma. It supplies neither a
rounded recursive child nor a priced recovery implementation. The existing
[fixed-profile consumer-budget obstruction](../p104-consumer-budget-audit/README.md)
still applies. No supplier, new kappa or selected-frontier change is claimed.

## Exact object and evidence

Base: main `4b82082f901945f8d0314f143576c7ad31e021fc`, priority 5.
PR2725 is pinned at `71d24b655c2fdddc063b9aaf285e8425ce197499`.
Its unchanged word has 5,268 events, 358 arbitrary public inputs, 3,104 ADDs,
1,940 transports, 208 exact signs and eight private lifetimes. Every private
field has zero ideal logical row before erasure. Only two of 104 data rows have
the inherited identity correction; this is not a complete identity supplier.

| Exact quantity | Coefficient | First attaining cut / role |
|---|---:|---|
| Initial-input amplification P | 127/2 | 3433 / X12 |
| Independent unit defects A | 4769/4 | 5069 / X7 |
| Feedback weights K | 6047/4 | 5069 / X7 |
| Ideal-operand weights J | 5534 | 5116 / X54 |
| Native-only unit defects N | 843/2 | 5069 / X7 |

Cut t means the boundary after the first t literal events. Signs, allocation
and erasure are exact; ADD and transport output errors give 5,044 defect sites.
The private pre-erasure cuts are 1937, 1950, 1961, 1974, 1987, 2000, 2011 and
2026. Their maxima are `J_C=317/2`, `K_C=22`; each cut is in [RESULT.json](RESULT.json).

Signed sparse forward propagation and reverse covector substitution agree on
every final input/error coefficient, attaining row and private cut. A separate
chronological reverse pass reconstructs the operand weights and all five scores
at **each of the 5,252 non-lifetime event cuts**. Complete score streams have
the same SHA256. Initial states cover cut 0; inserting zero or deleting a row
cannot create a maximum. Unchanged rows retain preceding scores.

Literal collinear executions attain all five independent-input/defect bounds.
These fixtures do not claim to attain the state-relative feedback bound. Each
private cut has a nonzero-residual fixture that recovers within the strict
radius. Another fixture confirms exported private errors survive erasure.

## Completed-operation contract and proof

In the predecessor's actual unitary logical charts, ideal transports are
identities and ADDs are literal rational row operations. Transforming a physical
defect into its instantaneous logical chart preserves its Hilbert norm. Signs
act exactly by -1. Private allocation inserts zero; erasure deletes only its
own row. Native correctness/unitarity, including phases, remains inherited;
this package does not regenerate native recipes.

Assume a completed transport's output defect is at most `u*||input||`, and
`dst += c*src` has defect at most `u*(||dst||+abs(c)*||src||)`, using actual
preinstruction operands. **All internal child and wrapper errors must fit
this allowance.** Inputs start without error; public helpers may be arbitrary.
Signs and known-zero allocation remain exact.

Let p_r be the L1 norm of an ideal input-coefficient row before an instruction.
At site j define weights a_j,w_j by

| Operation | Ideal operand weight a_j | Feedback weight w_j |
|---|---|---|
| Transport of r | p_r | 1 |
| ADD dst += c*src | p_dst + abs(c)*p_src | 1+abs(c) |

Let C[t,r,j] be the signed response of defect j at cut t in register r,
including subsequent resets. The certificate computes

```
J = max_(t,r) sum_j abs(C[t,r,j])*a_j = 5534,
K = max_(t,r) sum_j abs(C[t,r,j])*w_j = 6047/4.
```

The actual defect is at most `u*(B*a_j+w_j*E)`, hence
`E <= u*(B*J+K*E)`. Rearranging proves the bound. Correlated, adversarial and
state-dependent defects are permitted. Signs remain until the last triangle
inequality. `J+K=28183/4 < 2^13` proves the uniform 13-bit implication.
Since `J>2^12`, 12 bits fail this sufficient formula; this is **not a numerical
precision lower bound**.

## Conditional exact recovery

Let lambda >= 1 and f,h >= 0 be integers. Assume initial physical real and
imaginary components lie in `2^-f Z`, with `B <= 2^h`. Retain PR2813's
[tensor-grid premise](../p104-retimed-internal-grid/README.md): ideal physical
outputs lie on the grid of spacing delta=`2^-F`, where

```
F = f + ceil(9*lambda/2) + 2 >= 7.
```

Before each private erase, round every physical component to the nearest
multiple of delta, then erase the recovered zero. Ideal private vectors are
zero; Hilbert error strictly below delta/2 bounds every real/imaginary component
and guarantees unique zero recovery. Approximate states need not already lie
on that grid. At the private cuts,

```
E_C <= u*(B*J_C + K_C*E)
    <= u*B*(317/2 + 22*u*5534/(1-u*6047/4)).
```

**Private-only recovery:** `u <= 2^(-F-h-9)` suffices. It is at most `2^-16`.
The parenthesized coefficient increases with u on this interval; at `2^-16`
it is `82156733/512194 < 256`. Thus `E_C < delta/2`. Recovering a private zero
just before deleting it changes no retained row. Earlier exported errors stay
in the model, so the proof applies successively to all eight erasures.

**All-public-output recovery:** `u <= 2^(-F-h-14)` suffices for exact final grid
recovery and private recovery. Set `b=F+h+1` in the 13-bit implication:
`E < B*2^-b <= delta/2`, then apply the inherited ideal output lattice.

Strictness matters: half a grid step is ambiguous; just outside it, another
grid point can be nearer. Controls cover both failures, negative values and
several spacings. The recovery rule is a mathematical interface. Its scanning,
rounding, representation, storage and movement costs remain unpriced. The
conditional tensor implication is a written proof, not executed all-size
code or a formal-kernel certificate.

## Reproduce

Python 3.12 and standard library; direct replay needs neither Git nor network:

```sh
python3.12 -I -B research/p104-retimed-error-recovery/verify.py
python3.12 -I -B research/p104-retimed-error-recovery/check_all_cuts.py
python3.12 -I -B research/p104-retimed-error-recovery/test_verify.py
python3.12 scripts/research_package.py --package research/p104-retimed-error-recovery
```

Default replay writes nothing. `verify.py --write-result NEW_PATH` creates an
exclusive new receipt. Input SHA256 and Git blob pins are checked before WORD
parsing. No predecessor code is imported. The complete ideal endpoint map and
rank/event census match the pinned predecessor receipt. Source, receipt,
cleanup, chart, coefficient and recovery-radius mutants reject. A relocated
optimized replay tests input closure and unchanged file bytes.
[VALIDATION.md](VALIDATION.md) records actual runs and limitations.

## Credit and scope delta

Vasek / flyingviper supplies PR2725's word; Nick Petalas / PR2813 its internal
grid binding. Adam Gall / PR2096 supplies the Hilbert-defect method; ywz65's
[operand-weighted feedback](../p104-operand-weighted-feedback/README.md) and
[different private-macro dual](../p104-dual-precision/README.md) supply the
credited feedback framework. Their numerical constants are not transferred.
Retain commdata2338 / PR2662, ywz65 / PR2586, Ross Richardson's sharp-grid
finding, Rohan Arun / PR1972, Chafik Boukhalfa / PR1991, Adam Gall / PR1940,
Josie Elliston / PR1071, Ali Romman and the inherited E8/Clifford/compiler lineage.
Frozen predecessors are unchanged. Exact pins are in [SOURCES.json](SOURCES.json).

The delta is this changed word's signed error response and the completed-defect
to exact-private-zero implication. It does not replace the internal-grid
certificate, implement an approximate child or correct the other 102 rows.
The drawn physical correction/cost card changed to this precision side result;
[TASK.json](TASK.json) explains the scope and stopped expansion decision.
Prepared for Arham Tahir with substantial OpenAI Codex assistance in research,
proof, code and checks. Separate algorithms were checked by the same assistant;
no independent human review is claimed. New material is Apache-2.0.

## Open next questions

1. Bind an actual rounded rank-1 through rank-8 child, including wrappers and
   cancellation inputs, to an explicit u in the completed-output contract.
   A per-component or absolute allowance alone does not establish the relative
   Hilbert premise. This implementation is required to apply the lemma.
2. Give one physical state/precision and recovery-scan invoice for a viable
   owner window. Representation and movement remain unknown, and the present
   fixed-profile consumer screen fails. Precision constants alone do not
   justify expanding that family.
