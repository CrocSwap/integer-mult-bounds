# Lean semantics of nonlinear dirty commutators

**Scoped formalization / independent verification; no new κ.**
Lean 4.21.0 proves the nonlinear restoration induction from
[PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628) and
[PR663](https://github.com/CrocSwap/integer-mult-bounds/pull/663) for an explicit
typed recursive evaluator. Every finite binary tree restores its arbitrary
borrowed arrays, has an increment independent of its initial target, and has
an exact reverse-word inverse. Leaves may be arbitrary deterministic nonlinear
maps on integer arrays of any finite width.

With additive leaves, a separate theorem proves the ordered factor product,
independent of initial dirt, without assuming that factors commute. This adds
a kernel-checked proof of the existing argument, not a new commutator,
call-count improvement, precision estimate, or multiplication exponent.

The key identity is

```text
delta_node(x,z,t) = delta_right(z + delta_left(x,t), t)
                   - delta_right(z,t)
run_positive(x,y,s) = (y + delta(x,s), s)
run_negative(x,y,s) = (y - delta(x,s), s).
```

The evaluator passes the actual intermediate deeper-scratch states between
children. Their restoration is proved by induction. The source-restoring,
target-independent leaf interface and fixed external parameters are premises
of the model. [MODEL.md](MODEL.md) states the exact trust boundary; the source
proof is [NonlinearEcho.lean](NonlinearEcho.lean).

## Reproduce

Use Python 3.12+ and the official
[Lean 4.21.0 toolchain](https://github.com/leanprover/lean4/releases/tag/v4.21.0),
with core and bundled Std only:

```sh
python3 -B -I research/lean-nonlinear-commutator/verify.py --lean /path/to/lean-4.21.0/bin/lean
```

Expected final line:

```text
PASS_NONLINEAR_ECHO: 12 formal statements; 34 kernel trace equalities; 1170 source cases; 2364 tree cases; 13 controls; kappa unchanged
```

The generic proof alone, from this directory:

```sh
lean -DwarningAsError=true NonlinearEcho.lean
```

The verifier compiles fresh temporary objects, authenticates every consumed
source before AST extraction, and compares the complete deterministic receipt
with [EXPECTED.json](EXPECTED.json). It needs neither Git nor network access
and writes nothing inside the package by default. `--write /new/receipt.json`
reconstructs a receipt; `--emit-cases /new/TraceCases.lean` saves all source
trace equalities for inspection. Both refuse to overwrite existing outputs.
The expanded 83-factor proofs use an explicit 64 MiB Lean thread stack.

## Completed evidence

- **12 audited formal statements**, using only standard `propext` and
  `Quot.sound`. The universal semantics, exact inverse in both orders,
  additive-map product, and a nonlinear dirt-dependence counterexample are
  kernel-checked. No proof placeholder, custom axiom, or native evaluation
  oracle is used.
- **130 actual dispatcher traces / 206,830 instructions** cover factor
  counts 1..64 and 83, both signs. **34 Lean equalities** bind the complete
  literal source traces for counts 1..16 and 83 to the address compiler.
  These equalities have no axiom dependencies. The 83-factor word has 7,744
  instructions in each direction.
- **1,170 source execution cases** use widths 1,2,3 and three leaf families:
  offset floor maps, bounded square maps, and noncommuting integer shears.
  Functional evaluation and the independent increment recurrence agree with
  the mutable dispatcher. Both signs and full inverses execute **3,722,940**
  complete leaf calls. All source and borrowed data return exactly.
- **2,364 additional execution cases** cover all **197 ordered binary trees
  through seven leaves**, including unbalanced trees, with a separate literal
  instruction interpreter. Ideal products retain factor order.
- **13 controls:** six compiler mutations, three disallowed-axiom inputs,
  and four source alias/depth rejections. Concrete nonlinear witnesses also
  distinguish scratch restoration from dirt-independent output, and full
  inversion from merely negating signs in forward order.

[VALIDATION.md](VALIDATION.md) records the executed portability and failure
checks. The bounded domain and stopping rule are in [CLAIM.json](CLAIM.json).
The fresh OS draw was **83**, coincidentally the same as the preceding pass;
this pass addresses execution semantics, whereas PR887 addresses resources.

## Scope, pins, and credit

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. The dispatcher is pinned at
PR628 `0768f97d06c623b8211e651543c66135796b62bf`; the independent written audit
is PR663 `e0e546fd01b396478c68b6b6c5a16d87515983ba`. Six verbatim files and
their notices are retained with SHA256/Git-blob pins in
[SOURCES.json](SOURCES.json). The selected #799 κ remains
`1661634653669567/10^18`.

The universal theorem concerns the typed recursive evaluator. Connection to
the raw-address compiler and Python is the stated bounded evidence. All-size
compiler correctness, Python semantics, rounded leaf accuracy/restoration,
phase preparation, physical bit/tape execution, and the multiplication theorem
remain separate obligations. The known phase-alias gap in unmodified PR628
is not repaired here: external phase/coefficient data must be fixed and
nonaliased. Multiway echoes, connector reuse, and clean checkpoints have
different scopes.

Credit **Chafik Boukhalfa (@chafreaky)** for PR628, **0xkilgore** for PR663's
written induction and symbolic audit, **androolloyd** for related PR673, and
**Ali Romman** for the PR621 kernel lineage. Original notices preserve further
credit. Prepared for **Gareth Davidson (@bitplane), with substantial OpenAI
Codex assistance**. One AI agent performed the work; no independent human
review is claimed. Apache-2.0; see [NOTICE.md](NOTICE.md).
