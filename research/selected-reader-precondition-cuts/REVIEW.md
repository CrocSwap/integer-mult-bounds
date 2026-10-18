# Independent exact review of the precondition cuts

**Result:** the complete eight-by-704 scalar centre reader is identical at all
7,401 cuts before, between and after the 7,400 zero-frame prefix gates. Its
diagonal Gram entries remain

```
(150, 130, 146, 134, 122, 126, 142, 146).
```

All 1,260 permutations with cycle type `(4,4)` fail the necessary diagonal Gram
condition at every cut. This is 9,325,260 excluded cut/permutation pairs,
established by full reader equality and an exhaustive 1,260-permutation census.
There is no unresolved norm collision requiring an off-diagonal Gram argument.

## Source and independent computation

The scientific source is the selected `gauge44` provider in
`research/community-frontier1094-audit/selected-replay.tar.gz`, from canonical
base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. The archive SHA256 is
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.
The checker authenticates the compressed canonical word and emitted program
members separately. The predecessor is PR2491 at exact head
`c25a4ce22a887daf8cba8b3cfad72796752ab2ee`; its retained proof identifies the
post-prefix reader and the conditional native interpretation. Its contribution
is credited rather than reclassified as newly proved here.

`independent.py` imports neither the primary checker nor the predecessor
executable. It uses sparse integer rows with a common power-of-two denominator
per row, rather than Fraction covectors. It initializes **all 704 independent
input columns**, executes `A` forward, and independently executes
`precondition + compensation + A` forward. It selects the eight centre rows
`(92,57,81,224,11,240,9,256)` and compares all 5,632 entries with the retained
predecessor certificate. The complete invocation and post-prefix readers agree.

Starting with the invocation reader, it then removes prefix gates in
chronological order by right multiplication with their inverses. For an ADD
`t += q*s`, this changes column `s` by minus `q` times column `t`; for a scale
`t *= q`, it divides column `t` by `q`. Each of the resulting 7,400 full
readers equals the initial one. These exact comparisons cover every cut without
sampling or probabilistic fingerprints. The canonical/emitted gate sequences
are also compared exactly, including target-first ADD orientation.

## Why the finite outcome gives a simple native argument

Let `Y` be the 112-dimensional field-coordinate subspace with indices
`112,...,223`. Every prefix gate writes into `Y`: 7,344 ADDs and 56 nonzero
scales. The scalar reader `A` has zero in all 112 corresponding columns, and
has 227 nonzero columns in total. These two source facts are checked directly.

For any common payload space `H`, retain the predecessor's exact native
factorization

```
M = T_out (A tensor I_H) U_in,
```

where `U_in` is field-block-diagonal and unitary, and `T_out` is unitary. This
factorization relies on the retained exact frame transitions and the typed
reader segment; it is not deduced from phase-free tableau identities here.
Block-diagonality means that `U_in` preserves `Y tensor H`. Therefore
`M(Y tensor H)=0`, even if its blocks are different unitary payload maps.

Every native prefix gate `G` satisfies

```
range(G-I) is contained in Y tensor H,
M G = M + M(G-I) = M.
```

Consequently every remaining prefix suffix `C_k` satisfies `M C_k = M`.
This directly proves native-reader equality at the named cuts; it requires
neither unitarity of the prefix nor commutation of `U_in` with it. The actual
prefix gates are invertible, so the arbitrary-input quantifier at an earlier
cut does not acquire an attainability restriction.

For completeness, the narrower source commutation premise is compatible with
this proof: all 352 touched fields start at frame zero, receive ordinary entry
adapters, and are disjoint from all 240 residual-adapter fields. Under the exact
ordinary adapter convention `old_to_new(0)=I` and `T_0=I`, every touched block
of `U_in` is the identity, so it commutes with each actual prefix gate. This is
an exact identity statement, not an assertion that arbitrary Clifford operators
preserve constant payloads. In particular a **residual** adapter at frame zero
need not be identity. The source explicitly distinguishes it: the selected
local audit calls replacing a cold residual wrapper by the ordinary frame-zero
entry a defective identity replacement. The direct annihilated-subspace proof
above avoids depending on this additional commutation argument.

The source definition `canonical_frame(n,U)` returns `ident(n)` when `U` is
empty. A retained copy is in
`research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py`
(SHA256 `2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962`).
The ordinary/residual distinction is visible in
`research/complex-sw4-frame8/local/hpe_audit_local.py` and its
`cold_hpe_pre_wrapper_replaced_by_identity_entry_adapter` control. These
observations clarify the historical convention; the new executable does not
replay the full native compiler or its wrapper tests.

If a unitary input action `P` and a unitary output block-permutation `Q` obey
`M P = Q M`, then `M M* = Q M M* Q*`. Each output diagonal Gram block is the
listed scalar norm times `I_H`. Unitary payload maps on output edges therefore
force the scalar norms to agree along each output cycle. No listed value
occurs four times. This excludes cycle type `(4,4)`, including signed edges,
physical output permutations and frame-conjugated output permutations. It does
not exclude arbitrary nonunitary input actions or changed output normalization.

## Controls and their actual sensitivity

- The 112 source-data columns have exact Gram `56 I_8`. Omitting helper dirt
  changes the complete Gram and destroys this diagonal obstruction. The control
  detects the omission; equal diagonal entries alone do not claim an intertwiner.
- Reversing the actual prefix order or flipping all its ADD signs still yields
  the same reader. These are **accepted positive controls**, because the writes
  remain in the annihilated subspace. They must not be advertised as detectable
  corruption of this reader. They may violate other supplier obligations.
- A write into live column 224 changes the reader and is rejected by full
  equality. Thus the annihilated-column condition is substantive.
- A separate noncommuting two-field fixture checks the exact matrix
  `[[1,1/2],[-2,0]]`. Chronological right-inverse removal restores identity;
  reversed inverse order and a wrong inverse sign do not. This makes the
  independent recurrence sensitive to both mistakes even though this particular
  source reader cannot detect prefix-only sign/order changes.
- A general invertible nonunitary prefix need not preserve an obstruction:
  `A=diag(1,2,4,...,128)` has eight distinct row norms, but `C=A^-1` gives
  `A C=I`, which admits every paired output permutation with the same input
  permutation. The checker verifies this dyadic counterexample exactly.

Reproduction from the repository root:

```
python3 -I -B -O research/selected-reader-precondition-cuts/independent.py
```

The review run used CPython 3.14.6 and returned
`PASS_INDEPENDENT_PRECONDITION_CUTS` under `-O`, which disables assertions.
All acceptance checks use explicit exceptions. No output files are generated
by this command.

## Scope and remaining obligations

This is a finite, source-pinned complete coefficient calculation and a written
operator lemma for every payload space where the retained typed native
factorization applies. It is not a formal-kernel proof. Native frame correctness
and exact compiler realization remain inherited obligations; neither constant
payload tests nor this scalar computation discharge them.

The finite family comprises only the fixed eight centre totals and the 7,401
zero-frame scalar-prefix cuts. No later cut, changed total, output rescaling,
different provider, paid nonorthogonal interface, full restoration invoice,
new prefix precision bound, recursive-child cost or all-size supplier admission
is established. No selected record, charge or kappa changes follow.

Independent verification and this review: OpenAI Codex assisting Ross
Richardson. Historical reader and native factorization: ywz65 with substantial
OpenAI Codex assistance, PR2491. Apache-2.0; inherited source attribution and
licenses remain in the retained repository artifacts.
