# Completed-prefix codes and outer twiddle bounds

This package gives an enabling construction and scoped negative results
for the synthetic Fourier interface. The changed opposite DIF schedule
leaves completed physical bits outside every later twiddle. Codes on
those bits can therefore pass through the remaining exact transform.
The package also states the cost and precision conditions for a fixed
code bank and a physical address wrapper. It does not supply the native
layer or the recursive child contract that must use this interface.

The complete multiplication exponent is unchanged. There is no new
supplier exponent, selected record, or measured runtime improvement.

## Results and review boundary

| Result | Exact scope | Proof and existing review |
|---|---|---|
| Completed physical bits | The remaining forward map is identity on the completed slots. The changed opposite has exact endpoint `F_plus B_inverse L_inverse`, with the retained layer slots, cost order, and unencoded error bound. | [Proof](frozen/lanes/temporal-reuse/COMPLETED-PREFIX-CODES.md), [complete prefix and layout review](frozen/lanes/interface-proof/completed-prefix-review/REVIEW.md), [separate opposite review](frozen/lanes/source-domain/OPPOSITE-PREFIX-REVIEW.md) |
| Fixed code bank | A fixed finite alphabet of invertible dyadic Gaussian matrices on a fixed number of completed bits can be fused. Its final inverse costs `O(V ell)` and needs `O(ell)` extra precision and integer bits. Matrices need not commute. | [Proof](frozen/lanes/temporal-reuse/COMPLETED-PREFIX-CODES.md), [review](frozen/lanes/interface-proof/completed-prefix-review/REVIEW.md) |
| Completed row axis | Completing one whole axis gives enough row digits for the stated finite radix and depth. This has `O(V ell)` cost and a stated new precision allowance. It does not give an arbitrary growing-bank decoder. | [Proof](frozen/lanes/temporal-reuse/COMPLETED-PREFIX-CODES.md), [review](frozen/lanes/interface-proof/completed-prefix-review/REVIEW.md) |
| Physical past layout | Six block interchanges align the selected offsets and restore arbitrary spectator data. The reserve placement is conditional on a native word that fixes all unselected fields. The compact finite invoice remains open. | [Proof](frozen/lanes/temporal-reuse/PAST-CATALYST-LAYOUT.md), [review](frozen/lanes/interface-proof/completed-prefix-review/REVIEW.md) |
| Current-twiddle criterion | For scalar codes that fix the unprocessed bits and polynomial payload, a monomial replacement twiddle requires one branch address per output row. This excludes the stated odd-line and paired code at a nonterminal current bit. It permits dense mixing within that branch's row block. | [Proof](frozen/lanes/temporal-reuse/COMPLETED-PREFIX-CODES.md), [review](frozen/lanes/interface-proof/completed-prefix-review/REVIEW.md) |
| Separate transport cost | The stated conjugated twiddle needs `f` binary ADD depths per round, hence `Omega(Vp)` over the transform, in the fixed complete-stream pass grammar. | [Proof](frozen/lanes/temporal-reuse/TWIDDLE-PASS-COST.md), [review](frozen/lanes/coherent-port/TWIDDLE-PASS-PROOF-REVIEW.md) |
| Accumulated stable-port code | The exact two-round decoder has ten entries per scalar row and cannot be one native C tensor between monomial maps. The stated joint-parity proof gives an `Omega(Vp)` terminal decoder bound in the complete-stream pass grammar. | [Proof](frozen/lanes/temporal-reuse/ACCUMULATED-TWIDDLE-CODE.md), [review](frozen/lanes/coherent-port/TWIDDLE-PASS-PROOF-REVIEW.md) |

The pass bounds do not cover recursive native children, calls on smaller
volumes, a different complete endpoint, or a fused arithmetic algorithm.
The current-twiddle criterion does not cover polynomial-valued codes or
new arithmetic twiddles. A test on one factor does not rule out
cancellation in a complete supplier.

The [fixed-past closure note](frozen/lanes/temporal-reuse/FIXED-PAST-OUTER-CLOSURE.md)
is a conditional supplement. It assumes a fully priced native endpoint
`h_P tensor H0_A` on the same physical completed space P, with all required
arbitrary fields restored and all recursive, precision, and tape costs
included. Under those assumptions, `h^2=iI` and `h^8=I` permit one final
`O(Vd)` decode with an `O(d)` precision allowance. Its scalar normalization
check passes. No distinct final independent review of that closure note
was present in the frozen campaign. The separate review for this
publication now accepts its conditional written argument. That review
also checks 114 tensor-power cases and 30 decoded error propagators.
It does not prove the assumed supplier, recursive invoice, or guarded
approximation contract. No such supplier is proved here.

The terminal-slot decoder candidate is excluded. The
[outer-interface note](frozen/lanes/temporal-reuse/OUTER-ENCODING-INTERFACE.md)
and two Schur notes are retained as background dependencies of the reviewed
files. They are not additional primary results of this package. Their
producer programs and full native invoices are not replayed here.

## Historical source and current selected record

The proof and replay inputs use
[`3ae9a6f3ac74ded022ab3b4872a7357a621af6fb`](https://github.com/CrocSwap/integer-mult-bounds/tree/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb).
Its [selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/certificates/selected-result.json)
and [assembly](https://github.com/CrocSwap/integer-mult-bounds/blob/3ae9a6f3ac74ded022ab3b4872a7357a621af6fb/research/community-frontier1094-audit/ASSEMBLY.json)
belong to the historical
[PR #1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094)
selection. The exact margin checks are for that historical assembly.
The actual 112-port input is a frozen campaign source derived from the
older supplier snapshot `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

The publication base is
[`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`](https://github.com/CrocSwap/integer-mult-bounds/tree/b58ad9ef4d4e861b0eaa5dba41742bdc072dca51).
At that base, the [selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/b58ad9ef4d4e861b0eaa5dba41742bdc072dca51/certificates/selected-result.json)
is the conditional joint-helper construction of
[PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470),
with `kappa=60403/20000000=0.00302015`. Its inherited native/all-column,
owned-erasure, whole-job, compiler, precision/tape, analytic, prime, and
recovery hypotheses remain. Uniform words are not materialized.
The [current review](https://github.com/CrocSwap/integer-mult-bounds/blob/b58ad9ef4d4e861b0eaa5dba41742bdc072dca51/docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md)
is context only. This package establishes no transfer to that selected
construction or to a newer native graph.

The frozen files retain their historical wording, including references
to the then-current selection and publication hold. The scope in this
README controls this new package. No historical file was edited.

## Reproduce

Use Python 3.10 or later with its standard library. Use one CPU and allow
at least 3 GiB of memory. The driver runs each checker in sequence. It
needs no Git checkout, network, NumPy, or other package. Copy the complete
directory to any path and use a new output directory outside it.

```text
python3 -I -B replay.py --out /tmp/completed-prefix-normal
python3 -I -O -B replay.py --out /tmp/completed-prefix-optimized
```

The last line from each command must be:

```text
PASS_COMPLETED_PREFIX_OUTER_PACKAGE
```

The driver verifies 47 frozen inputs and all eight checker copies. It
compares every fresh result with its frozen receipt. The only permitted
receipt change is `checker_sha256`, where the frozen checker records its
own source hash. That field must equal the actual new checker hash.
All other fields must match exactly. The driver also checks that every
non-main mathematical function has the same Python syntax tree.
[PORTABILITY.patch](PORTABILITY.patch) gives every I/O and CLI edit.

The checks include 174,760 independent exact forward/opposite entries,
9,455 separate coefficient identities, 27,988 separate opposite matrix
entries, 455 layouts, and the complete two-round decoder. Negative
controls use the wrong common length for long and short axes, omit the
input bit reversal, use the old opposite twiddle, and remove the finite
example's twiddles. The scalar permutation countercontrol passes the
current-twiddle test. These checks protect exact conventions. The
all-size conclusions rely on the proofs and their stated assumptions.

Normal replay and an optimized cold export both passed. The cold export
ran from an unrelated directory with external tool lookup disabled.
[VALIDATION.json](VALIDATION.json) records the results. Source links and
license files were checked byte for byte through GitHub;
[SOURCE-LINK-CHECK.json](SOURCE-LINK-CHECK.json) records all 18 objects.
The full multiplication program, a new native supplier, recursive
encoded children, and the PR #4470 program were not run or admitted.
Existing review means separate AI-agent review, not independent human
review. See [NOTICE.md](NOTICE.md) for attribution and license.

## Open next questions

1. Construct a native layer whose complete physical endpoint acts only
   on the fixed completed space and the current active bits. Restore
   every required arbitrary input field.
2. Prove that each child has type `E_V F E_U^-1` inside the parent. Prove
   equal physical operand codes at every parent scalar access.
3. Give the finite movement, preparation, normalization, storage,
   precision, and recursive invoice for that layer and its final decode.
4. Before using the reviewed conditional fixed-past closure, prove its
   native endpoint and approximation assumptions on the guarded inputs.
5. Check a complete proposed construction against the current selected
   framework before any supplier or complete exponent comparison.
