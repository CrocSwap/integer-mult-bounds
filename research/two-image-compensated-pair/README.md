# A four-call compensated two-image pair

**Constructive exact local interface; no new kappa or Gaussian admission.**

For the original and phase-repaired two-image prefixes, this package gives
`(x,y) -> (F_f x,F_f^-1 y)` on two arbitrary independent inputs at every positive
width. It uses four paid rank-one C calls, eleven scalar ADDs and no initially
zero logical array. The second input becomes an explicit inverse-volume partner;
it is not returned unchanged or credited as an independent Gaussian job.
The complete pair has Euclidean norm three, inverse norm three and condition
number nine, uniformly in tensor width.

The source's finite free inverse for `L_f=A_f+2B_f` is used in dirty-source
shears. The standard block identity

`E12(L) E21(-L^-1) E12(L) W(-I) = diag(L,L^-1)`

is sandwiched between two copies of `diag(C_f,C_f^-1)`. Each inverse C uses
one paid forward C and a free shift. [PROOF.md](PROOF.md) supplies the all-width
operator proof, literal execution order, source restoration and complete bill.

| Variant | Paid C calls | Scalar ADDs | Primitive address applications |
|---|---:|---:|---:|
| Original U,V | 4 | 11 | 42 |
| Phase-repaired P,Q | 4 | 11 | 138 |

The inverse runs the same program with two extra bank swaps. The rational
denominator 15 is explicit: fixed rational mixing is permitted in the abstract
engine, but a native dyadic/rounded implementation needs its own precision,
storage and routing invoice. No recursion, binary caller or outer admission
is established, and no paid-call saving is claimed.

This is a constructive changed contract beyond
[PR4991's dirty-return obstruction](https://github.com/CrocSwap/integer-mult-bounds/pull/4991).
The two output determinants cancel. F has unequal singular values and is not
a scalar-unitary Gaussian job. A useful Gaussian-compatible consumer and its
complete price remain open. No source or selected frontier is changed.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -I -B research/two-image-compensated-pair/verify.py
python3.12 -I -O -B research/two-image-compensated-pair/verify.py
python3.12 -B scripts/research_package.py --package research/two-image-compensated-pair
```

Expected:

```text
PASS_TWO_IMAGE_COMPENSATED_PAIR variants=2 paid_calls=4 arbitrary_input_columns=288 no_new_kappa
```

Default replay is read-only and compares [PROGRAM.json](PROGRAM.json) and
[RESULT.json](RESULT.json). `--write-result NEW_PATH` exclusively creates a
fresh summary and sibling program; it does not overwrite either file.

A separate dense oracle constructs `C_f L_f C_f` directly and computes its
inverse by Gaussian elimination. It does not use the generated shear schedule
or polynomial inverse. For each variant, all sixteen independent input columns
at width one are checked over Q(i), and all 128 at width two over F17 with i=4.
Both inverse orders are checked. Width three adds a dirty-input round trip.
Modular equality is finite corroboration, not rational width-two or universal
proof; the written identities establish all widths.

Controls change an inverse coefficient, omit an actual source-restoring U,
try to label the transformed partner as returned dirt and omit a paid call
from the invoice. No hook-rank suite, Lean, native or selected cold replay is run.

## Assignment, sources and overlap

Base: `bee95ce88f9f19802f0613f92838895cd0e14a1f`, priority revision 7. OS seed:
`9765cbd650b275bfb905be59e697b044`. The `complex-new-helper-inventory` card was
retrieved for the concrete constructive continuation of PR4991. [TASK.json](TASK.json)
records the changed scope and stop rule. [SOURCES.json](SOURCES.json) pins three
main inputs; no predecessor checker is imported or executed.

[OVERLAP.json](OVERLAP.json) records search coverage and limits. Canonical claim:
[Discussion1166 comment19138901](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138901).
No publication, package pass or AI review is independent scientific acceptance.

## Open next questions

- Can an actual Gaussian-compatible consumer use both specified outputs without
  repaying their benefit? Start with its complete independent input, diagonal
  output and frame ledger. No such consumer or favorable moment is supplied.
- Can the denominator-15 word be realized with a complete precision, storage and
  routing bill? Start with one finite exact-grid or rounded invocation and its
  actual return contract. Ideal inverses do not imply the inverse of a rounded
  child realization.

## Credit

lee-phys supplies PR4688's two-image prefix, free inverse and rank engine;
Yiyang (@Lyy-iiis) supplies PR4710's phase repair; Dugongue supplies PR4743's
full-input triangular ports and independent-output qualification. Jacob Alan
Sussman's PR4628 supplies the engine and small-unit framework, retaining
eumemic/PR288 and Swapnil Jain P1/P2 credit. The elementary block/shear identity
is standard and not claimed as new. Original notices and AI disclosures remain.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in research,
proof explanation, implementation, verification and writing. Apache-2.0.
No proof-assistant or independent human review is claimed.
