# Two reusable clean checkpoints

With **50 ordered factors and six scratch arrays**, two initially clean
arrays reduce the optimal signed-leaf bill from **1,728 to 1,248** compared
with one clean array. Source and scratch are restored exactly. The class is
ordered binary product-shear trees whose connectors remain reserved during
all descendant calls. **Research construction; no new κ.**

For `n=2^s` unit-price factors, `s` scratch arrays and `c` initially clean
arrays, the written proof gives the exact class minimum

```text
4^(s-c) * 3^c.
```

Each additional clean array therefore saves exactly 25% at full capacity.
The 50-factor example saves 480 calls (27.78%). It changes the initial-space
contract: four arrays may be dirty, but two must genuinely start at zero.
No borrowed information is erased.

## Reproduce

Python 3.10+; standard library; no network or solver:

```sh
python3 -I -O -B research/two-clean-checkpoints/verify.py
```

Expected:

```text
PASS_TWO_CLEAN_CHECKPOINTS: 1619 trees; 192 rounded cases; n50/s6: 1728 -> 1248; no new kappa
```

The verifier recomputes and compares `EXPECTED.json`; it never updates it
unless explicitly invoked with `--write`. It checks:

- Every decorated binary tree through six factors, using an independent
  preorder enumeration and path resource counts; 723 exhaustive weighted
  optimum comparisons and 32,039 resource admissions.
- Exact noncommutative identities, nonlinear restoration and literal
  inverses for all 1,619 trees, plus the larger frozen witnesses.
- 137 comparisons against the unchanged one-clean/all-dirty PR788 optimizer.
- 192 executions of the actual pinned PR628 rounded leaves, compared with
  dense rational represented-factor solves. Both signs and shift directions,
  dirty inputs, exact zero-source identities, inverse restoration, 3,760
  forward leaf calls and 34,112 forward phase reads are checked.
- Instruction, resource and dirty-as-clean controls. A dirty array mislabeled
  clean can be restored while corrupting the target; the verifier rejects it.
- Eleven unchanged predecessor files against their recorded SHA-256 pins.

`rounded_check.py --out PATH` exports all rounded-case invoices and output
hashes; their canonical digest is retained in `EXPECTED.json`. The dense
reference is the predecessor's Gaussian-elimination path, separate from its
rounded leaf execution. The synthetic factors isolate the recursive interface;
no root-factor certificate or preparation algorithm is claimed.

## Cost and scope

The supplied two-clean witness executes 243 dirty nodes and 259 clean nodes;
the one-clean witness executes 575 and one. At common complete leaf price `t`
and internal dispatch prices `g_D,g_C`, its saving before external costs is
`480t + 332g_D - 258g_C`. Initialization/admission, parameter preparation,
planning, routing, source access and magnitude/precision capacity remain
charged in [PROOF.md](PROOF.md). Leaf-count optimality is not a runtime benchmark.

`planner.py` emits a streaming signed instruction word. Callers must provide
distinct physical arrays, immutable parameters, exactly zero clean inputs and
deterministic zero-preserving leaves whose negative instructions subtract the
identical increment. Clean admission is a caller obligation. Linear leaves
realize the ordered product; nonlinear rounded increments can depend on dirt.

[PROOF.md](PROOF.md) gives the restoration induction, exact class recurrence,
full-capacity theorem and conditional error bound. [SOURCES.json](SOURCES.json)
pins the base and dependencies; [NOTICE.md](NOTICE.md) retains attribution.
[CLAIM.md](CLAIM.md) records scope selection and overlap checks;
[VALIDATION.md](VALIDATION.md) records executed checks and limits.

This extends PR714's clean root and PR788's one reusable clean array by
allowing a second clean connector while the first stays reserved. PR730,
PR758 and PR784 optimize or bound different all-dirty echo classes; we make
no global optimum or literature-priority claim. The selected #626/#543
construction and `upstream/` are unchanged. Clean-space supply, supplier
integration, physical hosting, all-size compilation, fixed-tape routing and
analytic transfer remain unresolved; this is not a multiplication theorem.
