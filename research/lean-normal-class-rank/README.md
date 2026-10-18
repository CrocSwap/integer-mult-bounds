# Lean proof of the normal-class rank bound

This package kernel-checks **Lemma K of PR #2338**, the rectangular fixed-space
transfer used after it, and the resulting completed count and power-price bounds.
The mathematics and its P112 application originate in DreamingOfClouds' source
proof. The addition here is an explicit Lean proof with independently computed
finite fixtures and false-hypothesis controls. It does not certify the rest of
that PR or admit a P112 supplier.

Source: [PR #2338](https://github.com/CrocSwap/integer-mult-bounds/pull/2338),
head `82700676e1d42acf98dc1921cb6ef82551620008`, README §3.4, Lemma K
and its use in Theorem Bk. The exact README and attribution are retained in
`sources/`; `PREDECESSOR.json` records their Git blobs and SHA-256 digests.
[PR #2342](https://github.com/CrocSwap/integer-mult-bounds/pull/2342) checks a
three-call floor and explicitly leaves the broader all-batch proof unaudited.
This package addresses one universal implication in that broader proof.

## Exact statement

Let `F` be any field, `I` a finite index set of size `t`, and `Γ` any linearly
ordered type of class labels. For `K : Matrix I I F` and `α, β : I → Γ`, assume:

1. `α i ≠ β i` for every term `i`.
2. `K i j ≠ 0 → β i = α j` for every pair of terms.

`normal_class_rank` proves `t ≤ 2 rank(I − K)`.
`normal_class_half_kernel` proves the equivalent
`2 dim ker(I − K) ≤ t`, including `t = 0`.

The proof partitions terms into `α < β` and `β < α`. Each orientation exposes
an invertible principal submatrix of `I − K`: strict increase around the support
graph rules out a nonzero fixed vector, by choosing a maximal label in its
support. The two principal rank bounds and rank-nullity give the result.
No assumption about characteristic, integrality of coefficients or a finite
number of class labels is needed.

For rectangular `A : F^t → F^N` and `C : F^N → F^t`, the maps `C` and `A`
give inverse linear equivalences between the fixed spaces of `AC` and `CA`.
Thus the half-kernel bound transfers to `I_N − AC`, when `CA` satisfies the
same two class hypotheses. Our `C` is the row factor called `Cᵀ` in PR #2338.
This transfer concerns the fixed space, not equality of the zero eigenspaces
of arbitrary rectangular products.

If **all remaining `n` terms** factor the residual, so `AC + DE = I_N` with
`D : F^n → F^N` and `E : F^N → F^n`, `completed_count` proves
`2N ≤ 2n + t`. For prices `lo` and `hi ≥ 0`, `charged_count` then proves

```text
N hi + t (lo − hi/2) ≤ t lo + n hi.
```

With `N = 8k`, `lo = 7`, `hi = 8`, this gives `64k + 3t ≤ 7t + 8n`.
With prices `7^q` and `8^q`, the affine bound holds for every real `q`.
For `q ≤ 1`, Lean additionally proves

```text
(3/8) 8^q ≤ 7^q − 8^q/2
8k 8^q + (3/8)t 8^q ≤ t 7^q + n 8^q.
```

The intended concave physical pricing domain is `0 < q ≤ 1`. Applying this to
a P112 computation still requires proving that its rank-seven terms supply
these distinct classes and compatibility entries, that the coefficient
factorization is complete, and that every other term is charged at least the
stated high price. The geometric classification, frame witnesses, SAT/DRAT
rigidity check and physical supplier admission are outside this package.

## What was checked

A fresh local build used Lean `4.33.0-rc1`, commit
`62eed1db4d67327ec8120be05f1a1b0847d74561`, and Mathlib
`55b7917b472489c7c56a0fa6393af05cfd536599`. `KERNEL.json` records 26 actual
axiom probes: 18 main definitions/lemmas and eight counterexample lemmas.
Only `propext`, `Classical.choice` and `Quot.sound` occur. Three deliberately
false proof attempts fail after successful imports and valid theorem setup.
The proof files contain no `sorry`, added axiom or `native_decide`.

The controls show why the statement cannot be weakened:

| Changed premise/conclusion | Counterexample |
| --- | --- |
| Permit equal endpoint classes | `t=1`, `K=[1]`, `α=β=0`; residual rank zero |
| Replace compatibility by zero diagonal | `t=3`, `K=I−J`, where `J` is all ones; residual rank one |
| Replace half-kernel by one-third | Compatible two-cycle; residual rank and kernel dimension both one |

`finite.py` imports no predecessor checker. Fraction-based Gaussian elimination
and a separate binary pivot algorithm check **39,157 labelled matrices** over
both Q and F₂: all compatible binary-entry matrices for `t=0,…,4`, with
three class labels and distinct endpoints. The per-size counts are
`1, 6, 66, 1218, 37866`. Both orientation minors are checked too.
Nine rectangular fixture cases (including the repeated `N=t=2` case) exercise
ambient dimensions below, equal to and above the term count, after coordinate
shears. A complete two-dimensional factorization attains the abstract count
bound; this is not a claimed physical P112 realization.

Nine Python control groups exercise source hashes, rebound-hash proof escapes,
complete inventories, axiom coverage, strict JSON, receipt corruption,
historical kernel binding, output preservation and explicit kernel mode.
`VALIDATION.json` records the executed environments and command outcomes.
Hosted workflow results are separate from these local checks.

## Replay

The registered standard-library replay needs Python 3.12 and takes seconds:

```sh
python3.12 -B scripts/research_package.py --package research/lean-normal-class-rank
```

It checks source inventory, historical receipt consistency and independently
recomputes the finite fixtures. Its success marker explicitly says
`SOURCES_AND_FINITE_ONLY`; **it does not execute Lean**.

To execute a fresh kernel build with the pinned toolchain installed:

```sh
python3.12 -I -O -B research/lean-normal-class-rank/verify.py \
  --lake /path/to/lean-4.33.0-rc1-linux/bin/lake \
  --work-dir /tmp/normal-class-rank-new-build \
  --fetch-cache --out /tmp/normal-class-rank-new-result.json
```

Both output paths must be new. `--fetch-cache` downloads the pinned libraries;
instead, `--packages /path/to/pinned/.lake/packages` uses an existing library
cache. Dependency Git heads and tracked source cleanliness are checked. The
local proof files are always copied into a new directory and rebuilt; library
object files are reused through the usual Mathlib cache trust boundary. Build,
axiom and rejection logs stay in the chosen work directory. The scoped GitHub
workflow downloads the checksum-pinned official toolchain and invokes this same
kernel mode. A historical receipt alone is not evidence that this command ran
in a new environment.

## Selection and scope

One fresh draw (`39160e84f0f7e0d9acb16904f92cb37c`) selected the
independent-verification track. The first card led to inputs already audited in
PRs #2359 and #2360; this uses the second suggestion, `formal-interface-lemma`,
without rerolling. It records a scope change from the selected-review interface
to the pending all-batch rank implication. The required research baseline passed.
Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
No selected certificate, supplier or κ is changed.

Canonical coordination: [Discussion #2380](https://github.com/CrocSwap/integer-mult-bounds/discussions/2380).
See `TASK.json` for selection, scope and final refresh details.

## Open next questions

Can the exact P112 normal-class and frame premises be formally connected to
these matrix hypotheses? Start with the source PR's `c3` frame witnesses and
finite label table, and prove that every nonzero `CA` entry connects equal
normal classes. The present theorem assumes that relation. Formalizing that
binding would reduce a different gap from independently checking the source
SAT/DRAT rigidity certificate or completing physical supplier admission.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance in proof,
implementation, verification and writing. No subagents or independent human
review were used. See `NOTICE.md` for predecessor credit and harness reuse.
