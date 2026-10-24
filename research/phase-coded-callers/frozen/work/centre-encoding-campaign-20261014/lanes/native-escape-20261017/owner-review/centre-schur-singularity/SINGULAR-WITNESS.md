# A singular actual centre Schur mode at width five

The actual operator `S=B Q_U D` is singular at width five. The character
tuple is `(1,2,3,6,6)`, with each integer written in the first nine
coordinates of its tensor copy. All other character coordinates are
zero. Its eight-by-eight Schur matrix has rank seven and the null vector

```text
v = (0,0,1,0,-1,1,0,1).
```

Appending zero characters preserves the matrix. Thus the full operator
has a nonzero kernel at every width at least five. This is a direct
source witness, rather than an inference from the failure of `I+alpha S`.

## Actual source and phase

Use the pinned source matrix R and phase labels from DATA-PHASES:

```text
A = [0,7,20,27,36,46,57,111],
U = {0,...,111} minus A,
B = R_A^T R_U/4,       D=B^T,       BD=13I.
```

In a completed chart, the intrinsic line Q_p has eigenvalue
`i^(sum_j parity(q_p.chi_j))` at a tensor character tuple. This is the
same phase convention as the pinned minor service and Schur probe.
Those packets bind the actual line recipes and completed physical views.

Write q_k for bit k of a label q. The five characters give

```text
parity(q.1) + parity(q.2) + parity(q.3) + 2 parity(q.6)
    = 2(q0*q1 + q0 + q2) modulo 4.
```

The checker verifies this identity for all 512 nine-bit labels. It also
follows by expanding each parity modulo four. The phase is real:

```text
i^(sum_j parity(q.chi_j)) = (-1)^(q0*q1+q0+q2).
```

The source columns give 54 positive and 50 negative phases. No random
matrix or reconstructed root model is substituted for the actual graph.

## Exact matrix and null vector

The checker rebuilds the following matrix directly from all 104 source
columns and their exact Gaussian phases:

```text
          [ 1 -1 -4  7 -4  0 -5  0 ]
          [-1  5  0 -5 -4 -4  3  0 ]
          [-4  0 -3  4 -1  3  0 -1 ]
2 S   =   [ 7 -5  4  1  0 -4 -5  0 ]
          [-4 -4 -1  0  1  3  0 -1 ]
          [ 0 -4  3 -4  3  1  0 -1 ]
          [-5  3  0 -5  0  0  1  0 ]
          [ 0  0 -1  0 -1 -1  0  1 ].
```

Direct multiplication gives `S v=0`. The leading seven-by-seven minor
of S has determinant `-73`. Therefore S has rank exactly seven. The
ordinary source mode is also nonzero: `||D v||^2=52`, and Dv has 49
nonzero coordinates. The null vector does not come from discarding a
zero source mode.

Tensor the displayed centre vector with the stated spatial character.
This gives a nonzero vector in the kernel of the full operator. A zero
character in an added copy contributes no line phase, which proves the
same failure at every width at least five.

## Check and scope

Run with one process:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/native-escape-20261017/owner-review/centre-schur-singularity/check_singular_witness.py
```

The first line is `PASS_DIRECT_SOURCE_SCHUR_SINGULAR_WITNESS`.

The checker uses exact integer and rational arithmetic. It checks the
five retained source byte hashes, all 512 label phases, the direct
Gaussian sum, every null-vector coordinate, the exact minor determinant,
and the nonzero ordinary mode. No floating-point tolerance is used.
Normal Python and Python with `-O` produced byte-identical receipts.

The receipt is independent of the exploratory search scripts. The
search first found the quadratic form `q0*q1+q0+q2`; the five-character
identity above is the certificate used here.

This witness prevents an inverse of S on arbitrary centre inputs at
widths at least five. It does not rule out a larger joint invertible
unit, an additive shear, a restricted-input inverse, or a service that
retains the missing information elsewhere. The separate translation
operator `B Q_U^2 D` remains invertible as proved in its frozen packet.

No minimum singular width is claimed. The bounded width-two and
width-three results belong to a separate supplement. No native lower
bound, complete controller, supplier admission, or kappa improvement is
claimed. No PR, push, or commit was made. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
