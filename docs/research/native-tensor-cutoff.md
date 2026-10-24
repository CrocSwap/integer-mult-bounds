# Certify identities with actual affine and phase relations

Use [native-tensor-cutoff](../../research/native-tensor-cutoff/README.md) when
every payload operator is a binary affine permutation with a quadratic
Gaussian phase. This is the fixed monomial recipe grammar in [PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250).
The checker respects actual inverse, finite-order, commutation and phase
relations. It checks all dirty inputs and all returned roles.

The proof gives a finite criterion for a fixed n-axis program: equality at
widths **2n+4 through 2n+7** is equivalent to equality at every positive
width. The tool checks canonical native coefficients and constructs a short
basis witness on failure. It does not materialize those four tensor spaces.
The number of stored terms can still grow exponentially.

```sh
python3 -I -B research/native-tensor-cutoff/native_identity.py \
  /path/to/problem.json --output /tmp/native-certificate.json
python3 -I -B research/native-tensor-cutoff/check_certificate.py \
  /path/to/problem.json /tmp/native-certificate.json
```

Copy the input format from the package's source-conjugation example. Bind
each generator to exact source recipe bytes. Use a second complete program
as the reference. Keep a borrowed role's identity output when it must return
its dirt. Save both input and certificate files with the source pins.

The actual nine-axis example is a relation-dependent identity. Its deliberate
constant-phase error passes even widths but fails the separate checker's
width-25 witness. Another nine-axis example vanishes at every width below 9.
Small-matrix tests alone therefore do not establish the all-width claim.

Keep three boundaries explicit:

- Scalars stay outside tensor powers. A recipe phase c contributes f*c at
  width f. A scalar multiplying the complete register operation contributes
  that same scalar, not its f-th power.
- The four-width criterion requires a single fixed program and fixed scalar
  coefficients. Arbitrary width-dependent choices need the proof's separate
  phase-residue statement.
- This grammar excludes Hadamard gates, rectangular operators, nonlinear
  leaves and external aliases. Physical costs, precision, tape movement and
  supplier admission need their own proofs.

For independent operator symbols, use the
[universal dirty-circuit guide](universal-dirty-circuit-guide.md). Its smaller
grammar supports compact polynomial-size certificates. Named inverses alone
have their own [inverse certificate package](../../research/inverse-dirty-certificates/README.md).
Choose the grammar that the actual source satisfies. A failed independent
operator check does not refute an identity which uses native relations.

Prepared by Ali Romman with substantial OpenAI Codex assistance. The package
retains the source and classical mathematical attribution. This is an
author-checked research interface, not a selected-frontier update.
