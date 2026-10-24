# Scope corrections for the affine product cover

This note corrects two statements in `COVERAGE.md`, SHA256
`9f2e1ace092f732b2c839cc03be02ce7c2348bdeda4357b754947531517f9373`.
It preserves the original proof and checker bytes.

In Section 1, criterion (1) has an explicit domain condition:

    X in S_(n,d)
       iff wt(a)=d mod 4, W_0 subset E,
           and q_a vanishes on W_0.

The form `q_a` is defined only on `E`. The checker already tests the
domain condition before it evaluates the form.

In Section 2, the statement about the residues covered by affine
sectors of maximum dimension in unrestricted `S_n` requires `n>=3`.
For these values of `n`, their union is exactly `S_(n,f)` at even
width, and `S_(n,f) union S_(n,f+1)` at odd width. This follows from
the reviewed rigidity theorem and the product-cover result.
The statement is false without the row restriction. At `n=2` and
`lambda=2`, the maximal diagonal affine sector `{(x,x)}` also contains
the nonpreferred residues zero and two.

The pointwise quadratic criterion, the sharp fixed-residue product
cover, and the extension multiplicities remain valid for every
`n>=1`. No physical adaptive-code access or supplier claim is added.

The independent reviewer identified both scope points. No producer
file was changed. No PR, push, or commit was made. Before any eventual
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
