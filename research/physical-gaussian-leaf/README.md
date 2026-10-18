# Fused physical Gaussian leaf arithmetic

I implement exact Gaussian C/inverse-C coefficients, complete encoded axis
traversal and aligned signed ADD/subtraction with a fixed tape inventory.
I preserve borrowed inputs, check exact division and signed output width,
and erase owned work on success and named arithmetic rejection.

The older arithmetic in PR2287 stores intermediate sums and numerators at the
component width. I use a four-state carry and two sign-extension steps instead.
For example, at three bits `C(3+3i,3+3i)` fits, despite the intermediate sum
`6+6i`. I accept that exact endpoint without enlarging a coefficient word.
The implementation changes; the C identity and prior staged guards remain
credited source work.

I prove necessary/sufficient guards for each fused component and give the
complete physical time/space argument in [PROOF.md](PROOF.md). One complete
axis costs O(V); a direct f-axis leaf costs O(fV), including encoded setup,
movement, cleanup and returned-port copying. I retain the selected leaf
stopping predicate. I claim no faster arbitrary-width recursive child.

## Evidence and reproduction

From the repository root, with Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/physical-gaussian-leaf
```

I register eight bounded cold commands, with arithmetic/failure controls also
under `-O`. I authenticate the source archive and live inputs before importing
checks. [RESULT.json](RESULT.json) binds complete typed receipts; timings do
not determine receipt equality.

I passed all eight registered commands on Python 3.12.13/macOS arm64 by
23:36 UTC on October 16, 2026. I have not claimed a hosted CI pass.

| Check | Coverage |
|---|---|
| Fused C components | 37,640 cases: exhaustive four-input widths 2/3 and boundary probes at 17/65 |
| Signed ADD/subtract | 1,124 cases plus complete aligned Gaussian packets |
| Complete leaf | Spaced two-axis and three-axis packets, dirty spectators, multiple coefficient fields/outer rows and forward/inverse reuse |
| Exact grid | Credited sharp reserve at one through eight axes, impulse oracle and insufficient-reserve rejection |
| Ownership | Later-field arithmetic rejection, preserved borrows, erased partial output and valid cross-method retry |
| Failure controls | Eight source, carry, guard, direction, field-traversal and protected-return faults |

I use an independent integer formula for expected C outputs. I retain
`ceil(f/2)` as Alejandro Zarzuelo Urdiales's prior C-tensor reserve, with
Nick Petalas's prefix/capacity applications. I realize that bound in this
physical leaf; I do not claim it as a new denominator theorem. Normalized
Hadamard conversion keeps its separate f-bit reserve.

## Open next questions

1. Bind an actual selected child to the physical monomial and coefficient
   engines. Start with directed child 7 and retain ywz65's PR2534 interval,
   factorization and earlier fixture credit. A joined implementation needs
   explicit returned-port ownership and the appropriate leaf/nonleaf decision.
2. Complete the remaining coefficient operations and caller alignment.
   General dyadic scalar increments, normalization, copy/clear and private
   lifetimes still need their encoded physical paths. Start with one literal
   selected scalar and price its preparation and cleanup on the root grid.
   This package's ADD interface assumes aligned inputs.

I record the task, expansion decision and structured questions in
[TASK.json](TASK.json). Canonical coordination:
[Discussion2238](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-18984596).

## Attribution and limits

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in
mathematics, implementation, source analysis and prose, including analysis
subagents. Apache-2.0 with source-specific notices retained in frozen archives.

I retain Alejandro Zarzuelo Urdiales's PR45 Gaussian parity/tensor results,
James Chang's PR1869 finite ripple adder, AAAmirinu's PR2327 prefix audit,
ywz65's PR2534 selected-child fixture, and Nick Petalas's PR2772/3089
prefix/capacity work. PR2287 supplies the grid/operator convention;
PR3055/3087 and their credited predecessors supply the encoded tape framework.
I pin heads and source bytes in [SOURCES.json](SOURCES.json).

I have not proved a complete selected recursive caller, root-grid admission,
native/hosting identities or a new multiplication exponent. I leave the
selected frontier unchanged and claim no independent human or formal check
of this new program.
